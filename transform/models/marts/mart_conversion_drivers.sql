-- Grain: one row per student — journey features + outcome. Answers Q4 (crown), feeds Q3/Q5.
-- Single-use rollups stay as CTEs (YAGNI — promote only when a second consumer appears).
with lessons as (
    select student_id,
           count(distinct lesson_id)              as lessons_viewed,
           count(*) filter (where completed)      as lessons_completed,
           min(created_at)                        as first_lesson_at   -- the activation moment
    from {{ ref('stg_progress') }}
    group by student_id
),
dash as (
    select user_id, count(*) as dash_access
    from {{ ref('stg_events') }}
    where event_name = 'dashboard'
    group by user_id
),
pay as (
    select student_id,
           min(created_at)  as first_payment_at,
           sum(amount)      as total_paid
    from {{ ref('stg_payments') }}
    group by student_id
)
select
    d.student_id,
    d.user_id,
    d.signed_up_at,
    d.access_type,
    d.acquisition_source,
    coalesce(da.dash_access, 0)        as dash_access,
    coalesce(l.lessons_viewed, 0)      as lessons_viewed,
    l.first_lesson_at,
    l.first_lesson_at is not null      as is_activated,        -- activated = viewed >= 1 lesson
    l.first_lesson_at is not null
      and l.first_lesson_at <= d.signed_up_at + interval 7 day as activated_within_7d,
    p.first_payment_at is not null     as converted,
    p.first_payment_at,
    coalesce(p.total_paid, 0)          as total_paid
    -- TODO is_engaged: threshold decided from the real distribution
from {{ ref('dim_student') }} d
left join lessons l  on l.student_id = d.student_id
left join dash    da on da.user_id   = d.user_id
left join pay     p  on p.student_id = d.student_id
