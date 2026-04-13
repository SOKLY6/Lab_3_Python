from typing import Iterable

from src.domain.task import Task


class TaskAPI:
    """Источник из API"""

    def get_tasks(self) -> Iterable[Task]:
        """Возвращает задачи"""
        tasks = [
            Task(100001, "Мяукнуть"),
            Task(100002, "Гавкнуть", 4),
            Task(100003, "Гоготнуть", 5),
        ]
        for task in tasks:
            yield task
