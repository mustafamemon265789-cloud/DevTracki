from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = Field(default="medium")
    status: str = Field(default="todo")


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    assignee_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskBase):
    assignee_id: Optional[int] = None


class TaskRead(TaskBase):
    id: int
    project_id: int
    created_at: datetime


# Comments


class CommentBase(SQLModel):
    comment: str


class Comment(CommentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    author_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CommentCreate(CommentBase):
    pass


class CommentRead(CommentBase):
    id: int
    task_id: int
    author_id: int
    created_at: datetime
