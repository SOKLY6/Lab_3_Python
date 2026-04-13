import asyncio

from src.domain.task import Task


class NewTaskHandler():
    """Обработчик новых задач"""

    def can_handle(self, task: Task) -> bool:
        """Проверяет статус"""
        return task.status == "new"

    async def handle_task(self, task: Task) -> None:
        """Переводит в processing"""
        await asyncio.sleep(0)
        task.status = "processing"


class ProcessingTaskHandler():
    """Обработчик задач в работе"""

    def can_handle(self, task: Task) -> bool:
        """Проверяет статус"""
        return task.status == "processing"

    async def handle_task(self, task: Task) -> None:
        """Переводит в complete"""
        await asyncio.sleep(0)
        task.status = "complete"
