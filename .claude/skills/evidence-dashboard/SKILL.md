---
name: evidence-dashboard
description: Build or change an Evidence.dev dashboard page in this repo. Use whenever a page under dashboard/pages/ is created or edited, a chart or KPI is added, a mart needs to be shown on screen, or someone says the dashboard is unclear/too long. Carries this project's question set, mart contracts and data traps, plus verified Evidence syntax and the dashboard design rules.
---

# Building dashboards for DBuilders

A dashboard is not a place to put everything that is true. It is **one screen that
answers "how is the business doing?" in five seconds**, plus drill-downs for when a
number on that screen looks wrong.

Most bad dashboards fail for the same reason: every question got equal weight, so the
reader has to work out which number matters. Deciding what to leave off the home page
is the job.

## The procedure — in order

**1. Load the domain first.** Read `references/domain.md`. It holds the frozen
questions, what every mart column means, and the traps in this data. Never invent a
metric, a column, or a definition — if the number you want isn't in the contract, say
so and propose the model change instead of computing it in the page.

**2. Decide what this page is for.** One page, one job.

| Page | Job | Budget |
|---|---|---|
| `index.md` | State of the business, at a glance | **≤5 KPIs, ≤3 charts, 0 tables** |
| a drill-down page | Explain one number when it looks wrong | 1 question, as deep as needed |

If something doesn't fit the home budget, it does not get squeezed in — it moves to a
drill-down and the home page links to it. A home page that scrolls has failed.

**3. Order by decision value, not by question number.** Top of the page = the number
that would change what Tom does next week. The frozen question list is a *modelling*
order, not a layout order.

**4. Pick the form before the chart.** `references/design-rules.md` → the job→form
table. Single value = a stat tile, never a one-bar chart. Ordered stages = a funnel.
"One series is the point" = emphasis, not eight colours.

**5. Write it.** `references/evidence-syntax.md` — verified props only. If you are
unsure a prop exists, do not guess: check the docs or leave it out.

**6. Caption every chart with its "so what" in one line.** A chart with no sentence
under it makes the reader do the analysis. Caveats go behind `<Details>`, never in the
body — honesty should not cost clarity.

**7. Verify before handing over.** Run every query against the published snapshot:

```bash
duckdb dashboard/sources/lake/dashboard.duckdb -c "<the query, with lake.x -> the table name>"
```

Then `just publish` → `just dashboard`, and *look at the page*. Queries that parse can
still be wrong; charts that render can still be unreadable.

**8. Run the checklist below.** If any line fails, it is not done.

## Definition of done

- [ ] Home page fits one screen: ≤5 KPIs, ≤3 charts, no tables, no scroll
- [ ] The page composes in **rows** (`<Grid>`), not one long column; `full_width: true`
- [ ] Titles and captions ride on `title=`/`subtitle=`, not markdown headings per chart
- [ ] The top number is the one that drives a decision
- [ ] Every chart has a one-line "so what" caption
- [ ] Every query ran clean against the real snapshot, numbers sanity-checked
- [ ] No dual axis (`y2`), no rainbow, no 9th colour, no value-ramp on nominal categories
- [ ] Ordered categories use `sort=false` with the ordering done in SQL
- [ ] Caveats and data-honesty notes are behind `<Details>`, not in the flow
- [ ] Anything cut from the home page lives on a drill-down page that is linked
- [ ] Checked against the anti-pattern list in `references/design-rules.md`

## The house style

- **Numbers over prose.** The page is a set of numbers with sentences attached, not an
  essay with charts.
- **French or English?** Follow the surrounding page. Do not translate what is there.
- **The dashboard is a snapshot** — `just publish` is the refresh. Say so once, in the
  footer, not on every page.
- **Never widen the surface silently.** A new mart or a new column is a modelling
  decision: propose it, with the grain written as a sentence, before building it.
