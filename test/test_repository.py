from pathlib import Path

import pytest

from src.domain.protocols import TaskSource
from src.domain.task import Task
from src.logger.logger import get_logger
from src.repository.task_api import TaskAPI
from src.repository.task_file import FileSource
from src.repository.task_generator import TaskGenerator
from src.repository.task_storage import TaskStorage


def test_file_source_reads_tasks(tmp_path: Path) -> None:
    file_path = tmp_path / "tasks.jsonl"
    file_path.write_text('{"id": 1, "payload": "one"}\n\n{"id": 2, "payload": "two"}\n')

    tasks = list(FileSource(str(file_path)).get_tasks())

    assert [task.id for task in tasks] == [1, 2]
    assert [task.payload for task in tasks] == ["one", "two"]


def test_file_source_raises_for_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        list(FileSource("missing.jsonl").get_tasks())


def test_task_api_returns_fixed_tasks() -> None:
    tasks = list(TaskAPI().get_tasks())

    assert [task.id for task in tasks] == [100001, 100002, 100003]
    assert [task.priority for task in tasks] == [1, 4, 5]


def test_task_generator_creates_requested_count() -> None:
    TaskGenerator._id = 1
    generator = TaskGenerator(2)

    tasks = list(generator.get_tasks())

    assert len(tasks) == 2
    assert [task.id for task in tasks] == [1, 2]


def test_task_storage_stores_tasks() -> None:
    storage = TaskStorage()
    tasks = [Task(1, "a"), Task(2, "b")]

    storage.add_tasks(tasks)

    assert storage.get_list_tasks() == tasks


def test_repository_objects_match_protocol_and_logger_returns_logger() -> None:
    assert isinstance(TaskAPI(), TaskSource)
    assert isinstance(TaskGenerator(1), TaskSource)
    assert get_logger("test").name == "test"
