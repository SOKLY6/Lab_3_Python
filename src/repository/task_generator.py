import random
from typing import Iterable

from src.domain.task import Task


class TaskGenerator:
    """Генератор задач"""

    _id = 1
    TEXTS = [
        "Исправить баг с гусем",
        "Написать тесты",
        "Добавить функционал",
        "Починить гуся",
        "Разблокировать офис",
    ]

    def __init__(self, count: int) -> None:
        """Сохраняет количество"""
        self.count = count

    def get_tasks(self) -> Iterable[Task]:
        """Генерирует задачи"""
        for _ in range(self.count):
            yield Task(
                TaskGenerator._id,
                random.choice(TaskGenerator.TEXTS),
                random.randint(1, 5),
            )
            TaskGenerator._id += 1
