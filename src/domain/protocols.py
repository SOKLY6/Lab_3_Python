from typing import Iterable, Protocol, runtime_checkable

from src.domain.task import Task


@runtime_checkable
class TaskSource(Protocol):
    """Источник задач"""

    def get_tasks(self) -> Iterable[Task]:
        """Возвращает задачи"""
        ...


@runtime_checkable
class TaskExecutor(Protocol):
    """Обработчик задач"""

    def can_handle(self, task: Task) -> bool:
        """Проверяет задачу"""
        ...

    async def handle_task(self, task: Task) -> None:
        """Обрабатывает задачу"""
        ...
