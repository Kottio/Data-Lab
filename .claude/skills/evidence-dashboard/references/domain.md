# Domain contract — what the numbers mean

Source of truth: `transform/marts-design.md`. This file is the dashboard-facing
summary; if the two disagree, marts-design.md wins and this file is stale.

## The business in one paragraph

One online course. Visitors arrive (some through the LinkedIn/TikTok *bridge*, the rest
from YouTube and elsewhere), a few sign up for free access, some of those open a lesson,
and a very few pay. The funnel is wide at the top and needle-thin at the bottom: today
**683 visitors → 97 signups → 54 activated → 7 paying**. Any dashboard that does not make
that shape obvious has missed the point.

## The frozen questions (27/07)

Test each passed: *"would this number change what I do next week?"*

1. **How many new users, weekly?** — the pulse
2. **Visit → signup rate, by source** — is the bridge working?
3. **% of new users active within 7 days** — does onboarding work?
4. **How many engaged free users convert — and how many never do?** — the crown 👑
5. **Engaged free users: average activity** — how alive is the free tier?
6. **Revenue, weekly** — the scoreboard

Q4 is the one that pays the bills. It leads the page. Q1/Q2 are traffic hygiene; they
belong on the home page only as a small trend, or on a drill-down.

## Definitions (settled — do not redefine in a page)

| Term | Definition |
|---|---|
| visitor | one persistent **browser identity** (`session_id`, localStorage, no expiry) — *not* a visit |
| signup | a row in `students` |
| source | `bridge_*` events in the session → `tik_tok`, otherwise `other`, `unknown` if unstitched |
| **activated** | viewed ≥1 lesson (`progress`); the moment is `first_lesson_at` |
| never-activated | `lessons_viewed = 0` |
| **engaged** | viewed **≥3 of the 6 free lessons** (settled 28/07 from the distribution) |
| **converted** | has a row in `payment`. This is the money truth, not `access_type` |
| revenue | `sum(amount)/100` — assumed minor units (cents); **unconfirmed** |

## The published tables (what a page may read)

`just publish` copies these three marts into `dashboard/sources/lake/dashboard.duckdb`.
Evidence sees them through the source queries in `dashboard/sources/lake/*.sql`, so a
page refers to them as `lake.kpis`, `lake.drivers`, `lake.revenue`.

### `lake.kpis` ← mart_kpis_weekly — grain: **cohort_week × source**
`cohort_week` (ts, week of first sight) · `source` (tik_tok|other) · `new_visitors` ·
`signups` · `signup_rate_pct` (0–100 — divide by 100 before using `pct` formats)

### `lake.drivers` ← mart_conversion_drivers — grain: **one student**
`student_id` · `user_id` · `signed_up_at` · `access_type` (FREE|PAID) ·
`acquisition_source` (tik_tok|other|unknown) · `dash_access` (dashboard visits) ·
`lessons_viewed` · `first_lesson_at` · `is_activated` · `activated_within_7d` ·
`converted` · `first_payment_at` · `total_paid` (cents)

### `lake.revenue` ← mart_revenue_weekly — grain: **one payment week**
`payment_week` · `payments` · `paying_students` · `revenue` (already euros)

Weeks with no payment are **absent** — there is no date spine. A line chart will
connect across the gap; a bar chart will simply not draw them. Prefer bars.

## The traps — read before writing any query

1. **Outcome leakage.** `lessons_viewed` counts lessons at *any* time, including after
   payment. The entire 7+ bucket is PAID students reading paid content. It cannot be
   used as a predictor of conversion. Free-tier depth is 0–6; anything above is the
   consequence, not the cause. (Fix pending: `lessons_before_payment`.)
2. **`access_type` is current state, not state-at-the-time.** A converting student flips
   to PAID, so "engaged FREE students who converted" is 0 by construction. **Cohort on
   `signed_up_at`, never on `access_type`.**
3. **8 are PAID, 7 have a payment row.** One comped access. Use `converted` for money,
   `access_type` only for "what can this person see today".
4. **`progress` is a state table** — first and last touch, revisits overwritten at source.
   It is not an event stream. "Lessons viewed" is really "lessons ever opened".
5. **Cohort week ≠ payment week ≠ signup week.** `lake.kpis` cohorts on first sight,
   `lake.drivers` on signup, `lake.revenue` on payment. Never plot two of them on one axis.
6. **n is tiny.** 7 conversions. Rates on weekly slices swing wildly on one student —
   show counts next to any rate, and never draw a trendline through this.
7. **PII:** emails still leak into `event.properties` upstream (patch pending). Nothing
   in the marts exposes them, but do not add a page that reads raw events until it lands.

## Not answerable yet (say so, don't approximate)

- Why a student converts — needs `lessons_before_payment` and more than 7 payers
- Repeat/returning traffic — `session_id` never expires
- True lesson views over time — needs an app-side `lesson_view` event
- Anything YouTube-side — no channel data in the lake yet
