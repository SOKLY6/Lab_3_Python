from pathlib import Path

import questionary
import typer

from src.domain.task import Task
from src.logger.logger import get_logger
from src.repository.task_api import TaskAPI
from src.repository.task_file import FileSource
from src.repository.task_generator import TaskGenerator
from src.repository.task_storage import TaskStorage
from src.usecases.task_interact import TaskInteract

logger = get_logger(__name__)

app = typer.Typer()


def print_tasks(tasks: list[Task]) -> None:
    """Вывод задач в формате id: payload"""
    if not tasks:
        typer.echo("Задач нет")
        return

    typer.echo("\nТЕКУЩИЕ ЗАДАЧИ:")
    for task in tasks:
        typer.echo(f"{task.id}: {task.payload}")
    typer.echo(f"Всего задач: {len(tasks)}\n")


@app.callback(invoke_without_command=True)
def cli() -> None:
    """CLI для управления задачами"""
    task_interactor = TaskInteract(TaskStorage())

    while True:
        try:
            choice = questionary.select(
                "Выберите действие:",
                choices=[
                    "Загрузить задачи из файла",
                    "Сгенерировать задачи",
                    "Загрузить задачи из API",
                    "Показать все задачи",
                    "Выход из программы",
                ],
            ).ask()

            if choice == "Загрузить задачи из файла":
                file_path = Path("source/tasks.jsonl")

                if not file_path.exists():
                    logger.error(f"Файл не найден: {file_path}")
                    typer.echo("Файл не найден")
                    continue

                try:
                    file_source = FileSource(str(file_path))
                    tasks_count = task_interactor.add_tasks_from_source(
                        file_source
                    )
                    logger.info(
                        f"Загружено {tasks_count} задач из файла {file_path}"
                    )
                    typer.echo(f"Загружено {tasks_count} задач")
                except Exception as e:
                    logger.exception(f"Ошибка: {e}")
                    typer.echo("Ошибка обработки файла")

            elif choice == "Сгенерировать задачи":
                tasks_count = questionary.text(
                    "Количество задач для генерации:",
                ).ask()

                while not tasks_count or not tasks_count.isdigit():
                    typer.echo("Некорректное число")
                    continue

                try:
                    tasks_count = int(tasks_count)
                    generator = TaskGenerator(tasks_count)
                    tasks_count = task_interactor.add_tasks_from_source(
                        generator
                    )
                    logger.info(f"Сгенерировано {tasks_count} задач")
                    typer.echo(f"Сгенерировано {tasks_count} задач")
                except Exception as e:
                    logger.exception(f"Ошибка: {e}")
                    typer.echo("Ошибка генерации")

            elif choice == "Загрузить задачи из API":
                try:
                    api = TaskAPI()
                    tasks_count = task_interactor.add_tasks_from_source(api)
                    logger.info(f"Загружено {tasks_count} задач из API")
                    typer.echo(f"Загружено {tasks_count} задач")
                except Exception as e:
                    logger.exception(f"Ошибка: {e}")
                    typer.echo("Ошибка загрузки")

            elif choice == "Показать все задачи":
                try:
                    tasks = task_interactor.get_all_tasks()
                    logger.info(f"Просмотр задач: всего {len(tasks)}")
                    print_tasks(tasks)
                except Exception as e:
                    logger.exception(f"Ошибка: {e}")
                    typer.echo("Ошибка")

            elif choice == "Выход из программы":
                logger.info("Программа завершена")
                typer.echo("Выход из программы")
                break

        except KeyboardInterrupt:
            logger.info("Программа прервана пользователем")
            typer.echo("\nВыход из программы")
            break
        except Exception as e:
            logger.exception(f"Ошибка: {e}")
            typer.echo(f"Ошибка: {e}")
