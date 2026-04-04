from typing import Iterable

from src.domain.task import Task


class TaskAPI:
    """Имитация API с задачами"""

    def get_tasks(self) -> Iterable[Task]:
        """Возвращает список задач из API"""
        payload_1 = "Мяукнуть"
        payload_2 = "Гавкнуть"
        payload_3 = "Гоготнуть"
        task_1 = Task(100001, payload_1)
        task_2 = Task(100002, payload_2, 4)
        task_3 = Task(100003, payload_3, 5)
        tasks = [task_1, task_2, task_3]
        for task in tasks:
            yield task
