# remind-me
A reminder application that sends an email to the user based on the reminder date and time set by the user.

The solution is done using Django, Celery, PostgresSQL and RabbitMQ

Steps to run the project include giving the source as env.sh, python manage.py migrate.

The endpoints used are as follows:
1. 


Celeray ->  task = send_reminder.apply_async(args=[user_id, record_id], eta=reminder_time)
Will push to RabbitMQ
