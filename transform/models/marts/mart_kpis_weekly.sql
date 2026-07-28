-- Grain: one row per cohort_week x source. Answers Q1 (new users) & Q2 (visit->signup rate).
select
    date_trunc('week', first_seen)                          as cohort_week,
    case when from_bridge then 'tik_tok' else 'other' end   as source,
    count(*)                                                as new_visitors,
    count(*) filter (where signed_up)                       as signups,
    round(100.0 * count(*) filter (where signed_up) / count(*), 1) as signup_rate_pct
from {{ ref('int_sessions') }}
group by 1, 2
order by 1, 2
