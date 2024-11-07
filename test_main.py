import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app, get_db

# Erstelle eine Testdatenbank (SQLite)
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Überschreibe die get_db-Abhängigkeit, um die Testdatenbank zu verwenden
def get_test_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Anwenden der Überschreibung
app.dependency_overrides[get_db] = get_test_db

# Erstelle die Tabellen in der Testdatenbank
Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_db():
    # Tabellen erstellen
    Base.metadata.create_all(bind=engine)
    yield
    # Tabellen nach dem Test löschen
    Base.metadata.drop_all(bind=engine)

# Verbesserte Dokumentation und erweiterte Testfälle

# Testfälle für die Registrierung

def test_register_user_success(setup_db):
    """
    Testet eine erfolgreiche Benutzerregistrierung.
    Überprüft, ob ein neuer Benutzer registriert werden kann und die Antwort die richtigen Benutzerdaten enthält.
    """
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

def test_register_user_duplicate_username(setup_db):
    """
    Testet die Registrierung mit einem doppelten Benutzernamen.
    Überprüft, ob die Registrierung mit einem bereits vorhandenen Benutzernamen einen entsprechenden Fehler zurückgibt.
    """
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
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "newuser@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_register_user_duplicate_email(setup_db):
    """
    Testet die Registrierung mit einer doppelten E-Mail-Adresse.
    Überprüft, ob die Registrierung mit einer bereits vorhandenen E-Mail-Adresse einen entsprechenden Fehler zurückgibt.
    """
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
    response = client.post(
        "/register",
        json={
            "username": "newuser",
            "email": "testuser@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

# Tests für den Login-Endpunkt
def test_login_user_success(setup_db):
    """
    Testet einen erfolgreichen Benutzer-Login.
    Überprüft, ob ein registrierter Benutzer sich einloggen und einen gültigen Zugriffstoken erhalten kann.
    """
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
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_user_invalid_password(setup_db):
    """
    Testet den Login mit einem ungültigen Passwort.
    Überprüft, ob ein falsches Passwort einen entsprechenden Fehler zurückgibt.
    """
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
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

# Tests für den geschützten Endpunkt `/users/me`
def test_read_users_me_success(setup_db):
    """
    Testet den Zugriff auf den geschützten Endpunkt `/users/me` mit einem gültigen Token.
    Überprüft, ob der Endpunkt die richtigen Benutzerdaten zurückgibt.
    """
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

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_read_users_me_unauthorized(setup_db):
    """
    Testet den Zugriff auf den geschützten Endpunkt `/users/me` ohne Token.
    Überprüft, ob der Endpunkt einen Unauthorized-Fehler zurückgibt.
    """
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# Health-Check-Test
def test_health_check():
    """
    Testet den Endpunkt `/health`, um sicherzustellen, dass der Dienst ordnungsgemäß läuft.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# Test für die Home-Route
def test_home_route():
    """
    Testet die Home-Route, um sicherzustellen, dass die index.html korrekt zurückgegeben wird.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

# Bereinigung nach allen Tests
@pytest.fixture(scope="session", autouse=True)
def teardown_db():
    yield
    Base.metadata.drop_all(bind=engine)
