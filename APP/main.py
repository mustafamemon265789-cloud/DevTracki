from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.models.user import User, UserRead
from app.router import auth, project, tasks
from app.core.dependencies import get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    create_db_and_tables()
    print("Application startup complete")
    yield
    # Shutdown
    print("Application shutting down")

app = FastAPI(
    title="DevTrack API",
    description="API for DevTrack, a project management tool for developers and teams to track their projects and tasks",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(auth.router)
app.include_router(project.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {"message": "Welcome To DevTrack API"}

@app.get("/health")
def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy"}

@app.get("/users/me", response_model=UserRead, tags=["Users"])
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user