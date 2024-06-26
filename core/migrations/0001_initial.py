# Generated by Django 5.0.4 on 2024-04-19 10:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.AutoField(primary_key=True, serialize=False, unique=True),
                ),
                ("created_on", models.DateTimeField()),
                ("updated_on", models.DateTimeField()),
                ("deleted_on", models.DateTimeField(null=True)),
                ("full_name", models.CharField(max_length=63)),
            ],
            options={
                "db_table": "users",
            },
        ),
        migrations.CreateModel(
            name="Reminder",
            fields=[
                (
                    "id",
                    models.AutoField(primary_key=True, serialize=False, unique=True),
                ),
                ("created_on", models.DateTimeField()),
                ("updated_on", models.DateTimeField()),
                ("deleted_on", models.DateTimeField(null=True)),
                ("is_sent", models.BooleanField(default=False)),
                ("message", models.CharField(max_length=255)),
                (
                    "user_id",
                    models.ForeignKey(
                        db_column="user_id",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="core.user",
                    ),
                ),
            ],
            options={
                "db_table": "reminders",
            },
        ),
    ]
