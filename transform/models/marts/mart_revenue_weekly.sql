-- Grain: one row per payment week. Answers Q6 (the scoreboard).
-- Why its own mart: payment week is NOT cohort week. Folding revenue into
-- mart_kpis_weekly (grain: cohort_week x source) would break that model's grain —
-- the classic way a dashboard starts lying. Built now because Evidence reads it.
-- NOTE: `amount` is assumed to be minor units (cents). Confirm against Stripe before trusting.
select
    date_trunc('week', created_at)  as payment_week,
    count(*)                        as payments,
    count(distinct student_id)      as paying_students,
    sum(amount) / 100.0             as revenue
from {{ ref('stg_payments') }}
group by 1
order by 1
