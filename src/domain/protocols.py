from typing import Iterable, Protocol, runtime_checkable

from src.domain.task import Task


@runtime_checkable
class TaskSource(Protocol):
    """Протокол источника задач"""

    def get_tasks(self) -> Iterable[Task]:
        """Отдаёт задачи из ресурса"""
        ...


@runtime_checkable
class TaskExecutor(Protocol):
    """Протокол испольнителя задач"""

    async def handle_task(self, task: Task) -> None:
        """Асинхронно обрабатывает задачу"""
        ...
