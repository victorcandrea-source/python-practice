"""
Custom exception classes for Task API
"""


class TaskNotFoundError(Exception):
    """Raised when a task is not found"""
    pass


class InvalidStatusTransitionError(Exception):
    """Raised when a task status transition is invalid"""
    pass


class InvalidInputError(Exception):
    """Raised when input validation fails"""
    pass
