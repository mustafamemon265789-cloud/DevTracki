import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_session
from app.config import settings

# Create test database in memory
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def get_test_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = get_test_session

client = TestClient(app)

# Test fixtures
@pytest.fixture(scope="module")
def test_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def auth_headers(test_db):
    """Register and login to get auth token"""
    # Register
    register_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    client.post("/auth/register", json=register_data)

    # Login
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


class TestAuth:
    """Test Authentication System (Phase 2)"""

    def test_register_user(self, test_db):
        """Test user registration"""
        data = {
            "name": "New User",
            "email": "new@example.com",
            "password": "password123"
        }
        response = client.post("/auth/register", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == "New User"
        assert result["email"] == "new@example.com"
        assert "id" in result

    def test_login_user(self, test_db):
        """Test user login returns JWT token"""
        # Register first
        register_data = {
            "name": "Login User",
            "email": "login@example.com",
            "password": "loginpass123"
        }
        client.post("/auth/register", json=register_data)

        # Login
        login_data = {
            "username": "login@example.com",
            "password": "loginpass123"
        }
        response = client.post("/auth/login", data=login_data)
        assert response.status_code == 200
        result = response.json()
        assert "access_token" in result
        assert result["token_type"] == "bearer"

    def test_get_current_user(self, auth_headers, test_db):
        """Test getting current user profile"""
        response = client.get("/users/me", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert result["email"] == "test@example.com"


class TestProjects:
    """Test Project Management (Phase 3)"""

    def test_create_project(self, auth_headers, test_db):
        """Test creating a project"""
        data = {
            "name": "Test Project",
            "description": "A test project",
            "status": "active"
        }
        response = client.post("/projects/", json=data, headers=auth_headers)
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == "Test Project"
        assert result["description"] == "A test project"
        assert "id" in result

    def test_list_projects(self, auth_headers, test_db):
        """Test listing projects"""
        response = client.get("/projects/", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)

    def test_get_project(self, auth_headers, test_db):
        """Test getting a specific project"""
        # Create project first
        data = {"name": "Single Project", "description": "Test", "status": "active"}
        create_response = client.post("/projects/", json=data, headers=auth_headers)
        project_id = create_response.json()["id"]

        # Get project
        response = client.get(f"/projects/{project_id}", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "Single Project"

    def test_update_project(self, auth_headers, test_db):
        """Test updating a project"""
        # Create project
        data = {"name": "Update Project", "description": "Old desc", "status": "active"}
        create_response = client.post("/projects/", json=data, headers=auth_headers)
        project_id = create_response.json()["id"]

        # Update project
        update_data = {"name": "Updated Name", "description": "New desc", "status": "completed"}
        response = client.put(f"/projects/{project_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "Updated Name"
        assert result["status"] == "completed"

    def test_delete_project(self, auth_headers, test_db):
        """Test deleting a project"""
        # Create project
        data = {"name": "Delete Project", "description": "To delete", "status": "active"}
        create_response = client.post("/projects/", json=data, headers=auth_headers)
        project_id = create_response.json()["id"]

        # Delete project
        response = client.delete(f"/projects/{project_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/projects/{project_id}", headers=auth_headers)
        assert get_response.status_code == 404


class TestTasks:
    """Test Task & Comment System (Phase 4)"""

    @pytest.fixture
    def project_with_task(self, auth_headers, test_db):
        """Create a project and return its ID"""
        data = {"name": "Task Project", "description": "For tasks", "status": "active"}
        response = client.post("/projects/", json=data, headers=auth_headers)
        return response.json()["id"]

    def test_create_task(self, auth_headers, project_with_task, test_db):
        """Test creating a task in a project"""
        project_id = project_with_task
        data = {
            "title": "Test Task",
            "description": "Task description",
            "priority": "high",
            "status": "todo"
        }
        response = client.post(f"/projects/{project_id}/tasks", json=data, headers=auth_headers)
        assert response.status_code == 201
        result = response.json()
        assert result["title"] == "Test Task"
        assert result["priority"] == "high"
        assert result["project_id"] == project_id

    def test_list_tasks(self, auth_headers, project_with_task, test_db):
        """Test listing tasks in a project"""
        project_id = project_with_task

        # Create task
        data = {"title": "List Task", "priority": "medium", "status": "todo"}
        client.post(f"/projects/{project_id}/tasks", json=data, headers=auth_headers)

        # List tasks
        response = client.get(f"/projects/{project_id}/tasks", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_list_tasks_with_status_filter(self, auth_headers, project_with_task, test_db):
        """Test filtering tasks by status"""
        project_id = project_with_task

        # Create tasks with different statuses
        client.post(f"/projects/{project_id}/tasks",
                   json={"title": "Todo Task", "status": "todo"},
                   headers=auth_headers)
        client.post(f"/projects/{project_id}/tasks",
                   json={"title": "Done Task", "status": "done"},
                   headers=auth_headers)

        # Filter by status
        response = client.get(f"/projects/{project_id}/tasks?status=done", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert all(task["status"] == "done" for task in result)

    def test_update_task_status(self, auth_headers, project_with_task, test_db):
        """Test updating task status"""
        project_id = project_with_task

        # Create task
        data = {"title": "Update Task", "status": "todo"}
        create_response = client.post(f"/projects/{project_id}/tasks", json=data, headers=auth_headers)
        task_id = create_response.json()["id"]

        # Update status
        response = client.put(f"/tasks/{task_id}?status=in_progress", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "in_progress"

    def test_create_comment(self, auth_headers, project_with_task, test_db):
        """Test adding a comment to a task"""
        project_id = project_with_task

        # Create task
        task_data = {"title": "Comment Task", "status": "todo"}
        task_response = client.post(f"/projects/{project_id}/tasks", json=task_data, headers=auth_headers)
        task_id = task_response.json()["id"]

        # Add comment
        comment_data = {"comment": "This is a test comment"}
        response = client.post(f"/tasks/{task_id}/comments", json=comment_data, headers=auth_headers)
        assert response.status_code == 201
        result = response.json()
        assert result["comment"] == "This is a test comment"
        assert result["task_id"] == task_id

    def test_list_comments(self, auth_headers, project_with_task, test_db):
        """Test listing comments on a task"""
        project_id = project_with_task

        # Create task
        task_data = {"title": "Comment Task 2", "status": "todo"}
        task_response = client.post(f"/projects/{project_id}/tasks", json=task_data, headers=auth_headers)
        task_id = task_response.json()["id"]

        # Add comment
        client.post(f"/tasks/{task_id}/comments",
                   json={"comment": "First comment"},
                   headers=auth_headers)

        # List comments
        response = client.get(f"/tasks/{task_id}/comments", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1


class TestAuthProtection:
    """Test protected endpoints require authentication"""

    def test_protected_endpoints_require_auth(self, test_db):
        """Test that protected endpoints return 401 without token"""
        endpoints = [
            ("GET", "/users/me"),
            ("GET", "/projects/"),
            ("POST", "/projects/", {"name": "Test", "status": "active"}),
        ]

        for method, url, *body in endpoints:
            kwargs = {}
            if body:
                kwargs["json"] = body[0]

            if method == "GET":
                response = client.get(url, **kwargs)
            elif method == "POST":
                response = client.post(url, **kwargs)
            else:
                continue

            assert response.status_code == 401, f"{method} {url} should require auth"
