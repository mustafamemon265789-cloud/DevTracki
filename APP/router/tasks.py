from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.task import Task, TaskRead, Comment, CommentCreate, CommentRead
from app.models.project import Project
from app.core.dependencies import get_current_user
from app.models.user import User
from app.database import get_session

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific task by ID"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if user owns the project or is assigned to task
    project = session.get(Project, task.project_id)
    if project.owner_id != current_user.id and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")

    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    assignee_id: int | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = session.get(Project, task.project_id)
    if current_user.id != project.owner_id and current_user.id != task.assignee_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
        
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if priority is not None:
        task.priority = priority
    if status is not None:
        task.status = status  # todo | in_progress | done
    if assignee_id is not None:
        task.assignee_id = assignee_id

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    project = session.get(Project, task.project_id)

    if current_user.id != project.owner_id and current_user.id != task.assignee_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")

    session.delete(task)
    session.commit()
    return None


# ===== COMMENTS UNDER TASKS =====

@router.post("/{task_id}/comments", response_model=CommentRead, status_code=201)
def create_comment(
    task_id: int,
    comment_in: CommentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Add a comment to a task"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    comment = Comment(
        comment=comment_in.comment,
        task_id=task_id,
        author_id=current_user.id
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


@router.get("/{task_id}/comments", response_model=list[CommentRead])
def list_comments(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    comments = session.exec(
        select(Comment).where(Comment.task_id == task_id)
    ).all()
    return comments
