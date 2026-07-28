-- Grain: one row per session (browser identity).
-- Foundation of all traffic/cohort numbers — guarded by unique test on session_id.
with signup_time as (
    select session_id, min(created_at) as signed_up_at
    from {{ ref('stg_events') }}
    where event_name = 'new_user'
    group by session_id
)
select
    e.session_id,
    min(e.created_at)                        as first_seen,
    bool_or(s.session_id is not null)        as signed_up,
    min(s.signed_up_at)                      as signed_up_at,
    bool_or(e.event_name like 'bridge%')     as from_bridge
from {{ ref('stg_events') }} e
left join signup_time s using (session_id)
where e.created_at <= coalesce(s.signed_up_at, timestamp '9999-12-31')
  and e.event_name not in ('dashboard', 'pro_page_view')
group by e.session_id
