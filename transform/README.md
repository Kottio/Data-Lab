# transform/ — dbt (Fusion) on the lake

Profile lives at the **repo root** (`profiles.yml`, cwd rule) — run everything from the root via `just`.

## Layers

```
staging/       stg_*   1:1 sources — rename/cast only.        VIEWS.  Not for consumers.
intermediate/  int_*   reusable assembly steps.               VIEWS.  Not for consumers.
marts/         fct_* dim_*  the product — documented, tested. TABLES. (+schema: marts)
```

Rule of thumb: staging **renames**, intermediate **assembles**, marts **present**.
Views live in the catalog (no Parquet); tables write Parquet into `lake_files/`.

Design doc: [marts-design.md](marts-design.md)

## Dimensional modeling — the theory in one page

**The flow (Kimball, distilled):**
`question → process → grain → fact + dims → (optionally) aggregate mart`

- Every business question decomposes as **measure BY context**:
  "lessons viewed **by** free users" = count of events (fact) *by* plan (dim).
- **Facts are verbs** — things that happened, measured at a declared grain
  (one process per fact; fidelity over convenience).
- **Dims are nouns** — who/what/when/where, the axes you slice by
  (designed for reuse: `dim_student` joins every fact ever built).
- **Grain is a written sentence** ("one row per student × event") and becomes the
  mart's `unique` test. *Every analytics bug is eventually a grain bug.*
- **Aggregate marts** pre-answer frequent questions (dashboard/MCP feeds):
  derived, disposable, rebuilt at will — never the source of truth.

One-line summary: *questions decompose into measures-by-context; processes become facts
at a declared grain; contexts become reusable dims; frequent questions get pre-answered in marts.*

## Design before code

1. Write the business questions the warehouse must answer.
2. Per question: which **process** (→ a fact) and which **grain** (one row per *what*?).
3. The grain is a written sentence at the top of every mart — and becomes its `unique` test.
   *Every analytics bug is eventually a grain bug.*

## The iteration loop

1. **Sketch** in the REPL: `just lakehouse` (or `duckdb -ui` for the browser UI) — iterate SQL against `stg_*` live.
2. **Freeze** into a model file; replace table names with `{{ ref('...') }}` / `{{ source('...') }}`.
3. **Build the branch, not the project**: `dbt build -s int_x` · `-s +fct_y` (it + upstream) · `-s stg_x+` (it + downstream). Fast loop > full run.
4. **`dbt build`, never bare `run`** — runs *and tests* in DAG order.
5. **Test at birth**: every mart gets `unique` + `not_null` on its grain key the day it's created.
6. **Spot-check like an analyst**: reconcile counts vs raw, trace one known row through.

Rhythm: *questions → grains → sketch → model → build -s → test → spot-check → PR.*


## Processes hiding in them → the facts

| Process observed                              | Fact                  | Grain (one row per…)                | Feeds questions  |
| --------------------------------------------- | --------------------- | ----------------------------------- | ---------------- |
| A student does something (view, click, visit) | `fct_activity`        | **student × event** (event id)      | 2, 4, 5, 6, 7, 8 |
| A student progresses in content               | `fct_progress`        | **student × lesson** (latest state) | 3, 8             |
| A student changes plan (free→paid)            | `fct_plan_changes` ❓ | **student × change event**          | 1                |
