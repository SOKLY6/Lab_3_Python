from logging import Logger

from src.domain.protocols import TaskExecutor, TaskSource
from src.domain.task_queue import TaskQueue
from src.logger.logger import get_logger


class TaskQueueInteract:
    """Сервис очереди"""

    def __init__(self, queue: TaskQueue) -> None:
        """Сохраняет очередь"""
        self._queue = queue
        self._logger = get_logger(__name__)

    def add_tasks_from_sources(self, sources: list[TaskSource]) -> int:
        """Добавляет задачи из источников"""
        total = 0

        for source in sources:
            if not isinstance(source, TaskSource):
                raise TypeError

            tasks = list(source.get_tasks())
            self._queue.add_tasks(tasks)
            total += len(tasks)

        return total

    def get_all_tasks(self) -> TaskQueue:
        """Возвращает очередь"""
        return self._queue

    async def process_tasks_with_handlers(
        self,
        handlers: list[TaskExecutor],
        logger: Logger | None = None,
    ) -> int:
        """Запускает обработку"""
        current_logger = logger or self._logger
        return await self._queue.process_tasks(handlers, current_logger)
