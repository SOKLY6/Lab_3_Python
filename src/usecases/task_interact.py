from src.domain.protocols import TaskSource
from src.domain.task import Task
from src.repository.task_storage import TaskStorage


class TaskInteract:
    """Класс для работы с задачами"""

    def __init__(self, storage: TaskStorage) -> None:
        """Инициализирует хранилище"""
        self._storage = storage

    def add_tasks_from_source(self, source: TaskSource) -> int:
        """Добавляет задачи из источника в хранилище"""
        if not isinstance(source, TaskSource):
            raise TypeError

        tasks = list(source.get_tasks())
        self._storage.add_tasks(tasks)
        return len(tasks)

    def get_all_tasks(self) -> list[Task]:
        """Возвращает все задачи"""
        return self._storage.get_list_tasks()
