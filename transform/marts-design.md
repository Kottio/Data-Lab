# Marts design — from questions to grains

> Working doc for the dimensional model. Every mart's grain is a sentence; the sentence becomes its `unique` test.
> Status: DRAFT — open decisions marked ❓, to settle before model #1.

## The questions

- How many new users, weekly? — the pulse. (U1)
- Visit → signup rate, by source — is TikTok/bridge working?
- % of new users active within 7 days — does onboarding work?
- How many engaged free users convrt — and how many never do? — the crown. (D1)
- engaged free user avg activity
- Revenue, weekly. — the scoreboard. (D2)

## Processes hiding in them → the facts

| Process observed                              | Fact                  | Grain (one row per…)                | Feeds questions  |
| --------------------------------------------- | --------------------- | ----------------------------------- | ---------------- |
| A student does something (view, click, visit) | `fct_activity`        | **student × event x progress**      | 3,4,5


## Dimensions

- `dim_student` — plan, signup date, acquisition source, Total_lesson_viewed, 
- `dim_date` — standard calendar.


## Aggregated marts (the dashboard feeds)





## ❓ Open decisions — settle BEFORE building

1. **"Active" needs a definition.** ≥1 event within how many days? Rolling 7/30-day? Every metric
   here depends on it. Write it once, in words; it later becomes THE semantic-layer definition.
2. **Free→paid history doesn't exist yet.** `raw.students` holds only the _current_ plan — our merge
   overwrites history, so conversion (Q1) is currently unanswerable. Options:
   a) a payments/subscription table in Neon → ingest it (best if it exists — where do plan changes live?),
   b) **dbt snapshots** on stg_students (SCD2 — records plan transitions from now on),
   c) an app-side plan_changed event.
3. **"First module"** — is module order explicit in the data (position column?) or convention?
4. **Bridge activity (Q5)** — which event fields identify destination (YouTube vs landing)?
   Are referrer/source properties in `raw.events`? Q9 (YouTube analytics) = separate future source.

## Order of construction (once decisions land)

1. `dim_student` + `fct_activity` → answers 4, 6, 7, 8 immediately
2. `dim_content` + `fct_progress` → answers 3
3. plan-history decision → `fct_plan_changes` + `mart_funnel` → answers 1, 2
4. `mart_engagement_daily` last — aggregates are cheap once facts are right## THE QUESTIONS — the core six (frozen 27/07)

_The dashboard. Test each passed: "would this number change what I do next week?"_

1. **How many new users, weekly?** — the pulse
2. **Visit → signup rate, by source** — is TikTok/bridge working? _(contains weekly visits by source)_
3. **% of new users active within 7 days** — does onboarding work?
4. **How many engaged free users convert — and how many never do?** — the crown 👑
5. **Engaged free users: average activity** — how alive is the free tier?
6. **Revenue, weekly** — the scoreboard

**Definitions ✎:** active = ≥1 identified event · activation window = 7 days ·
"engaged" = threshold TBD (decide from the real distribution at build time) ·
conversion = a row in `payment` · source: `bridge_*` events → `tik_tok`, else `other`

## Drill-downs (not on the dashboard — opened when a core number looks wrong)

- Never-activated users: how many, and why (by source, by cohort)
- Weekly actives / events per active, by plan · module-1 completion within 14 days (`progress`)
- Avg activity per cohort · median time signup → first `dashboard` event
- Revenue by cohort · conversion window analysis






with count_new AS ( SELECT count(*) as count_students , week(created_at) as week_num  from students group by week(created_at))  SELECT *, week(created_at) as week_num  FROM students inner join count_new on count_new.week_num = week(students.created_at)