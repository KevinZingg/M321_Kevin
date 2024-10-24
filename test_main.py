# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app, get_db  # Import get_db correctly here

# Create a test database (SQLite)
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def get_test_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Apply the override
app.dependency_overrides[get_db] = get_test_db  # Make sure get_db is imported from main.py

# Create the tables in the test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after test
    Base.metadata.drop_all(bind=engine)

# Tests for registration endpoint
def test_register_user(setup_db):
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

# Tests for login endpoint
def test_login_user(setup_db):
    # Register user first
    client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    # Test login
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

# Tests for protected endpoint `/users/me`
def test_read_users_me(setup_db):
    # Register and login to get the token
    client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]

    # Test `/users/me` endpoint
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

# Health check test
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# Home route test
def test_home_route():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

# Cleanup after all tests are run
@pytest.fixture(scope="session", autouse=True)
def teardown_db():
    yield
    Base.metadata.drop_all(bind=engine)
