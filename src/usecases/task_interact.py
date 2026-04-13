import asyncio
from logging import Logger

from src.domain.protocols import TaskExecutor, TaskSource
from src.domain.task import Task
from src.domain.task_queue import TaskQueue
from src.logger.logger import get_logger


class TaskQueueInteract:
    """Сервис очереди"""

    def __init__(self, queue: TaskQueue) -> None:
        """Сохраняет очередь"""
        self._queue = queue
        self._logger = get_logger(__name__)
        self._executors: list[TaskExecutor] = []
        self._running = False
        self._processed_count = 0

    async def add_tasks_from_sources(self, sources: list[TaskSource]) -> int:
        """Добавляет задачи из источников"""
        total = 0

        for source in sources:
            if not isinstance(source, TaskSource):
                raise TypeError

            tasks = list(source.get_tasks())
            await self._queue.put_tasks(tasks)
            total += len(tasks)

        return total

    def get_all_tasks(self) -> TaskQueue:
        """Возвращает очередь"""
        return self._queue

    def register_executor(self, executor: TaskExecutor) -> None:
        """Регистрирует исполнителя"""
        if not isinstance(executor, TaskExecutor):
            raise TypeError("Исполнитель должен соответствовать TaskExecutor")

        self._executors.append(executor)

    async def process_tasks(
        self,
        worker_count: int = 1,
        logger: Logger | None = None,
    ) -> int:
        """Запускает обработку"""
        current_logger = logger or self._logger
        self._running = True
        self._processed_count = 0

        async with self._queue:
            workers = [
                asyncio.create_task(self._worker(index + 1, current_logger))
                for index in range(worker_count)
            ]
            await self._queue.close()
            await asyncio.gather(*workers)

        self._running = False
        return self._processed_count

    async def _worker(self, worker_id: int, logger: Logger) -> None:
        """Обрабатывает задачи"""
        logger.info("Worker %s started", worker_id)

        while self._running:
            task = await self._queue.get()
            if task is None:
                return

            executor = self._get_executor(task)
            if executor is None:
                logger.error("Executor not found for task %s", task.id)
                continue

            try:
                await executor.handle_task(task)
                self._processed_count += 1
                logger.info("Worker %s processed task %s", worker_id, task.id)
            except Exception as error:
                logger.exception(
                    "Worker %s failed task %s: %s",
                    worker_id,
                    task.id,
                    error,
                )

    def _get_executor(self, task: Task) -> TaskExecutor | None:
        for executor in self._executors:
            if executor.can_handle(task):
                return executor
        return None
