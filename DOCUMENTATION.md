# Chart Implementation Plan for `index.html`

## Quick run instructions

From the repository root, start a local web server:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/index.html
```

---

Below is the **best low-friction approach** to render charts directly in your current `index.html` using the CSV files in `analysis/exports/CSVs/`.

## Why this approach

- **No build step required**: everything runs in a single HTML file.
- **Simple CSV loading**: use `PapaParse` to fetch + parse CSV files.
- **Reliable charting**: use `Chart.js` for line/bar charts with good defaults.
- **Scalable**: you can add new charts by only appending to one config array.

---

## Recommended architecture (inside `index.html`)

1. Keep your theme UI as-is.
2. Add a `dashboard` section with chart containers.
3. Add CDN scripts for:
   - `papaparse`
   - `chart.js`
4. Add a `CHART_CONFIGS` array that maps:
   - CSV file path
   - chart title
   - chart type
   - x/y columns
5. Loop through configs, fetch each CSV, parse rows, render chart.
6. Show a readable inline error if one CSV fails.

---

## Important browser note (file access)

If you open `index.html` directly with `file://`, many browsers block local CSV fetches.

Use a local server from the repo root, for example:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/index.html
```

---

## Drop-in example to integrate

Use this pattern directly in your existing file.

### 1) Add this dashboard markup in `<main>`

```html
<section id="dashboard" aria-label="Business charts">
  <h2>Analytics Dashboard</h2>
  <div id="chartGrid" class="chart-grid"></div>
</section>
```

### 2) Add supporting CSS

```css
#dashboard {
  margin-top: 1.5rem;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-top: 0.75rem;
}

.chart-card {
  background: var(--surface);
  border: 1px solid color-mix(in srgb, var(--primary) 22%, transparent);
  border-radius: 12px;
  padding: 0.75rem;
}

.chart-title {
  margin: 0 0 0.5rem;
  font-size: 0.95rem;
  color: var(--muted);
}

.chart-error {
  color: #c0392b;
  font-size: 0.9rem;
}
```

### 3) Add these CDN scripts before your main `<script>`

```html
<script src="https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
```

### 4) Extend your script with a chart renderer

```html
<script>
  const CHART_CONFIGS = [
    {
      id: 'revenueOverTime',
      title: 'Revenue Over Time',
      csvPath: 'analysis/exports/CSVs/01_01_revenue_over_time.csv',
      type: 'line',
      xKey: 'order_date',
      yKey: 'revenue'
    },
    {
      id: 'ordersOverTime',
      title: 'Orders Over Time',
      csvPath: 'analysis/exports/CSVs/01_02_orders_over_time.csv',
      type: 'bar',
      xKey: 'order_date',
      yKey: 'orders'
    }
    // Add the rest of your CSV files the same way.
  ];

  async function loadCsvRows(csvPath) {
    const response = await fetch(csvPath);
    if (!response.ok) {
      throw new Error(`Failed to load ${csvPath}: ${response.status}`);
    }

    const csvText = await response.text();
    const parsed = Papa.parse(csvText, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true
    });

    if (parsed.errors?.length) {
      throw new Error(parsed.errors[0].message);
    }

    return parsed.data;
  }

  function createChartCard(container, { id, title }) {
    const card = document.createElement('article');
    card.className = 'chart-card';

    const h3 = document.createElement('h3');
    h3.className = 'chart-title';
    h3.textContent = title;

    const canvas = document.createElement('canvas');
    canvas.id = `chart-${id}`;

    card.append(h3, canvas);
    container.appendChild(card);
    return canvas;
  }

  function renderErrorCard(container, title, message) {
    const card = document.createElement('article');
    card.className = 'chart-card';
    card.innerHTML = `
      <h3 class="chart-title">${title}</h3>
      <p class="chart-error">${message}</p>
    `;
    container.appendChild(card);
  }

  async function renderDashboard() {
    const grid = document.getElementById('chartGrid');

    for (const config of CHART_CONFIGS) {
      try {
        const rows = await loadCsvRows(config.csvPath);
        const labels = rows.map((r) => r[config.xKey]);
        const values = rows.map((r) => r[config.yKey]);

        const canvas = createChartCard(grid, config);

        new Chart(canvas.getContext('2d'), {
          type: config.type,
          data: {
            labels,
            datasets: [
              {
                label: config.title,
                data: values,
                borderColor: '#1769ff',
                backgroundColor: 'rgba(23, 105, 255, 0.25)',
                fill: config.type === 'line',
                tension: 0.25
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              x: { ticks: { maxRotation: 45, minRotation: 0 } },
              y: { beginAtZero: true }
            }
          }
        });
      } catch (error) {
        renderErrorCard(grid, config.title, `Could not render chart: ${error.message}`);
      }
    }
  }

  renderDashboard();
</script>
```

---

## Suggested next improvement (optional)

When you add all CSVs, create a small **column mapping helper** to normalize field names (`date`, `revenue`, `orders`, etc.), since each CSV may use slightly different headers.

This keeps your chart loop clean and prevents brittle hardcoded assumptions.
