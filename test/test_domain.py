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
from src.usecases.task_handlers import NewTaskHandler, ProcessingTaskHandler


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


def test_task_queue_iter_contains_put_and_get() -> None:
    async def run() -> tuple[list[int], bool, int]:
        first = Task(1, "a", 1, "new")
        second = Task(2, "b", 2, "processing")
        queue = TaskQueue([first])
        await queue.put(second)
        task = await queue.get()
        return [item.id for item in queue], first in queue, task.id if task else 0

    remaining_ids, contains_first, task_id = asyncio.run(run())

    assert remaining_ids == [2]
    assert contains_first is False
    assert task_id == 1


def test_task_queue_filters_remove_tasks() -> None:
    async def run() -> tuple[list[int], list[int], list[int]]:
        queue = TaskQueue(
            [
                Task(1, "a", 1, "new"),
                Task(2, "b", 2, "processing"),
                Task(3, "c", 3, "new"),
            ]
        )
        filtered_by_status = [task.id async for task in queue.filter_by_status("new")]
        await queue.put(Task(3, "c", 3, "new"))
        filtered_by_priority = [
            task.id
            async for task in queue.filter_by_priority(
                min_priority=2,
                max_priority=3,
            )
        ]
        remaining = [task.id for task in queue]
        return filtered_by_status, filtered_by_priority, remaining

    filtered_by_status, filtered_by_priority, remaining = asyncio.run(run())

    assert filtered_by_status == [1, 3]
    assert filtered_by_priority == [2, 3]
    assert remaining == []


def test_task_queue_context_manager_closes_queue() -> None:
    async def run() -> bool:
        queue = TaskQueue([])
        async with queue:
            pass
        task = await queue.get()
        return task is None

    assert asyncio.run(run()) is True


def test_exceptions_inherit_base_exception() -> None:
    assert issubclass(IncorrectTaskId, TaskException)
    assert issubclass(EmptyTaskPayload, TaskException)
    assert issubclass(IncorrectTaskPriority, TaskException)
    assert issubclass(IncorrectTaskStatus, TaskException)


def test_handlers_match_protocol() -> None:
    assert isinstance(NewTaskHandler(), TaskExecutor)
    assert isinstance(ProcessingTaskHandler(), TaskExecutor)
