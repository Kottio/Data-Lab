SELECT id as payment_id, student_id, enrollment_id, amount, currency, created_at FROM {{source('lake', 'payments')}}

