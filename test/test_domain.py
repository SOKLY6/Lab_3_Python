import asyncio
from datetime import datetime, timedelta

import pytest

from src.domain.exceptions import (
    EmptyTaskPayload,
    IncorrectTaskId,
    IncorrectTaskPriority,
    IncorrectTaskStatus,
    TaskException,
)
from src.domain.protocols import TaskExecutor
from src.domain.task import Task
from src.domain.task_queue import TaskQueue
from src.usecases.task_handlers import (
    CompleteTaskHandler,
    NewTaskHandler,
    ProcessingTaskHandler,
)


class BrokenHandler:
    def can_handle(self, task: Task) -> bool:
        return task.id == 99

    async def handle_task(self, task: Task) -> None:
        raise RuntimeError("boom")


def test_task_validates_fields() -> None:
    task = Task(1, "test", 2, "new")

    assert task.id == 1
    assert task.payload == "test"
    assert task.priority == 2
    assert task.status == "new"
    assert isinstance(task.creation_time, datetime)
    assert isinstance(task.living_time, timedelta)


def test_task_raises_validation_errors() -> None:
    with pytest.raises(TypeError):
        Task("1", "x")  # type: ignore[arg-type]
    with pytest.raises(IncorrectTaskId):
        Task(0, "x")
    with pytest.raises(EmptyTaskPayload):
        Task(1, None)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        Task(1, 1)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        Task(1, "x", "1")  # type: ignore[arg-type]
    with pytest.raises(IncorrectTaskPriority):
        Task(1, "x", 0)
    with pytest.raises(TypeError):
        Task(1, "x", 1, 1)  # type: ignore[arg-type]
    with pytest.raises(IncorrectTaskStatus):
        Task(1, "x", 1, "bad")


def test_task_queue_iter_contains_and_filters() -> None:
    first = Task(1, "a", 1, "new")
    second = Task(2, "b", 2, "processing")
    third = Task(3, "c", 3, "new")
    queue = TaskQueue([first, second, third])

    assert [task.id for task in queue] == [1, 2, 3]
    assert first in queue
    assert Task(4, "d") not in queue

    filtered_by_status = queue.filter_by_status("new")
    assert next(filtered_by_status).id == 1
    assert [task.id for task in queue] == [2, 3]
    assert [task.id for task in filtered_by_status] == [3]
    assert [task.id for task in queue] == [2]

    queue.add_tasks([first, third])
    filtered_by_priority = queue.filter_by_priority(min_priority=2, max_priority=3)
    assert [task.id for task in filtered_by_priority] == [2, 3]
    assert [task.id for task in queue] == [1]


def test_task_queue_processes_tasks() -> None:
    queue = TaskQueue(
        [
            Task(1, "a", 1, "new"),
            Task(2, "b", 1, "processing"),
            Task(3, "c", 1, "complete"),
            Task(99, "d", 1, "new"),
        ]
    )

    processed = asyncio.run(
        queue.process_tasks(
            [
                BrokenHandler(),
                NewTaskHandler(),
                ProcessingTaskHandler(),
                CompleteTaskHandler(),
            ]
        )
    )

    tasks = list(queue)
    assert processed == 3
    assert tasks[0].status == "processing"
    assert tasks[1].status == "complete"
    assert tasks[2].status == "complete"
    assert tasks[3].status == "new"


def test_task_queue_skips_task_without_handler() -> None:
    queue = TaskQueue([Task(1, "a", 1, "new")])

    processed = asyncio.run(queue.process_tasks([ProcessingTaskHandler()]))

    assert processed == 0
    assert list(queue)[0].status == "new"


def test_exceptions_inherit_base_exception() -> None:
    assert issubclass(IncorrectTaskId, TaskException)
    assert issubclass(EmptyTaskPayload, TaskException)
    assert issubclass(IncorrectTaskPriority, TaskException)
    assert issubclass(IncorrectTaskStatus, TaskException)


def test_handlers_match_protocol() -> None:
    assert isinstance(NewTaskHandler(), TaskExecutor)
    assert isinstance(ProcessingTaskHandler(), TaskExecutor)
    assert isinstance(CompleteTaskHandler(), TaskExecutor)
