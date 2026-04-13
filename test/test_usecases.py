import asyncio

import pytest

from src.domain.task import Task
from src.domain.task_queue import TaskQueue
from src.usecases.task_handlers import (
    CompleteTaskHandler,
    NewTaskHandler,
    ProcessingTaskHandler,
)
from src.usecases.task_interact import TaskInteract, TaskQueueInteract


class BadSource:
    pass


def test_task_queue_interact_adds_tasks_from_sources() -> None:
    interactor = TaskQueueInteract(TaskQueue([]))

    class LocalSource:
        def get_tasks(self) -> list[Task]:
            return [Task(1, "a"), Task(2, "b")]

    count = interactor.add_tasks_from_sources([LocalSource()])  # type: ignore[list-item]

    assert isinstance(interactor, TaskInteract)
    assert count == 2
    assert [task.id for task in interactor.get_all_tasks()] == [1, 2]


def test_task_queue_interact_raises_for_bad_source() -> None:
    interactor = TaskQueueInteract(TaskQueue([]))

    with pytest.raises(TypeError):
        interactor.add_tasks_from_sources([BadSource()])  # type: ignore[list-item]


def test_task_queue_interact_processes_tasks_with_handlers() -> None:
    interactor = TaskQueueInteract(
        TaskQueue(
            [
                Task(1, "a", 1, "new"),
                Task(2, "b", 1, "processing"),
                Task(3, "c", 1, "complete"),
            ]
        )
    )

    processed = asyncio.run(
        interactor.process_tasks_with_handlers(
            [
                NewTaskHandler(),
                ProcessingTaskHandler(),
                CompleteTaskHandler(),
            ]
        )
    )

    tasks = list(interactor.get_all_tasks())
    assert processed == 3
    assert tasks[0].status == "processing"
    assert tasks[1].status == "complete"
    assert tasks[2].status == "complete"
