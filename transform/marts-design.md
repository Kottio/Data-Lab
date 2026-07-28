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
"engaged" = **TBD** (pick the threshold from the real distribution in `mart_conversion_drivers`)

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
              mart_kpis_weekly    grain: week × source → Q1, Q2 (Q6 revenue col to add)
              mart_conversion_drivers  grain: student — features + is_activated + converted → Q3, Q4 👑, Q5*
              [tables, marts schema]                     *Q5 pending the "engaged" threshold
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
- ⚠️ **PII hole open:** emails inside `event.properties` JSON (`lead_email_captured`, signup).
  Patch the events `add_map` (hash/drop keys) + rebuild ritual — **before Evidence ships.**

## Next

1. PII patch + rebuild
2. Evidence dashboard on the two marts (Phase 6) — decide both ✎ definitions with the
   distributions on screen
3. Dagster (Phase 4) → CI → droplet
