import asyncio
from typing import AsyncIterator, Iterable, Iterator

from src.domain.task import Task


class TaskQueue:
    """Асинхронная очередь задач"""

    def __init__(self, tasks: Iterable[Task] | None = None) -> None:
        """Создаёт очередь"""
        self._tasks = list(tasks) if tasks is not None else []
        self._condition = asyncio.Condition()
        self._closed = False

    def __iter__(self) -> Iterator[Task]:
        """Итерируется по задачам"""
        return iter(list(self._tasks))

    def __contains__(self, task: object) -> bool:
        """Проверяет наличие задачи"""
        return task in self._tasks

    async def __aenter__(self) -> "TaskQueue":
        """Открывает очередь"""
        self._closed = False
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: object | None,
    ) -> bool:
        """Закрывает очередь"""
        await self.close()
        return False

    async def put(self, task: Task) -> None:
        """Добавляет задачу"""
        async with self._condition:
            if self._closed:
                raise RuntimeError("Очередь закрыта")

            self._tasks.append(task)
            self._condition.notify()

    async def put_tasks(self, tasks: Iterable[Task]) -> None:
        """Добавляет список задач"""
        async with self._condition:
            if self._closed:
                raise RuntimeError("Очередь закрыта")

            added = list(tasks)
            self._tasks.extend(added)
            if added:
                self._condition.notify_all()

    async def get(self) -> Task | None:
        """Возвращает задачу"""
        async with self._condition:
            while not self._tasks and not self._closed:
                await self._condition.wait()

            if not self._tasks:
                return None

            return self._tasks.pop(0)

    async def close(self) -> None:
        """Закрывает очередь"""
        async with self._condition:
            self._closed = True
            self._condition.notify_all()

    async def filter_by_status(self, status: str) -> AsyncIterator[Task]:
        """Извлекает задачи по статусу"""
        while True:
            async with self._condition:
                task = self._pop_first_by_status(status)
            if task is None:
                return
            yield task

    async def filter_by_priority(
        self,
        min_priority: int | None = None,
        max_priority: int | None = None,
    ) -> AsyncIterator[Task]:
        """Извлекает задачи по приоритету"""
        while True:
            async with self._condition:
                task = self._pop_first_by_priority(
                    min_priority=min_priority,
                    max_priority=max_priority,
                )
            if task is None:
                return
            yield task

    def _pop_first_by_status(self, status: str) -> Task | None:
        for index, task in enumerate(self._tasks):
            if task.status == status:
                return self._tasks.pop(index)
        return None

    def _pop_first_by_priority(
        self,
        min_priority: int | None = None,
        max_priority: int | None = None,
    ) -> Task | None:
        for index, task in enumerate(self._tasks):
            if min_priority is not None and task.priority < min_priority:
                continue
            if max_priority is not None and task.priority > max_priority:
                continue
            return self._tasks.pop(index)
        return None
