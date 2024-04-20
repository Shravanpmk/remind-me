from datetime import datetime
from typing import Type

from celery.result import AsyncResult
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from .services import ReminderService
from .tasks import send_reminder


class GetRemindersView(APIView):
    def get(self, request: Type[Request]) -> Type[Response]:
        query_params = request.query_params

        user_id = int(query_params.get("userId", 1))
        per_page = int(query_params.get("perPage", 100))
        page = int(query_params.get("page", 0))
        order_by = str(query_params.get("sortBy", "id"))

        filtered_data = (
            ReminderService(user_id=user_id)
            .get_filtered_records(per_page=per_page, page=page, order_by=order_by)
            .values("created_on", "updated_on", "message", "status")
        )

        return Response(
            status=HTTP_200_OK, data={"status": "OK", "data": filtered_data}
        )


class CreateReminderView(APIView):
    def post(self, request: Type[Request]) -> Type[Response]:
        data = request.data
        current_timestamp = timezone.now()

        user_id = int(data.get("user_id", 1))
        message = str(data.get("message"))
        reminder_time = datetime.strptime(
            data.get("reminderTime"), "%Y-%m-%d %H:%M:%S.%f %z"
        )

        reminder_service = ReminderService(user_id=user_id)

        record_id = reminder_service.create_record(
            data={"message": message, "reminder_time": reminder_time},
            timestamp=current_timestamp,
        )

        task = send_reminder.apply_async(args=[user_id, record_id], eta=reminder_time)

        reminder_service.update_notification_task_id(
            record_id=record_id,
            notification_task_id=task.id,
            timestamp=current_timestamp,
        )

        return Response(
            status=HTTP_201_CREATED,
            data={"status": "OK", "message": "Reminder created successfully!"},
        )


class DeleteReminderView(APIView):
    def post(self, request: Type[Request]) -> Type[Response]:
        data = request.data
        current_timestamp = timezone.now()

        user_id = int(data.get("userId", 1))
        record_id = int(data.get("recordId", -1))

        reminder_service = ReminderService(user_id=user_id)

        record = reminder_service.get_record_by_id(record_id=record_id)

        notification_task_id = record.notification_task_id

        notification_task = AsyncResult(notification_task_id)

        if notification_task.state in ("SUCCESS", "FAILURE"):
            return Response(
                status=HTTP_400_BAD_REQUEST,
                data={
                    "status": "ERROR",
                    "code": "REMINDER_COMPLETE",
                    "message": "Reminder has been completed already!",
                },
            )

        elif notification_task.state == "STARTED":
            return Response(
                status=HTTP_400_BAD_REQUEST,
                data={
                    "status": "ERROR",
                    "code": "REMINDER_IN_PROGRESS",
                    "message": "Reminder is in progress!",
                },
            )

        reminder_service.delete_record(record_id=record_id, timestamp=current_timestamp)
        notification_task.revoke(terminate=False)

        return Response(
            status=HTTP_201_CREATED,
            data={"status": "OK", "message": "Reminder deleted successfully!"},
        )
