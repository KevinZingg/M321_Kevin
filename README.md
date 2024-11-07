# Testbericht

## Übersicht

Dieses Dokument dient als Zusammenfassung des Testprotokolls für das Backend des Projekts. Ziel ist es, sicherzustellen, dass die Anwendung die Qualitätsstandards durch automatisierte Unit-Tests und Integrationstests erfüllt. Die folgenden Abschnitte geben Details zur Testumgebung, den verwendeten Tools, den Testergebnissen und allen relevanten Warnungen oder veralteten Funktionen, die während der Tests festgestellt wurden.

## Testumgebung

- **Betriebssystem:** Linux (Ubuntu)
- **Python-Version:** Python 3.10.15
- **Virtuelle Umgebung:** venv
- **Testframework:** Pytest 8.3.3
- **Plugins:** anyio-4.4.0
- **Datenbank:** SQLite (für Testzwecke)

### Projektverzeichnisstruktur



/home/ubuntu/Documents/fastapi
├── README.md
├── __pycache__
├── auth.py
├── cert.pem
├── database.py
├── help.txt
├── key.pem
├── main.py
├── models.py
├── schemas.py
├── static
├── templates
├── test.db
├── test_main.py
├── users.db
└── venv

## Test Execution Summary

Die Tests wurden mit `pytest` erstellt und mit dem folgenden Command kann man sie ausführen:

```sh
pytest


## Test Results

- **Total Tests Collected:** 9
- **Tests Passed:** 9 (100%)
- **Warnings:** 5
- **Execution Time:** 4.46s

### Detailed Test Warnings

Die folgenden warnings wurden gefunden:

1. **SQLAlchemy Deprecation Warning**: The `declarative_base()` function should be updated to `sqlalchemy.orm.declarative_base()`. This function has been deprecated since SQLAlchemy 2.0.
   - **File:** `database.py`, Line: 30
   - [More Info](https://sqlalche.me/e/b8d9)

2. **Pydantic Deprecated Configuration**: The class-based `config` for Pydantic is deprecated and will be removed in V3.0. `ConfigDict` should be used instead.
   - **File:** `venv/lib/python3.10/site-packages/pydantic/_internal/_config.py`, Line: 291
   - [Migration Guide](https://errors.pydantic.dev/2.9/migration/)

3. **FastAPI `on_event` Deprecation Warning**: The `@app.on_event("startup")` decorator is deprecated. It is recommended to use lifespan event handlers instead.
   - **File:** `main.py`, Line: 170
   - [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)

4. **Starlette Templating Warning**: The `TemplateResponse(name, {"request": request})` format is deprecated; use `TemplateResponse(request, name)` instead.
   - **File:** `test_main.py::test_home_route`

For complete documentation on warnings, please refer to [Pytest Warnings](https://docs.pytest.org/en/stable/how-to/capture-warnings.html).

## Tests Included in `test_main.py`

### User Registration

- `test_register_user_success`: Verifies successful user registration.
- `test_register_user_duplicate_username`: Tests registration with an existing username.
- `test_register_user_duplicate_email`: Tests registration with an existing email.

### User Login

- `test_login_user_success`: Verifies successful user login.
- `test_login_user_invalid_password`: Tests login with an incorrect password.

### Protected Endpoint `/users/me`

- `test_read_users_me_success`: Verifies access to `/users/me` with a valid token.
- `test_read_users_me_unauthorized`: Verifies unauthorized access to `/users/me` without a token.

### Health Check

- `test_health_check`: Verifies the `/health` endpoint returns status `ok`.

### Home Route

- `test_home_route`: Verifies that the home page returns the correct `index.html`.
