from __future__ import absolute_import, unicode_literals

from logging import getLogger

from celery import shared_task
from django.utils import timezone

from .services import ReminderService

logger = getLogger(__name__)


@shared_task
def send_reminder(user_id: int, reminder_id: int):
    current_timestamp = timezone.now()
    reminder_service = ReminderService(user_id=user_id)

    message = reminder_service.get_record_by_id(reminder_id)

    logger.info("Sending email with content: {%s}", message)

    reminder_service.update_send_status(
        record_id=reminder_id, timestamp=current_timestamp
    )
