# Evidence syntax — verified, not remembered

Everything here was checked against docs.evidence.dev or against this repo.
If something you need is **not** in this file, do not guess a prop name:
say so, check the docs, then add it here.

## The page

A page is a markdown file under `dashboard/pages/`.
`index.md` is `/`; `pages/growth.md` is `/growth`.
Front matter is optional; `title:` sets the page heading.

## Page frontmatter and layout

```yaml
---
title: KottioDev
full_width: true      # break the ~1280px default column
max_width: 1600       # or pin it to a number of pixels
---
```

**Evidence is a document, not a canvas.** There is no absolute positioning and no
drag-and-drop. Side-by-side comes from one component:

```
<Grid cols=3 gapSize=sm>   <!-- cols 1–6, default 2; gapSize none|sm|md|lg -->
  <BigValue .../>
  <BarChart .../>
</Grid>
```

On small screens Grid stacks automatically. `<Group>` puts several items inside a
**single** grid cell.

**Put titles and captions on the component, not around it.** Markdown headings and
paragraphs written *inside* a `<Grid>` or `<Group>` are not reliably processed —
every chart takes `title` and `subtitle` props, and `<DataTable>` takes `title` too.
Use those; keep markdown prose between grids, never inside one.

## Hiding the SQL blocks

Query blocks are shown by default **in dev only**:

```js
// @evidence-dev/component-utilities/src/stores.js
export const showQueries = localStorageStore('showQueries', dev && browser);
```

Toggle it per-browser from the ⋮ kebab menu in the header ("Hide Queries") — it
persists in localStorage. A production build has them off by default; a visitor can
still turn them on unless the layout is ejected and given `neverShowQueries`.
This is a **viewer setting, not a page problem** — never restructure a page to hide
queries.

## Queries

A query is a fenced block with a name:

````
```sql weekly
select * from lake.kpis order by cohort_week
```
````

- The name is how components reference it: `data={weekly}`.
- **Source refs are `source.query`** — in this repo the source is `lake`
  (`dashboard/sources/lake/`), and each `.sql` file there is a query:
  `lake.kpis`, `lake.drivers`, `lake.revenue`.
- **Chain queries with `${query_name}`**:
  `select * from ${weekly} where source = 'tik_tok'`.
  Some dialects need an alias: `from ${weekly} w`.
- Order of blocks on the page does not matter — chains resolve.
- Inline a scalar in prose with `{weekly[0].signups}`.

## Inputs and params

- `<Dropdown name=src .../>` → read as `${inputs.src.value}`.
- URL params on a drill-down page → `${params.source}`
  (file `pages/source/[source].md` gives `params.source`).

## Component inventory (verified to exist)

**Data** — `<Value>`, `<BigValue>`, `<DataTable>` (+ `<Column>`)
**Charts** — `<LineChart>`, `<AreaChart>`, `<BarChart>`, `<ScatterPlot>`,
`<BubbleChart>`, `<FunnelChart>`, `<SankeyDiagram>`, `<Heatmap>`,
`<CalendarHeatmap>`, `<Histogram>`, `<BoxPlot>`, `<ReferenceLine>`,
`<ReferenceArea>`, `<CustomECharts>`
**Inputs** — `<ButtonGroup>`, `<Dropdown>`, `<TextInput>`, `<DateRange>`, `<DimensionGrid>`
**UI** — `<Accordion>`, `<Alert>`, `<Details>`, `<Grid>`, `<Modal>`, `<Tabs>`
**Maps** — `<AreaMap>`, `<PointMap>`, `<BubbleMap>`, `<BaseMap>`, `<USMap>`

Anything not on this list: check before using.

## The props that actually get used here

### `<BigValue>` (the KPI tile)
`data` `value` `title` `fmt` `link` `description`
`comparison` `comparisonTitle` `comparisonDelta` `comparisonFmt` `downIsGood`
`neutralMin` `neutralMax`
`sparkline` `sparklineType` `sparklineValueFmt` `sparklineDateFmt`
`sparklineColor` `sparklineYScale`
`minWidth` `maxWidth` `emptySet` `emptyMessage` `connectGroup`

`data` must be a **single-row** query (or it silently shows row 0).

```
<BigValue data={totals} value=paying title="Paying students" fmt=num0/>
```

### `<BarChart>` / `<LineChart>` / `<AreaChart>`
`data` `x` `y` `y2` `series` `sort` (default true) `type` (stacked|grouped|stacked100)
`xFmt` `yFmt` `y2Fmt` `colorPalette` `seriesColors` `fillColor` `outlineColor`
`fillOpacity` `swapXY` `xAxisTitle` `yAxisTitle` `yGridlines` `yBaseline`
`yTickMarks` `yMin` `yMax` `title` `subtitle` `legend`
`chartAreaHeight` (default 180) `labels` (default false) `labelPosition`
`downloadableData` `downloadableImage`
`<LineChart>` also takes `markers`.

**`sort` is on by default** — for an ordered category (funnel stages, week
buckets) set `sort=false` and impose the order in SQL.

**`y2` exists. Do not use it.** A second y-scale is the single most common
chart lie; two measures → two charts or index both to a base.

### `<DataTable>`
`data` `rows` `title` `search` `sortable` `link` `rowShading` `totalRow` `groupBy`
`<Column>` takes `id` `fmt` `title` `align` `contentType`.
Only on drill-down pages, and inside `<Details>` — never on `index.md`.

### `<Grid>`
`<Grid cols=3>` … `</Grid>` — lays components side by side. Use for the KPI row.

### `<Details title="...">`
Collapsible. Where every caveat goes, so the screen stays clean and the
honesty stays available.

### `<Alert status=warning>`
For a caveat the reader must not miss (e.g. "n = 7; treat rates as directional").

## Formatting

- Built-in tags: `pct0` `pct1` `num0` `num1` `usd` `eur` `mmm d` `yyyy-mm-dd`.
- Excel-style custom codes work anywhere a `fmt` is accepted:
  `fmt='€#,##0'`, `fmt='$#,##0.0'`, `fmt='#,##0.0%'`.
- **Percent formats expect a fraction.** `signup_rate_pct` is already ×100 in
  the mart — divide by 100 in the query before using `pct1`.

## Links and drill-downs

- Markdown link: `[Growth detail](/growth)`.
- On a tile: `<BigValue ... link='/growth'/>`.
- Table row link: a column containing a path + `link=` on `<DataTable>`.
- Dynamic page: `pages/source/[source].md`, read `${params.source}`.

## The publish workflow (this repo)

Evidence's DuckDB connector autoloads only **default** DuckDB extensions.
`ducklake` is not one of them, so Evidence **cannot ATTACH the lake**.
`infra/publish.sh` copies the marts into a plain
`dashboard/sources/lake/dashboard.duckdb` — the shop window.

Consequence to own on the page: **the dashboard reads a snapshot.**

Run order (Tom runs these, not the AI):

```
just transform    # dbt builds the marts in the lake
just publish      # copy marts -> dashboard.duckdb
just dashboard    # evidence dev server
```

`just lakehouse` must be **closed first** — DuckDB takes a file lock and
`publish` will fail while a session is open.

To check a query before putting it on a page:

```
duckdb dashboard/sources/lake/dashboard.duckdb -c "<your sql>"
```

Table names inside that file are the mart names
(`mart_kpis_weekly`, `mart_conversion_drivers`, `mart_revenue_weekly`);
`lake.kpis` / `lake.drivers` / `lake.revenue` are the Evidence-side names
defined by the `.sql` files in `dashboard/sources/lake/`.

## Config

`dashboard/evidence.config.yaml` holds `colorPalettes.default` (categorical,
light + dark), `colorScales`, and semantic colors. Change colours **there**,
never per-chart with `seriesColors`, unless one chart genuinely needs emphasis.
