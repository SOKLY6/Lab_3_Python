import asyncio

import pytest

from src.domain.protocols import TaskExecutor
from src.domain.task import Task
from src.domain.task_queue import TaskQueue
from src.usecases.task_handlers import NewTaskHandler, ProcessingTaskHandler
from src.usecases.task_interact import TaskQueueInteract


class BadSource:
    pass


class LocalSource:
    def get_tasks(self) -> list[Task]:
        return [Task(1, "a"), Task(2, "b", 1, "processing"), Task(3, "c", 1, "complete")]


class PreparedSource:
    def __init__(self, tasks: list[Task]) -> None:
        self._tasks = tasks

    def get_tasks(self) -> list[Task]:
        return self._tasks


def test_task_queue_interact_adds_tasks_from_sources() -> None:
    async def run() -> tuple[bool, int, list[int]]:
        interactor = TaskQueueInteract(TaskQueue([]))
        count = await interactor.add_tasks_from_sources([LocalSource()])  # type: ignore[list-item]
        return (
            isinstance(interactor, TaskQueueInteract),
            count,
            [task.id for task in interactor.get_all_tasks()],
        )

    is_alias, count, ids = asyncio.run(run())

    assert is_alias is True
    assert count == 3
    assert ids == [1, 2, 3]


def test_task_queue_interact_registers_and_uses_executors() -> None:
    async def run() -> tuple[int, list[Task]]:
        interactor = TaskQueueInteract(TaskQueue([]))
        tasks = [
            Task(1, "a", 1, "new"),
            Task(2, "b", 1, "processing"),
            Task(3, "c", 1, "complete"),
        ]
        source = PreparedSource(tasks)
        await interactor.add_tasks_from_sources([source])  # type: ignore[list-item]
        interactor.register_executor(NewTaskHandler())
        interactor.register_executor(ProcessingTaskHandler())
        processed = await interactor.process_tasks()
        return processed, tasks

    processed, tasks = asyncio.run(run())

    assert processed == 2
    assert [task.status for task in tasks] == ["processing", "complete", "complete"]


def test_task_queue_interact_raises_for_bad_source() -> None:
    async def run() -> None:
        interactor = TaskQueueInteract(TaskQueue([]))
        await interactor.add_tasks_from_sources([BadSource()])  # type: ignore[list-item]

    with pytest.raises(TypeError):
        asyncio.run(run())


def test_task_queue_interact_raises_for_bad_executor() -> None:
    interactor = TaskQueueInteract(TaskQueue([]))

    with pytest.raises(TypeError):
        interactor.register_executor("bad")  # type: ignore[arg-type]


def test_handlers_match_executor_protocol() -> None:
    assert isinstance(NewTaskHandler(), TaskExecutor)
    assert isinstance(ProcessingTaskHandler(), TaskExecutor)
