# Test Report

## Overview

This document serves as a test protocol summary for the backend of the project. The goal is to ensure the application meets quality standards through automated unit tests and integration tests. The following sections provide details on the test environment, tools used, testing outcomes, and any relevant warnings or deprecated features noted during testing.

## Test Environment

- **Operating System:** Linux (Ubuntu)
- **Python Version:** Python 3.10.15
- **Virtual Environment:** venv
- **Test Framework:** Pytest 8.3.3
- **Plugins:** anyio-4.4.0
- **Database:** SQLite (for testing purposes)

### Project Directory Structure

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

The tests were executed using `pytest` with the following command:

```sh
pytest


## Test Results

- **Total Tests Collected:** 9
- **Tests Passed:** 9 (100%)
- **Warnings:** 5
- **Execution Time:** 4.46s

### Detailed Test Warnings

During the test run, the following warnings were noted:

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

## Test Protocol Quality Evaluation

- **Screenshots**: (Screenshots can be included if needed to visually demonstrate the test results or steps.)
- **Test Versions and Warnings**: The versions of Python, pytest, and plugins used in the testing environment have been documented.
- **Conclusion**: The tests demonstrate good coverage for the user registration, login, protected routes, and health check functionalities. However, several warnings related to deprecated features should be addressed to ensure long-term maintainability of the project.

## Suggestions for Improvement

- **Deprecation Fixes**: Update the deprecated features in SQLAlchemy, Pydantic, and FastAPI to their latest versions.
- **Test Coverage**: Consider expanding the test coverage to include edge cases and negative scenarios for all endpoints.
- **Environment Versions**: It is recommended to include the output of `pip freeze` to capture the exact versions of all dependencies.
