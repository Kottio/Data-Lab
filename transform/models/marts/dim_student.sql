-- Grain: one row per student. ATTRIBUTES ONLY.
-- Single course => one enrollment per student (1:1 join, created at signup).
with session_map as (
    -- stitching: session -> user (sessionId persists in localStorage)
    select session_id, min(user_id) as user_id
    from {{ ref('stg_events') }}
    where user_id is not null
    group by session_id
),
first_session as (
    -- acquisition source = source of the user's earliest known session
    select m.user_id, i.from_bridge,
           row_number() over (partition by m.user_id order by i.first_seen) as rn
    from session_map m
    join {{ ref('int_sessions') }} i using (session_id)
)
select
    s.student_id,
    s.user_id,
    s.created_at                                            as signed_up_at,
    e.access_type,
    case when f.from_bridge then 'tik_tok'
         when f.from_bridge is not null then 'other'
         else 'unknown' end                                 as acquisition_source
from {{ ref('stg_students') }} s
left join {{ ref('stg_enrollments') }} e on e.student_id = s.student_id
left join first_session f on f.user_id = s.user_id and f.rn = 1
