from datetime import datetime, timedelta

from src.domain.descriptors import (
    CorrectTaskId,
    CorrectTaskPriority,
    CorrectTaskStatus,
    NotEmptyPayload,
)


class Task:
    """Модель задачи"""

    id = CorrectTaskId()
    payload = NotEmptyPayload()
    priority = CorrectTaskPriority()
    status = CorrectTaskStatus()

    def __init__(
        self, id: int, payload: str, priority: int = 1, status: str = "new"
    ) -> None:
        """Создаёт задачу"""
        self.id = id
        self.payload = payload
        self.priority = priority
        self.status = status
        self.__creation_time = datetime.now()

    @property
    def living_time(self) -> timedelta:
        """Возвращает время жизни"""
        return datetime.now() - self.__creation_time

    @property
    def creation_time(self) -> datetime:
        """Возвращает время создания"""
        return self.__creation_time
