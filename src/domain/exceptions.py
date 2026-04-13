class TaskException(Exception):
    """Базовая ошибка"""


class IncorrectTaskId(TaskException):
    """Ошибка id"""


class EmptyTaskPayload(TaskException):
    """Ошибка payload"""


class IncorrectTaskPriority(TaskException):
    """Ошибка приоритета"""


class IncorrectTaskStatus(TaskException):
    """Ошибка статуса"""
