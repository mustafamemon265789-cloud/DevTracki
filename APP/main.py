from fastapi import FastAPI, Depends
from app.database import create_db_and_tables
from app.models.user import User, UserRead
from app.models.project import Project
from app.models.task import Task, Comment
from app.router import auth, project, tasks
from app.core.dependencies import get_current_user

app = FastAPI(
    title="DevTrack API",
    description="API for DevTrack, a project management tool for developers and teams to track their projects and tasks",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(project.router)
app.include_router(tasks.router)

@app.on_event("startup")
def on_startup():
    # Create all database tables on startup
    create_db_and_tables()
    print("Tables Created Successfully")

@app.get("/")
def root():
    return {"message": "Welcome To DevTrack API"}

@app.get("/users/me", response_model=UserRead, tags=["Users"])
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user
