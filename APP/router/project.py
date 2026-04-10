from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.project import Project
from app.schemas.projects import ProjectCreate, ProjectRead
from app.models.task import Task, TaskCreate, TaskRead, Comment, CommentCreate, CommentRead
from app.core.dependencies import get_current_user
from app.models.user import User
from app.database import get_session

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectRead, status_code=201)
def create_project(
    project_in: ProjectCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    project = Project(
        name=project_in.name,
        description=project_in.description,
        status=project_in.status,
        owner_id = current_user.id
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.get("/", response_model=list[ProjectRead])
def list_projects(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    projects = session.exec(
        select(Project).where(Project.owner_id == current_user.id)
    ).all()
    return projects


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    project = session.get(Project, project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    project_in: ProjectCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    project = session.get(Project, project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    project.name = project_in.name
    project.description = project_in.description
    project.status = project_in.status
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    project = session.get(Project, project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(project)
    session.commit()
    return None


# ===== TASKS UNDER PROJECTS =====

@router.post("/{project_id}/tasks", response_model=TaskRead, status_code=201)
def create_task(
    project_id: int,
    task_in: TaskCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a task in a project"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = Task(
        **task_in.model_dump(),
        project_id=project_id
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/{project_id}/tasks", response_model=list[TaskRead])
def list_tasks(
    project_id: int,
    status: str | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List all tasks in a project with optional status filter"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(Task).where(Task.project_id == project_id)

    if status:
        query = query.where(Task.status == status)

    tasks = session.exec(query).all()
    return tasks
