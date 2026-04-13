import asyncio
from logging import Logger
from typing import Iterable, Iterator

from src.domain.protocols import TaskExecutor
from src.domain.task import Task
from src.logger.logger import get_logger


class TaskQueue:
    """Очередь задач"""

    def __init__(self, tasks: Iterable[Task] | None = None) -> None:
        """Создаёт очередь"""
        self._tasks = list(tasks) if tasks is not None else []
        self._async_queue: asyncio.Queue[Task] | None = None

    def add_tasks(self, tasks: Iterable[Task]) -> None:
        """Добавляет задачи"""
        self._tasks.extend(tasks)

    def __iter__(self) -> Iterator[Task]:
        """Итерируется по задачам"""
        for task in self._tasks:
            yield task

    def __contains__(self, task: object) -> bool:
        """Проверяет наличие задачи"""
        return task in self._tasks

    async def __aenter__(self) -> "TaskQueue":
        """Готовит async очередь"""
        self._async_queue = asyncio.Queue()
        for task in self._tasks:
            await self._async_queue.put(task)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: object | None,
    ) -> bool:
        """Освобождает ресурсы"""
        self._async_queue = None
        return False

    def filter_by_status(self, status: str) -> Iterator[Task]:
        """Извлекает задачи по статусу"""
        index = 0
        while index < len(self._tasks):
            task = self._tasks[index]
            if task.status == status:
                yield self._tasks.pop(index)
            else:
                index += 1

    def filter_by_priority(
        self,
        min_priority: int | None = None,
        max_priority: int | None = None,
    ) -> Iterator[Task]:
        """Извлекает задачи по приоритету"""
        index = 0
        while index < len(self._tasks):
            task = self._tasks[index]
            if min_priority is not None and task.priority < min_priority:
                index += 1
                continue
            if max_priority is not None and task.priority > max_priority:
                index += 1
                continue
            yield self._tasks.pop(index)

    async def process_tasks(
        self,
        handlers: list[TaskExecutor],
        logger: Logger | None = None,
    ) -> int:
        """Асинхронно обрабатывает задачи"""
        current_logger = logger or get_logger(__name__)
        processed_count = 0

        async with self:
            if self._async_queue is None:
                return processed_count

            while not self._async_queue.empty():
                task = await self._async_queue.get()
                try:
                    handler = self._get_handler(task, handlers)
                    await handler.handle_task(task)
                    processed_count += 1
                    current_logger.info("Task %s processed", task.id)
                except LookupError as error:
                    current_logger.error(str(error))
                except Exception as error:
                    current_logger.exception(
                        "Task %s failed: %s",
                        task.id,
                        error,
                    )
                finally:
                    self._async_queue.task_done()

        return processed_count

    def _get_handler(
        self,
        task: Task,
        handlers: list[TaskExecutor],
    ) -> TaskExecutor:
        """Находит обработчик"""
        for handler in handlers:
            if handler.can_handle(task):
                return handler

        raise LookupError(f"Handler not found for task {task.id}")
