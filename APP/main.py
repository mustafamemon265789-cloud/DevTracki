from fastapi import FastAPI, Depends
from app.models.user import User, UserRead
from app.models.project import Project
from app.models.task import Task, Comment
from app.routers import auth, projects, tasks
from app.core.dependencies import get_current_user

app = FastAPI(
    title="DevTrack API",
    description="API for DevTrack, a project management tool for developers and teams to track their projects and tasks",
    version="1.0.0"
)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)

@app.on_event("startup")
def on_startup():
    #for db create_tables
    print("Tables Created Successfully")

@app.get("/")
def root():
    return {"message": "Welcome To DevTrack API"}
  
@app.get("/users/me", response_model=UserRead, tags=["Users"])
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user
