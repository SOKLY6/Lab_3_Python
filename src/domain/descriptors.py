from typing import Any

from src.domain.exceptions import (
    EmptyTaskPayload,
    IncorrectTaskId,
    IncorrectTaskPriority,
    IncorrectTaskStatus,
)


class CorrectTaskId:
    def __set_name__(self, owner: Any, name: str) -> None:
        self.name = "_" + name

    def __get__(self, instance: Any, owner: Any) -> int:
        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Id должно быть целым числом")
        if value < 1:
            raise IncorrectTaskId("Id должен быть натуральным числом")
        instance.__dict__[self.name] = value


class NotEmptyPayload:
    def __set_name__(self, owner: Any, name: str) -> None:
        self.name = "_" + name

    def __get__(self, instance: Any, owner: Any) -> str:
        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: str) -> None:
        if value is None:
            raise EmptyTaskPayload("Описание задачи не может быть пустым")
        if not isinstance(value, str):
            raise TypeError("Описание задачи должно задаваться строкой")
        instance.__dict__[self.name] = value


class CorrectTaskPriority:
    def __set_name__(self, owner: Any, name: str) -> None:
        self.name = "_" + name

    def __get__(self, instance: Any, owner: Any) -> int:
        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Приоритет должен быть целым числом")
        if value < 1:
            raise IncorrectTaskPriority(
                "Приоритет задачи должен задаваться натуральным числом"
            )
        instance.__dict__[self.name] = value


class CorrectTaskStatus:
    STATUSES = ["new", "processing", "complete"]

    def __set_name__(self, owner: Any, name: str) -> None:
        self.name = "_" + name

    def __get__(self, instance: Any, owner: Any) -> str:
        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Статус задачи должен задаваться строкой")
        if value not in self.STATUSES:
            raise IncorrectTaskStatus("Несуществующий статус задачи")
        instance.__dict__[self.name] = value
