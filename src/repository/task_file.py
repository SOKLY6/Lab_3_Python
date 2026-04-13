import json
from typing import Iterable

from src.domain.task import Task


class FileSource:
    """Источник из файла"""

    def __init__(self, filename: str) -> None:
        """Сохраняет путь"""
        self.filename = filename

    def get_tasks(self) -> Iterable[Task]:
        """Читает задачи"""
        with open(self.filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                data = json.loads(line)
                yield Task(id=int(data["id"]), payload=data["payload"])
