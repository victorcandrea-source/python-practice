from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from schemas import (
    TaskCreateRequest, 
    TaskResponse, 
    TaskPatchRequest, 
    TaskStatusChangeRequest
)
from task_system import task_manager
from exceptions import (
    TaskNotFoundError, 
    InvalidStatusTransitionError, 
    InvalidInputError
)
from typing import List, Optional

manager = task_manager()
app = FastAPI(title="TaskManager")


# ==========================================
# Exception Handlers (Centralized)
# ==========================================

@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidStatusTransitionError)
async def invalid_status_transition_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidInputError)
async def invalid_input_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Catch-all for unexpected errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


# ==========================================
# Health Check
# ==========================================

@app.get("/health")
async def health_check():
    return {"status": "ok"}


# ==========================================
# Task Endpoints (RESTful)
# ==========================================

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_endpoint(payload: TaskCreateRequest):
    """
    Create a new task.
    Returns: TaskResponse with 201 Created status
    """
    new_task = manager.create_task(
        title=payload.title,
        owner=payload.owner,
        description=payload.description or ""
    )
    return new_task


@app.get("/tasks", response_model=List[TaskResponse])
async def list_tasks_endpoint(
    task_status: Optional[str] = None,
    owner: Optional[str] = None,
    sort_by: str = "id"
):
    """
    List all tasks with optional filtering and sorting.
    Query params:
      - task_status: filter by status
      - owner: filter by owner
      - sort_by: sort field (id, title, owner, status, created_at)
    """
    return manager.list_tasks(
        filter_status=task_status,
        filter_owner=owner,
        sort_by=sort_by
    )


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_endpoint(task_id: int):
    """
    Get a specific task by ID.
    Raises: TaskNotFoundError → 404
    """
    return manager.get_task_by_id(task_id)


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
async def patch_task_endpoint(task_id: int, payload: TaskPatchRequest):
    """
    Partially update a task (PATCH).
    All fields are optional.
    At least one field must be provided.
    Raises:
      - TaskNotFoundError → 404
      - InvalidInputError → 422 (if no fields provided)
    """
    return manager.update_task(
        task_id=task_id,
        title=payload.title,
        owner=payload.owner,
        description=payload.description
    )


@app.post("/tasks/{task_id}/status", response_model=TaskResponse)
async def change_task_status_endpoint(task_id: int, payload: TaskStatusChangeRequest):
    """
    Change task status.
    Enforces workflow rules (e.g., cannot change from canceled/blocked).
    Raises:
      - TaskNotFoundError → 404
      - InvalidStatusTransitionError → 409
    """
    return manager.change_status(task_id=task_id, new_status=payload.new_status)
