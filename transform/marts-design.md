# Marts design — questions → funnel → model

> **The method:** `question → process → grain → fact + dims → (optionally) aggregate mart`
> Questions decompose as **measure BY context** — facts are verbs, dims are nouns.
> Grain = a written sentence = the mart's `unique` test. Every analytics bug is eventually a grain bug.
> **The consumer test:** a model exists only if something reads it. (Full theory: [README.md](README.md))

## THE QUESTIONS — the core six (frozen 27/07)

*Test each passed: "would this number change what I do next week?"*

1. **How many new users, weekly?** — the pulse
2. **Visit → signup rate, by source** — is TikTok/bridge working?
3. **% of new users active within 7 days** — does onboarding work?
4. **How many engaged free users convert — and how many never do?** — the crown 👑
5. **Engaged free users: average activity** — how alive is the free tier?
6. **Revenue, weekly** — the scoreboard

**Definitions ✎:** conversion = a row in `payment` · source: `bridge_*` events → `tik_tok`, else `other` ·
**activated = viewed ≥1 lesson** (`progress`); activation moment = first lesson access; never-activated = `lessons_viewed = 0` ·
**"engaged" — the distribution, read 28/07** (97 students):

| lessons viewed | students | of which PAID |
|---|---|---|
| 0 | 43 | 1 |
| 1–2 | 20 | 1 |
| 3–5 | 19 | 1 |
| 6 | 10 | 0 |
| 7+ | 5 | **5** |

The free module is 6 lessons — the plateau at 6 is the ceiling of the free tier, and the whole
7+ bucket is paid students reading paid content. So **engaged = viewed ≥ 3 of the 6 free lessons**
(half the free module): 29 students, a real cohort, entirely inside the free tier.
Anything above 6 is not a driver of conversion — it *is* conversion.

## Drill-downs (off-dashboard, opened when a core number looks wrong)

Never-activated: how many & why (by source/cohort) · actives & events-per-active by plan ·
module-1 completion 14d (`progress`) · median time signup → first dashboard · revenue by cohort

## THE MODEL — as built (9, zero orphans)

```
raw (dlt: students, event, progress, enrollments, payments)
 └─ staging   stg_students · stg_events (student_id→user_id) · stg_progress
              stg_enrollments · stg_payments                     [views, 1:1]
 └─ int       int_sessions        grain: session (browser identity)
              — signup anchor, first_seen, signed_up, from_bridge
              — foundation of all traffic/cohort numbers (unique test = session_id)
 └─ marts     dim_student         grain: student — attributes only
              — access_type (1:1 enrollment, single course), acquisition_source
                (retroactive stitching via persistent sessionId, as internal CTE)
              mart_kpis_weekly    grain: cohort_week × source → Q1, Q2
              mart_conversion_drivers  grain: student — features + is_activated + converted → Q3, Q4 👑, Q5
              mart_revenue_weekly grain: payment_week → Q6
              — payment week ≠ cohort week: revenue in mart_kpis_weekly would break its grain.
                Built 28/07 because Evidence reads it (consumer test passed).
              [tables, marts schema]
```

## Deferred until a consumer exists (the over-modeling lesson, 28/07)

`fct_events`, `fct_progress`, `fct_payments`, `dim_date`, `int_session_student_map` were built
and **cut** — zero consumers. They return the day Evidence/the MCP door actually reads
event-grain or needs a date spine — built then, as a documented step, not as shelf-ware.

## Data honesty notes

- `session_id` = persistent **browser identity** (localStorage, no expiry) — not a visit.
  "New visitors" = first-seen cohort; weekly *traffic* would count browsers per week.
- `progress` is a **state** table (first/last touch only — revisits overwritten at source).
  True lesson-view actions need an app-side `lesson_view` event (instrumentation backlog).
- ⚠️ **Outcome leakage in `lessons_viewed`:** it counts lessons viewed at *any* time, including
  after payment. Every 7+ student is PAID — so the column cannot be used to predict conversion.
  Fix when Q4 goes from describing to explaining: `lessons_before_payment` = distinct lessons with
  `created_at < coalesce(first_payment_at, '9999-12-31')`.
- ⚠️ **`access_type` is current state, not state-at-the-time.** A student who converts flips to PAID,
  so "engaged FREE students who converted" is 0 by construction. Cohort on signup, not on access_type.
- ⚠️ **8 students are PAID, 7 have a payment row.** One comped/manual access (13 lessons, €0).
  Expected, but it means `access_type = 'PAID'` ≠ `converted`. `converted` is the money truth.
- ⚠️ **PII hole open:** emails inside `event.properties` JSON (`lead_email_captured`, signup).
  Patch the events `add_map` (hash/drop keys) + rebuild ritual — **before Evidence ships.**

## Next

1. PII patch + rebuild — **before the dashboard is public**
2. ✅ Evidence dashboard on the marts (Phase 6) — the core six on one page; both ✎ definitions
   settled from the distributions on screen
3. `lessons_before_payment` when Q4 must explain, not describe
4. Dagster (Phase 4) → CI → droplet
