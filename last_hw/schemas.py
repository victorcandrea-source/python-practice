"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class TaskCreateRequest(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, description="Task title")
    owner: str = Field(..., min_length=1, description="Task owner")
    description: Optional[str] = Field(
        default="", description="Task description"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Fix bug in login",
                "owner": "Alice",
                "description": "Update authentication logic",
            }
        }
    )


class TaskPatchRequest(BaseModel):
    """Schema for partially updating a task."""

    title: Optional[str] = Field(None, min_length=1, description="Task title")
    owner: Optional[str] = Field(None, min_length=1, description="Task owner")
    description: Optional[str] = Field(None, description="Task description")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated title",
                "description": "Updated description",
            }
        }
    )


class TaskStatusChangeRequest(BaseModel):
    """Schema for changing task status."""

    new_status: str = Field(..., min_length=1, description="New task status")

    model_config = ConfigDict(
        json_schema_extra={"example": {"new_status": "in_progress"}}
    )


class TaskResponse(BaseModel):
    """Schema for task response in API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    owner: str = Field(..., description="Task owner")
    description: str = Field(..., description="Task description")
    status: str = Field(..., description="Task status")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Fix bug in login",
                "owner": "Alice",
                "description": "Update authentication logic",
                "status": "in_progress",
                "created_at": "2026-03-30T10:00:00",
                "updated_at": "2026-03-30T10:15:00",
            }
        }
    )
