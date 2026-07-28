SELECT id as event_id, 
created_at,
event_name, 
properties, 
student_id as user_id, 
session_id
FROM {{ source('lake', 'event')}}