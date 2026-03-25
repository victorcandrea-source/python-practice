from task_system import *
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1)
    owner: str = Field(..., min_length=1)
    description: Optional[str] = ""
    

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    owner: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None


class TaskPatchRequest(BaseModel):
    """Partial update request - all fields optional"""
    title: Optional[str] = Field(None, min_length=1)
    owner: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None

class TaskStatusChangeRequest(BaseModel):
    new_status: str = Field(..., min_length=1)


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    owner: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime