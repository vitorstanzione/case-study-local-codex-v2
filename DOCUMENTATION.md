# Dashboard Setup & Chart Extension Guide

This document explains only what you need to:
1. run the dashboard locally, and
2. add or update charts safely.

It intentionally excludes one-off implementation history.

---

## 1) Local setup (required)

From repo root:

```bash
python -m http.server 8000
```

Open:

```text
http://localhost:8000/index.html
```

### Why this is required
The page loads CSV files via `fetch(...)`. Opening `index.html` with `file://` will fail in most browsers because local file requests are blocked.

---

## 2) Data and chart file locations

- **Main page**: `index.html`
- **Query exports consumed by charts**: `analysis/exports/CSVs/`
- **Python chart scripts (if regenerating assets/data)**: `analysis/py/`
- **Generated static chart images (if used by page)**: `visualizations/`

When adding a chart, first decide whether the page should render it:
- dynamically from CSV in browser, or
- as a pre-generated static image.

Keep that choice consistent for the new chart.

---

## 3) Standard workflow to add a new chart

1. **Create/confirm the dataset**
   - Add or update the SQL/Python logic that produces the chart dataset.
   - Ensure the corresponding CSV is present in `analysis/exports/CSVs/` with stable column names.

2. **Register the chart in `index.html`**
   - Add one new chart entry in the page chart config (id, title, source path, x/y fields, chart type).
   - Reuse existing patterns for styling/colors/axis options.

3. **Validate in browser**
   - Start local server.
   - Hard refresh page.
   - Confirm the chart renders and no console/network errors appear.

4. **Basic data sanity checks**
   - Confirm row count is non-zero.
   - Confirm x-axis field is ordered as expected (especially dates).
   - Confirm numeric field is parsed as number (not string).

---

## 4) Chart config checklist (before committing)

For every new chart entry in `index.html`, verify:

- unique chart `id`
- human-readable `title`
- correct relative CSV path
- correct `x` and `y` column names (exact match with CSV header)
- suitable chart `type` for the metric
- axis/label formatting is readable on narrow screens

If any of these are wrong, the chart may silently render empty or with misleading values.

---

## 5) CSV contract for frontend compatibility

To reduce breakage, exported CSVs should follow these rules:

- Header row present.
- No duplicate column names.
- Dates in ISO-like format (`YYYY-MM-DD`) when used on x-axis.
- Metric columns contain numeric values only (no currency symbols in raw field).
- Keep naming predictable (example: `order_date`, `revenue`, `orders`, `customers`).

If a query requires display formatting (e.g., `$1,234`), format in tooltip/label logic in frontend, not in raw CSV data.

---

## 6) Troubleshooting

### Chart does not appear
- Check browser DevTools Network tab for 404 on CSV path.
- Verify chart config keys match CSV headers exactly.
- Confirm server is running from repository root.

### Chart appears but looks wrong
- Validate date sorting before rendering.
- Validate numeric parsing for y-values.
- Check for null/empty records in CSV.

### Only some charts render
- Isolate the failing chart config and test its CSV path manually in browser.
- Keep per-chart error handling so one failed chart does not block others.

---

## 7) Definition of done for a new chart

A chart addition is complete when:

- dataset export exists and is stable,
- chart is wired into `index.html`,
- local page renders correctly via `http://localhost:8000/index.html`,
- no fetch/parse errors occur in console,
- chart is readable on desktop and mobile widths.
