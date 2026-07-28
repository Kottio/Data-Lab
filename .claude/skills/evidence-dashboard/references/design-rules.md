# Design rules — what makes a dashboard readable

A dashboard is a **decision surface**, not a report. The test is not "is
everything true?" — it is "can someone tell how the business is doing in five
seconds, and does the page tell them what to do next?"

Comprehensiveness is the failure mode here, not the goal. Everything you cut
still exists — it lives one click away.

## The budget

| Page | Job | Budget |
|---|---|---|
| `index.md` | State of the business, at a glance | **≤5 KPIs · ≤3 charts · 0 tables** |
| a drill-down | **one** question, properly | 1 chart + 1 table + the caveats |

If a number does not change what someone would do this week, it is not a KPI.
If a chart needs a paragraph to be understood, it is the wrong chart.

## Layout: rows, not a column

A page that reads as one long scroll has failed even if every chart on it is right.
Compose in **rows of two or three**, with `full_width: true` in the frontmatter:

| Row | Contents |
|---|---|
| 1 | the KPI row — `<Grid cols=5 gapSize=sm>` of `<BigValue>` |
| 2 | one sentence of reading |
| 3 | `<Grid cols=2>` — the two charts that matter |
| 4 | links to the drill-downs |
| 5 | `<Details>` — caveats, and any table |

Tables live inside `<Details>` even on drill-down pages: available on demand,
never competing with the charts for the first look.

Chart titles and captions ride on the component (`title=`, `subtitle=`), not as
markdown headings — markdown inside a `<Grid>` is not reliably rendered, and a
heading per chart re-introduces the long-scroll feel.

Evidence gives no free-form canvas. If a request needs placed tiles, say so plainly
rather than fighting the framework.

## Pick the form before the colour

| The data's job | Form | Not |
|---|---|---|
| A single current value (+ trend) | stat tile (`<BigValue>` + sparkline) | a one-bar bar chart |
| A handful of headline numbers | a KPI row (`<Grid>` of `<BigValue>`) | a grouped bar chart |
| Compare magnitude across categories | bar | pie |
| Trend over time | line (area for a single series) | bar, unless gaps matter |
| Weeks with missing periods | **bar** (absence is visible) | line (it interpolates a lie) |
| Tell distinct series apart | grouped/stacked bar, multi-line | more colours than series |
| One series is the point, rest are context | **emphasis** — colour it, gray the others | categorical palette |
| Ordered stages, each a subset | funnel (or horizontal bar, `sort=false`) | a line |
| Part-to-whole | stacked bar (horizontal if names are long) | pie |
| >7 meaningful classes | a table, on a drill-down page | more colours |

**Emphasis is the most underused form.** When the story is "this one source is
doing the work," that is one accent hue plus gray — not a rainbow.

## Series-count ladder

| Series | Treatment |
|---|---|
| 1–3 | comfortable; direct-label |
| 4 | direct labels become **mandatory** |
| 5–6 | soft cap — legend or small multiples |
| 7–8 | ceiling — past it, fold the tail into "Other" or facet |

Never solve "too many series" by generating another hue. A 9th hue is
indistinguishable from an existing one under colour-vision deficiency.

## Colour: the non-negotiables

- **Never a dual axis** (`y2`). Two scales on one chart is the #1 chart lie.
- **Colour follows the entity, never its rank.** `tik_tok` is the same colour on
  every chart and every page, whether it is first or last.
- **Sequential = one hue, light→dark. Diverging = two opposite hues + a neutral
  gray midpoint.** Never a rainbow; never a hue at the midpoint.
- **Text wears text colours**, never the series colour. A coloured mark beside
  the label carries the identity.
- **Status colours are reserved** (good / warning / critical) and never reused as
  "series 4".
- **Don't eyeball a palette — measure it.** The dataviz skill ships
  `scripts/validate_palette.js`; run it on any palette before committing it.

### The validated palette for this repo

The palette originally shipped in `dashboard/evidence.config.yaml` **failed** four of
the five checks (lightness band, chroma floor, CVD ΔE 4.6 on the worst adjacent pair,
normal-vision ΔE 7.3 — under the hard floor of 15). It was replaced on 28/07 with this
one, which passes in both modes. Do not change it without re-running the validator:

```yaml
theme:
  colorPalettes:
    default:
      light:
        - "#2a78d6"
        - "#008300"
        - "#e87ba4"
        - "#eda100"
        - "#1baf7a"
        - "#eb6834"
        - "#4a3aa7"
        - "#e34948"
      dark:
        - "#3987e5"
        - "#008300"
        - "#d55181"
        - "#c98500"
        - "#199e70"
        - "#d95926"
        - "#9085e9"
        - "#e66767"
```

Installed 28/07. Note the nesting: palettes live under `theme:`, and light and dark
are **separate lists** — dark is not an automatic flip of light, it is its own set of
steps validated against the dark surface.

## Anti-patterns — if the page does any of these, it is wrong

- A KPI row of numbers with no comparison — a number with no baseline is trivia.
- A chart per mart column, because the column exists.
- A table on `index.md`.
- A line chart over weeks where some weeks have no rows (it interpolates).
- Rates shown without their denominator when n is small.
- Two different week grains (cohort week, payment week) on one axis.
- Caveats written as a paragraph nobody reads instead of a `<Details>`.
- A page that answers six questions equally instead of one question first.
- Colour used decoratively — every hue on screen should mean something.
- A markdown `##` heading above every chart — that is what turns a dashboard into a
  scrolling document. The heading belongs in the chart's `title` prop.
- Restructuring a page to hide the `sql` blocks — that is a viewer toggle, not layout.

## Captions

Every chart carries **one line of "so what"** under its title — the reading, not
the description. "Signups are flat while visits doubled: the landing page is the
bottleneck" beats "Signups by week and source."

If you cannot write that line, the chart is not earning its place.
