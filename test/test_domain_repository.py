import pytest
from datetime import datetime, timedelta
from pathlib import Path

from src.domain.task import Task
from src.domain.protocols import TaskSource
from src.domain.exceptions import (
    IncorrectTaskId,
    EmptyTaskPayload,
    IncorrectTaskPriority,
    IncorrectTaskStatus,
)
from src.repository.task_generator import TaskGenerator
from src.repository.task_file import FileSource
from src.repository.task_api import TaskAPI


@pytest.fixture
def tasks_file_path() -> Path:
    return Path("source/tasks.jsonl")


@pytest.fixture
def real_tasks(tasks_file_path) -> list[Task]:
    file_source = FileSource(str(tasks_file_path))
    return list(file_source.get_tasks())


class TestTaskValidation:
    def test_valid_task_creation(self):
        task = Task(id=1, payload="Тестовая задача", priority=3, status="new")
        assert task.id == 1
        assert task.payload == "Тестовая задача"
        assert task.priority == 3
        assert task.status == "new"
        assert isinstance(task.creation_time, datetime)
        assert isinstance(task.living_time, timedelta)

    def test_task_with_real_data(self, real_tasks):
        assert len(real_tasks) == 10
        for task in real_tasks:
            assert isinstance(task.id, int)
            assert isinstance(task.payload, str)
            assert task.priority == 1
            assert task.status == "new"

    def test_id_must_be_int(self):
        with pytest.raises(TypeError, match="целым числом"):
            Task(id="1", payload="test")

    def test_id_must_be_positive(self):
        with pytest.raises(IncorrectTaskId, match="натуральным"):
            Task(id=0, payload="test")

    def test_payload_must_be_str(self):
        with pytest.raises(TypeError, match="строкой"):
            Task(id=1, payload=123)

    def test_payload_cannot_be_none(self):
        with pytest.raises(EmptyTaskPayload, match="Описание задачи не может быть пустым"):
            Task(id=1, payload=None)

    def test_priority_must_be_int(self):
        with pytest.raises(TypeError):
            Task(id=1, payload="test", priority="3")

    def test_priority_must_be_positive(self):
        with pytest.raises(IncorrectTaskPriority):
            Task(id=1, payload="test", priority=0)

    def test_priority_can_be_changed(self):
        task = Task(id=1, payload="test", priority=2)
        task.priority = 5
        assert task.priority == 5

    def test_status_must_be_str(self):
        with pytest.raises(TypeError, match="строкой"):
            Task(id=1, payload="test", status=123)

    def test_status_must_be_valid(self):
        with pytest.raises(IncorrectTaskStatus, match="Несуществующий статус"):
            Task(id=1, payload="test", status="invalid_status")

    def test_valid_statuses(self):
        for status in ["new", "processing", "complete"]:
            task = Task(id=1, payload="test", status=status)
            assert task.status == status

    def test_status_can_be_changed(self):
        task = Task(id=1, payload="test", status="new")
        task.status = "processing"
        assert task.status == "processing"

    def test_creation_time_immutable(self):
        task = Task(id=1, payload="test")
        with pytest.raises(AttributeError):
            task.creation_time = datetime.now()

    def test_living_time_increases(self):
        task = Task(id=1, payload="test")
        time1 = task.living_time
        time2 = task.living_time
        assert time2 > time1


class TestTaskGenerator:
    def test_generator_returns_correct_count(self):
        generator = TaskGenerator(5)
        tasks = list(generator.get_tasks())
        assert len(tasks) == 5

    def test_generator_returns_tasks(self):
        generator = TaskGenerator(3)
        for task in generator.get_tasks():
            assert isinstance(task, Task)

    def test_generator_increments_id(self):
        TaskGenerator._id = 1
        generator = TaskGenerator(3)
        tasks = list(generator.get_tasks())
        assert tasks[0].id == 1
        assert tasks[1].id == 2
        assert tasks[2].id == 3

    def test_generator_sets_random_priority(self):
        generator = TaskGenerator(10)
        priorities = [task.priority for task in generator.get_tasks()]
        assert all(1 <= p <= 5 for p in priorities)
        assert len(set(priorities)) > 1

    def test_generator_uses_texts_from_list(self):
        generator = TaskGenerator(1)
        task = next(generator.get_tasks())
        assert task.payload in TaskGenerator.TEXTS


class TestFileSource:
    def test_file_source_reads_all_tasks(self, real_tasks):
        assert len(real_tasks) == 10

    def test_file_source_correct_ids(self, real_tasks):
        expected_ids = list(range(1, 11))
        actual_ids = [task.id for task in real_tasks]
        assert actual_ids == expected_ids

    def test_file_source_correct_payloads(self, real_tasks):
        expected_payloads = [
            "Исправить баг с гусем, который съел дедлайн",
            "Написать тесты для гусиного дозора",
            "Добавить функционал кормления гусей в прод",
            "Починить гуся, украл ноутбук у разработчика",
            "Разблокировать вход в офис от стаи гусей",
            "Переписать говнокод, который написал гусь",
            "Освободить серверную от захвативших ее гусей",
            "Провести ревью кода, пока гусь не ущипнул",
            "Задеплоить фикс после гусиного переполоха",
            "Восстановить документацию, съеденную гусем"
        ]
        actual_payloads = [task.payload for task in real_tasks]
        assert actual_payloads == expected_payloads

    def test_file_source_default_priority(self, real_tasks):
        for task in real_tasks:
            assert task.priority == 1

    def test_file_source_default_status(self, real_tasks):
        for task in real_tasks:
            assert task.status == "new"

    def test_file_source_file_not_found(self):
        file_source = FileSource("nonexistent.jsonl")
        with pytest.raises(FileNotFoundError):
            list(file_source.get_tasks())


class TestTaskAPI:
    def test_api_returns_three_tasks(self):
        api = TaskAPI()
        tasks = list(api.get_tasks())
        assert len(tasks) == 3

    def test_api_returns_tasks_with_correct_ids(self):
        api = TaskAPI()
        tasks = list(api.get_tasks())
        assert tasks[0].id == 100001
        assert tasks[1].id == 100002
        assert tasks[2].id == 100003

    def test_api_returns_tasks_with_correct_payloads(self):
        api = TaskAPI()
        tasks = list(api.get_tasks())
        assert tasks[0].payload == "Мяукнуть"
        assert tasks[1].payload == "Гавкнуть"
        assert tasks[2].payload == "Гоготнуть"

    def test_api_sets_different_priorities(self):
        api = TaskAPI()
        tasks = list(api.get_tasks())
        assert tasks[0].priority == 1
        assert tasks[1].priority == 4
        assert tasks[2].priority == 5

    def test_api_sets_default_status(self):
        api = TaskAPI()
        tasks = list(api.get_tasks())
        for task in tasks:
            assert task.status == "new"


class TestTaskSourceProtocol:
    def test_task_generator_implements_protocol(self):
        assert isinstance(TaskGenerator(1), TaskSource)

    def test_file_source_implements_protocol(self, tasks_file_path):
        assert isinstance(FileSource(str(tasks_file_path)), TaskSource)

    def test_task_api_implements_protocol(self):
        assert isinstance(TaskAPI(), TaskSource)

    def test_all_sources_return_tasks(self, tasks_file_path):
        sources = [
            TaskGenerator(2),
            FileSource(str(tasks_file_path)),
            TaskAPI()
        ]
        for source in sources:
            tasks = list(source.get_tasks())
            assert len(tasks) > 0
            assert all(isinstance(t, Task) for t in tasks)


class TestExceptions:
    def test_exceptions_inheritance(self):
        from src.domain.exceptions import (
            TaskException,
            IncorrectTaskId,
            EmptyTaskPayload,
            IncorrectTaskPriority,
            IncorrectTaskStatus,
        )
        assert issubclass(IncorrectTaskId, TaskException)
        assert issubclass(EmptyTaskPayload, TaskException)
        assert issubclass(IncorrectTaskPriority, TaskException)
        assert issubclass(IncorrectTaskStatus, TaskException)

    def test_exceptions_can_be_raised_and_caught(self):
        from src.domain.exceptions import TaskException
        with pytest.raises(TaskException):
            raise IncorrectTaskId()
        with pytest.raises(TaskException):
            raise EmptyTaskPayload()
        with pytest.raises(TaskException):
            raise IncorrectTaskPriority()
        with pytest.raises(TaskException):
            raise IncorrectTaskStatus()