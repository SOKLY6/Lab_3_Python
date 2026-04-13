from typing import Any

from src.domain.exceptions import (
    EmptyTaskPayload,
    IncorrectTaskId,
    IncorrectTaskPriority,
    IncorrectTaskStatus,
)


class CorrectTaskId:
    """Дескриптор id"""

    def __set_name__(self, owner: Any, name: str) -> None:
        """Сохраняет имя"""
        self.name = "_" + name

    def __get__(self, instance: Any, owner: Any) -> int:
        """Возвращает id"""
        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: int) -> None:
        """Проверяет id"""
        if not isinstance(value, int):
            raise TypeError("Id должно быть целым числом")
        if value < 1:
            raise IncorrectTaskId("Id должен быть натуральным числом")
        instance.__dict__[self.name] = value


class NotEmptyPayload:
    """Дескриптор payload"""

    def __set_name__(self, owner: Any, name: str) -> None:
        """Сохраняет имя"""
        self.name = "_" + name

    def __get__(self, instance: Any, owner: Any) -> str:
        """Возвращает payload"""
        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: str) -> None:
        """Проверяет payload"""
        if value is None:
            raise EmptyTaskPayload("Описание задачи не может быть пустым")
        if not isinstance(value, str):
            raise TypeError("Описание задачи должно задаваться строкой")
        instance.__dict__[self.name] = value


class CorrectTaskPriority:
    """Дескриптор приоритета"""

    def __set_name__(self, owner: Any, name: str) -> None:
        """Сохраняет имя"""
        self.name = "_" + name

    def __get__(self, instance: Any, owner: Any) -> int:
        """Возвращает приоритет"""
        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: int) -> None:
        """Проверяет приоритет"""
        if not isinstance(value, int):
            raise TypeError("Приоритет должен быть целым числом")
        if value < 1:
            raise IncorrectTaskPriority(
                "Приоритет задачи должен задаваться натуральным числом"
            )
        instance.__dict__[self.name] = value


class CorrectTaskStatus:
    """Дескриптор статуса"""

    STATUSES = ["new", "processing", "complete"]

    def __set_name__(self, owner: Any, name: str) -> None:
        """Сохраняет имя"""
        self.name = "_" + name

    def __get__(self, instance: Any, owner: Any) -> str:
        """Возвращает статус"""
        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: str) -> None:
        """Проверяет статус"""
        if not isinstance(value, str):
            raise TypeError("Статус задачи должен задаваться строкой")
        if value not in self.STATUSES:
            raise IncorrectTaskStatus("Несуществующий статус задачи")
        instance.__dict__[self.name] = value
