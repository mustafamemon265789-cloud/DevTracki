from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    status: str = "todo"
    assignee_id: Optional[int] = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: str
    status: str
    project_id: int
    assignee_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assignee_id: Optional[int] = None


class CommentCreate(BaseModel):
    comment: str


class CommentRead(BaseModel):
    id: int
    comment: str
    task_id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True
