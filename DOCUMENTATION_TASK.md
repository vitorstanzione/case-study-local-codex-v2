# Task: Create Documentation for CSV Charting in `index.html`

## Objective
Create a documentation file that explains the recommended approach to implement charts directly in `index.html` using CSV files from `analysis/exports/CSVs/`.

## Scope
- Document how to:
  - load CSV files in-browser,
  - parse CSV content,
  - render charts,
  - and run the page through a local server.

## Required Contents
1. **Overview**
   - Goal of plotting CSV exports in the browser.
2. **Dependencies**
   - `Chart.js` (CDN)
   - `Papa Parse` (CDN)
3. **Implementation Steps**
   - Add chart `<canvas>` elements.
   - Add `loadCSV()` helper using `fetch()`.
   - Parse with Papa Parse (`header: true`, `dynamicTyping: true`, `skipEmptyLines: true`).
   - Create reusable chart renderer (e.g., line chart).
   - Initialize charts via `initCharts()`.
4. **Runtime Requirement**
   - Explain why `file://` usually fails for `fetch()`.
   - Provide local server command:
     - `python -m http.server 8000`
5. **Error Handling**
   - Show how to catch initialization failures and display a user-facing message.
6. **Example Snippet**
   - Include a small copy-paste example with one or two CSV-based charts.

## Deliverable
- A new markdown documentation file (recommended name: `docs/csv-charting-guide.md`) containing the above sections.

## Acceptance Criteria
- Documentation is actionable and copy-paste friendly.
- Paths use forward slashes (`analysis/exports/CSVs/...`).
- Includes at least one working chart example.
- Clearly states the local server requirement.
