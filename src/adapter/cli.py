import asyncio
from pathlib import Path

import questionary
import typer

from src.domain.task import Task
from src.domain.task_queue import TaskQueue
from src.logger.logger import get_logger
from src.repository.task_api import TaskAPI
from src.repository.task_file import FileSource
from src.repository.task_generator import TaskGenerator
from src.usecases.task_handlers import NewTaskHandler, ProcessingTaskHandler
from src.usecases.task_interact import TaskQueueInteract

logger = get_logger(__name__)

app = typer.Typer()


def print_tasks(tasks: list[Task]) -> None:
    """Печатает задачи"""
    if not tasks:
        typer.echo("Задач нет")
        return

    typer.echo("\nТЕКУЩИЕ ЗАДАЧИ:")
    for task in tasks:
        typer.echo(f"{task.id}: {task.payload} [{task.status}]")
    typer.echo(f"Всего задач: {len(tasks)}\n")


@app.callback(invoke_without_command=True)
def cli() -> None:
    """Запускает меню"""
    task_interactor = TaskQueueInteract(TaskQueue([]))
    task_interactor.register_executor(NewTaskHandler())
    task_interactor.register_executor(ProcessingTaskHandler())

    while True:
        try:
            choice = questionary.select(
                "Выберите действие:",
                choices=[
                    "Загрузить задачи из файла",
                    "Сгенерировать задачи",
                    "Загрузить задачи из API",
                    "Показать все задачи",
                    "Асинхронно обработать очередь",
                    "Выход из программы",
                ],
            ).ask()

            if choice == "Загрузить задачи из файла":
                file_path = Path("source/tasks.jsonl")
                if not file_path.exists():
                    logger.error("Файл не найден: %s", file_path)
                    typer.echo("Файл не найден")
                    continue

                try:
                    file_source = FileSource(str(file_path))
                    tasks_count = asyncio.run(
                        task_interactor.add_tasks_from_sources([file_source])
                    )
                    typer.echo(f"Загружено {tasks_count} задач")
                except Exception as error:
                    logger.exception("Ошибка: %s", error)
                    typer.echo("Ошибка обработки файла")

            elif choice == "Сгенерировать задачи":
                tasks_count = questionary.text(
                    "Количество задач для генерации:",
                ).ask()

                while not tasks_count or not tasks_count.isdigit():
                    typer.echo("Некорректное число")
                    tasks_count = questionary.text(
                        "Количество задач для генерации:",
                    ).ask()

                try:
                    generator = TaskGenerator(int(tasks_count))
                    created = asyncio.run(
                        task_interactor.add_tasks_from_sources([generator])
                    )
                    typer.echo(f"Сгенерировано {created} задач")
                except Exception as error:
                    logger.exception("Ошибка: %s", error)
                    typer.echo("Ошибка генерации")

            elif choice == "Загрузить задачи из API":
                try:
                    api = TaskAPI()
                    loaded = asyncio.run(
                        task_interactor.add_tasks_from_sources([api])
                    )
                    typer.echo(f"Загружено {loaded} задач")
                except Exception as error:
                    logger.exception("Ошибка: %s", error)
                    typer.echo("Ошибка загрузки")

            elif choice == "Показать все задачи":
                try:
                    print_tasks(list(task_interactor.get_all_tasks()))
                except Exception as error:
                    logger.exception("Ошибка: %s", error)
                    typer.echo("Ошибка")

            elif choice == "Асинхронно обработать очередь":
                try:
                    processed = asyncio.run(
                        task_interactor.process_tasks(logger=logger)
                    )
                    typer.echo(f"Обработано задач: {processed}")
                except Exception as error:
                    logger.exception("Ошибка: %s", error)
                    typer.echo("Ошибка асинхронной обработки")

            elif choice == "Выход из программы":
                typer.echo("Выход из программы")
                break

        except KeyboardInterrupt:
            typer.echo("\nВыход из программы")
            break
        except Exception as error:
            logger.exception("Ошибка: %s", error)
            typer.echo(f"Ошибка: {error}")
