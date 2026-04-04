class TaskException(Exception):
    pass


class IncorrectTaskId(TaskException):
    pass


class EmptyTaskPayload(TaskException):
    pass


class IncorrectTaskPriority(TaskException):
    pass


class IncorrectTaskStatus(TaskException):
    pass
