import json
from typing import Iterable

from src.domain.task import Task


class FileSource:
    """Читает задачи из JSONL файла"""

    def __init__(self, filename: str) -> None:
        """Сохраняет путь к файлу"""
        self.filename = filename

    def get_tasks(self) -> Iterable[Task]:
        """Читает и возвращает задачи из файла"""
        with open(self.filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                data = json.loads(line)
                task = Task(id=int(data["id"]), payload=data["payload"])
                yield task
