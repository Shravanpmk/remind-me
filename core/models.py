from django.db import models


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True, unique=True, null=False)
    created_on = models.DateTimeField(null=False)
    updated_on = models.DateTimeField(null=False)
    deleted_on = models.DateTimeField(null=True)

    class Meta:
        abstract = True


class User(BaseModel):
    full_name = models.CharField(max_length=63)

    class Meta:
        db_table = "users"


class Reminder(BaseModel):
    user_id = models.ForeignKey(User, db_column="user_id", on_delete=models.DO_NOTHING)
    is_sent = models.BooleanField(null=False, default=False)
    message = models.CharField(max_length=255)
    notification_task_id = models.CharField(max_length=63, null=True)
    reminder_time = models.DateTimeField(null=False)

    class Meta:
        db_table = "reminders"
