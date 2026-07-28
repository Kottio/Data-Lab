SELECT 
id as progress_id, 
student_id, 
lesson_id, 
completed, 
completed_at, 
created_at, 
updated_at
FROM {{source("lake", "progress")}}