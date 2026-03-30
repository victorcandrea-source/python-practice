"""
FastAPI application for Task Management System.
Provides RESTful endpoints for task operations.
"""

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging

from config import APP_TITLE, APP_VERSION, APP_DESCRIPTION
from schemas import (
    TaskCreateRequest,
    TaskResponse,
    TaskPatchRequest,
    TaskStatusChangeRequest,
)
from task_system import get_task_manager
from exceptions import (
    TaskNotFoundError,
    InvalidStatusTransitionError,
    InvalidInputError,
    DatabaseError,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)


# ==========================================
# Exception Handlers (Centralized)
# ==========================================


@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request, exc):
    """Handle TaskNotFoundError -> 404."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidStatusTransitionError)
async def invalid_status_transition_handler(request, exc):
    """Handle InvalidStatusTransitionError -> 409."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidInputError)
async def invalid_input_handler(request, exc):
    """Handle InvalidInputError -> 422."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


@app.exception_handler(DatabaseError)
async def database_error_handler(request, exc):
    """Handle DatabaseError -> 500."""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database operation failed."},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Catch-all for unexpected errors -> 500."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )


# ==========================================
# Health Check Endpoint
# ==========================================


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        Status of the application and database.
    """
    try:
        manager = get_task_manager()
        return {"status": "ok", "message": "Task Management System is running."}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "detail": "Database connection failed."},
        )


# ==========================================
# Task Endpoints (RESTful)
# ==========================================


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
)
async def create_task(payload: TaskCreateRequest):
    """
    Create a new task.

    Args:
        payload: TaskCreateRequest with title, owner, and optional description.

    Returns:
        TaskResponse (201 Created): The newly created task.

    Raises:
        422: If validation fails (missing/empty required fields).
        500: If database operation fails.
    """
    manager = get_task_manager()
    new_task = manager.create_task(
        title=payload.title,
        owner=payload.owner,
        description=payload.description or "",
    )
    logger.info(f"Task created: {new_task['id']}")
    return new_task


@app.get("/tasks", response_model=List[TaskResponse], tags=["Tasks"])
async def list_tasks(
    task_status: Optional[str] = None,
    owner: Optional[str] = None,
    sort_by: str = "id",
):
    """
    List all tasks with optional filtering and sorting.

    Args:
        task_status: Filter by task status (optional).
        owner: Filter by task owner (optional).
        sort_by: Field to sort by (default: 'id'). Valid: id, title, owner, status, created_at.

    Returns:
        List[TaskResponse]: Array of task objects.

    Raises:
        500: If database operation fails.
    """
    manager = get_task_manager()
    tasks = manager.list_tasks(
        filter_status=task_status, filter_owner=owner, sort_by=sort_by
    )
    logger.info(f"Listed {len(tasks)} tasks")
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(task_id: int):
    """
    Get a specific task by ID.

    Args:
        task_id: The ID of the task to retrieve.

    Returns:
        TaskResponse: The requested task.

    Raises:
        404: If task not found.
        500: If database operation fails.
    """
    manager = get_task_manager()
    task = manager.get_task_by_id(task_id)
    logger.info(f"Retrieved task {task_id}")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def patch_task(task_id: int, payload: TaskPatchRequest):
    """
    Partially update a task (PATCH).

    All fields are optional, but at least one must be provided.
    Cannot update tasks in terminal statuses (canceled, blocked).

    Args:
        task_id: The ID of the task to update.
        payload: TaskPatchRequest with optional title, owner, description.

    Returns:
        TaskResponse: The updated task.

    Raises:
        404: If task not found.
        422: If no fields provided or task in terminal status.
        500: If database operation fails.
    """
    manager = get_task_manager()
    updated_task = manager.update_task(
        task_id=task_id,
        title=payload.title,
        owner=payload.owner,
        description=payload.description,
    )
    logger.info(f"Updated task {task_id}")
    return updated_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
async def delete_task(task_id: int):
    """
    Delete a task.

    Cannot delete tasks in terminal statuses (canceled, blocked).

    Args:
        task_id: The ID of the task to delete.

    Returns:
        204 No Content: If deletion successful.

    Raises:
        404: If task not found.
        422: If task in terminal status.
        500: If database operation fails.
    """
    manager = get_task_manager()
    manager.delete_task(task_id)
    logger.info(f"Deleted task {task_id}")
    return None


@app.post(
    "/tasks/{task_id}/status", response_model=TaskResponse, tags=["Tasks"]
)
async def change_task_status(task_id: int, payload: TaskStatusChangeRequest):
    """
    Change task status (workflow transition).

    Enforces workflow rules:
    - Cannot transition from terminal statuses (canceled, blocked).
    - Status must be one of: todo, in_progress, done, canceled, blocked.

    Args:
        task_id: The ID of the task.
        payload: TaskStatusChangeRequest with new_status.

    Returns:
        TaskResponse: The task with updated status.

    Raises:
        404: If task not found.
        409: If status transition is invalid (from terminal status).
        422: If new_status is invalid.
        500: If database operation fails.
    """
    manager = get_task_manager()
    updated_task = manager.change_status(
        task_id=task_id, new_status=payload.new_status
    )
    logger.info(f"Changed task {task_id} status to {payload.new_status}")
    return updated_task


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
