"""
Custom exception classes for Task Management API.
"""


class TaskNotFoundError(Exception):
    """Raised when a task is not found in the database."""

    pass


class InvalidStatusTransitionError(Exception):
    """Raised when a task status transition violates workflow rules."""

    pass


class InvalidInputError(Exception):
    """Raised when input validation fails."""

    pass


class DatabaseError(Exception):
    """Raised when a database operation fails."""

    pass
