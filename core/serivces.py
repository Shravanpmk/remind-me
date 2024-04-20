from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Generic, Optional, Type, TypeVar

from django.core.paginator import EmptyPage, Paginator
from django.db import models, transaction

from .models import Reminder, User

ModelType = TypeVar("ModelType", bound=models.Model)


class BaseService(ABC, Generic[ModelType]):
    def __init__(
        self, user_id: int, model: Type[ModelType], is_user_table=False
    ) -> None:
        self.user_id = user_id
        self.__model = model
        self.__is_user_table = is_user_table

    def __get_all_records(self) -> models.QuerySet[ModelType]:
        if self.__is_user_table:
            return self.__model.objects.filter(id=self.user_id)

        return self.__model.objects.filter(user_id=self.user_id)

    @abstractmethod
    def _filter_records(
        self, queryset: models.QuerySet[ModelType]
    ) -> models.QuerySet[ModelType]:
        pass

    def get_filtered_records(
        self, per_page: int = 100, page: int = 0, order_by: str = "id"
    ) -> models.QuerySet[ModelType]:
        if self.__is_user_table:
            return self.__model.objects.filter(id=self.user_id)

        queryset = self._filter_records(
            queryset=self.__get_all_records().order_by(order_by)
        )

        paginator = Paginator(queryset, per_page)

        try:
            return paginator.page(page).object_list
        except EmptyPage:
            return self._filter_records(queryset=self.__model.objects.none())

    def get_records(self) -> models.QuerySet[ModelType]:
        return self.__get_all_records().filter(deleted_on__isnull=True)

    def get_record_by_id(self, record_id: int) -> Optional[ModelType]:
        return self.get_records().get(id=record_id)

    @transaction.atomic
    def create_record(self, data: Dict[str, Any], timestamp: datetime) -> int:
        if not self.__is_user_table:
            user_record = UserService(user_id=self.user_id).get_record_by_id(
                record_id=self.user_id
            )
            data["user_id"] = user_record

        data["created_on"] = timestamp
        data["updated_on"] = timestamp

        created_record = self.__model.objects.create(**data)

        return created_record.id

    @transaction.atomic
    def update_record(
        self, record_id: int, updated_data: Dict[str, Any], timestamp: datetime
    ) -> None:
        updated_data["updated_on"] = timestamp

        active_record = self.get_record_by_id(record_id=record_id)

        if not active_record:
            # !TODO: Create Exception
            raise Exception("Invalid record ID")

        for field, value in updated_data.items():
            setattr(active_record, field, value)

        active_record.save()

    @transaction.atomic
    def delete_record(self, record_id: int, timestamp: datetime) -> None:
        data = {"updated_on": timestamp, "deleted_on": timestamp}

        self.update_record(record_id=record_id, updated_data=data, timestamp=timestamp)


class UserService(BaseService[User]):
    def __init__(self, user_id: int):
        super().__init__(user_id, User, True)

    def _filter_records(self, queryset: models.QuerySet[User]) -> models.QuerySet[User]:
        return queryset


class ReminderService(BaseService[Reminder]):
    def __init__(self, user_id: int):
        super().__init__(user_id, Reminder)

    def _filter_records(
        self, queryset: models.QuerySet[Reminder]
    ) -> models.QuerySet[Reminder]:
        queryset = queryset.annotate(
            status=models.Case(
                models.When(deleted_on__isnull=False, then=models.Value("deleted")),
                models.When(
                    deleted_on__isnull=True, is_sent=True, then=models.Value("sent")
                ),
                models.When(
                    deleted_on__isnull=True, is_sent=False, then=models.Value("created")
                ),
                default=models.Value("unknown"),
                output_field=models.CharField(),
            )
        )

        return queryset

    def update_send_status(self, record_id: int, timestamp: datetime) -> None:
        self.update_record(
            record_id=record_id, updated_data={"is_sent": True}, timestamp=timestamp
        )

    def update_notification_task_id(
        self, record_id: int, notification_task_id: str, timestamp: datetime
    ) -> None:
        self.update_record(
            record_id=record_id,
            updated_data={"notification_task_id": notification_task_id},
            timestamp=timestamp,
        )
