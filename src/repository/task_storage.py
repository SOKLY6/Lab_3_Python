from src.domain.task import Task


class TaskStorage:
    """Хранилище задач в памяти"""

    def __init__(self) -> None:
        """Инициализирует пустой список задач"""
        self.tasks_list: list[Task] = []

    def add_tasks(self, new_tasks: list[Task]) -> None:
        """Добавляет задачи в хранилище"""
        self.tasks_list.extend(new_tasks)

    def get_list_tasks(self) -> list[Task]:
        """Возвращает все задачи"""
        return self.tasks_list
