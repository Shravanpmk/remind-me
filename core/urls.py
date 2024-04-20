from django.urls import path

from .views import CreateReminderView, DeleteReminderView, GetRemindersView

urlpatterns = [
    path("reminders", GetRemindersView.as_view(), name="get-reminders-view"),
    path("reminders/create", CreateReminderView.as_view(), name="create-reminder-view"),
    path("reminders/delete", DeleteReminderView.as_view(), name="delete-reminder-view"),
]
