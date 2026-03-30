# Development Guide

Guide for developers working with the Task Management System.

## Development Setup

### Initial Setup

```bash
# 1. Clone the repository and navigate to project
cd last_hw

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies including dev tools
pip install -r requirements.txt
pip install black flake8 mypy  # Optional: code quality tools

# 4. Set up environment variables
cp .env.example .env

# 5. Ensure PostgreSQL is running (Docker or local)
# Using Docker:
docker run --name postgres_dev -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=task_management -p 5432:5432 -d postgres:15

# 6. Run tests to verify setup
pytest tests/ -v
```

### Running Development Server

```bash
# With auto-reload
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# With debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
uvicorn api:app --reload --log-level debug
```

## Project Structure Walkthrough

### Core Application Files

#### `config.py` - Configuration Management
- Centralized configuration from environment variables
- Database URL construction
- Application settings

**Key Functions:**
- `Config.get_database_url()` - PostgreSQL connection string
- `Config.get_database_url_psycopg2()` - psycopg2-specific format

#### `db_handler.py` - Database Repository Layer
- PostgreSQL connection management
- Query execution abstraction
- Schema initialization

**Key Classes:**
- `DatabaseHandler` - Main database operations class
- `get_db_handler()` - Singleton factory function

**Key Methods:**
```python
db.ensure_tables_exist()        # Initialize schema
db.execute_query(sql, params)   # SELECT queries
db.execute_update(sql, params)  # INSERT/UPDATE/DELETE
db.fetch_one(sql, params)       # Single row as dict
db.fetch_all(sql, params)       # Multiple rows as dicts
```

#### `task_system.py` - Business Logic Service Layer
- Task model (data structure)
- TaskManager service (business logic)

**Key Classes:**
- `Task` - Task data model
- `TaskManager` - Business logic service

**Task Model:**
```python
task = Task(
    task_id=1,
    title="...",
    description="...",
    owner="...",
    status="...",
    created_at="...",
    updated_at="..."
)
```

**TaskManager Methods:**
```python
manager.create_task(title, owner, description)
manager.get_task_by_id(task_id)
manager.list_tasks(filter_status, filter_owner, sort_by)
manager.update_task(task_id, title, owner, description)
manager.delete_task(task_id)
manager.change_status(task_id, new_status)
```

#### `schemas.py` - Pydantic Models
Request/response validation using Pydantic BaseModel.

**Key Classes:**
- `TaskCreateRequest` - POST /tasks
- `TaskPatchRequest` - PATCH /tasks/{id}
- `TaskStatusChangeRequest` - POST /tasks/{id}/status
- `TaskResponse` - All task responses

#### `api.py` - FastAPI Application
RESTful API endpoints with exception handling.

**Key Routes:**
```python
GET    /health                      # Health check
POST   /tasks                       # Create task
GET    /tasks                       # List tasks (filterable)
GET    /tasks/{id}                  # Get task
PATCH  /tasks/{id}                  # Update task
DELETE /tasks/{id}                  # Delete task
POST   /tasks/{id}/status           # Change status
```

#### `exceptions.py` - Custom Exceptions
Application-specific exception hierarchy.

**Exception Types:**
- `TaskNotFoundError` → 404
- `InvalidStatusTransitionError` → 409
- `InvalidInputError` → 422
- `DatabaseError` → 500

## Development Workflow

### Writing New Features

1. **Plan & Design**
   - Sketch the feature
   - Design API endpoint (if needed)
   - Plan database changes

2. **Implement**
   - Update database schema (if needed) in `db_handler.py`
   - Add business logic in `task_system.py`
   - Update Pydantic models in `schemas.py`
   - Add API endpoints in `api.py`

3. **Test**
   - Write unit tests in `tests/test_task_system.py`
   - Write integration tests in `tests/test_api.py`
   - Add database tests in `tests/test_db_handler.py`

4. **Verify**
   - Run: `pytest tests/ -v`
   - Check coverage: `pytest --cov=. tests/`
   - Format code: `black .`
   - Lint code: `flake8 .`

### Example: Adding a Due Date Field

```bash
# 1. Update database schema
# In db_handler.py::ensure_tables_exist():
cursor.execute("""
    ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP;
""")

# 2. Update Task model
# In task_system.py::Task:
def __init__(self, ..., due_date: str = None):
    ...
    self.due_date = due_date

# 3. Update TaskManager
# In task_system.py::TaskManager.create_task():
def create_task(self, title, owner, description, due_date=None):
    ...

# 4. Update Pydantic schemas
# In schemas.py:
class TaskCreateRequest(BaseModel):
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    due_date: Optional[str] = None

# 5. Update API endpoints
# In api.py: Update endpoints as needed

# 6. Write tests
pytest tests/ -v --cov=.
```

## Testing Best Practices

### Unit Tests vs Integration Tests

**Unit Tests** (test_task_system.py)
- Test business logic in isolation
- Mock database if needed
- Test error cases
- Test edge cases

```python
def test_create_task_empty_title_raises_error(self, task_manager):
    with pytest.raises(InvalidInputError):
        task_manager.create_task(title="", owner="Alice")
```

**Integration Tests** (test_api.py)
- Test full request/response cycle
- Use TestClient
- Test database persistence
- Test error responses

```python
def test_create_task_success(self, test_client, sample_task_data):
    response = test_client.post("/tasks", json=sample_task_data)
    assert response.status_code == 201
```

**Database Tests** (test_db_handler.py)
- Test database operations
- Test connection handling
- Test schema generation
- Test error handling

```python
def test_ensure_tables_exist_creates_tasks_table(self):
    db = DatabaseHandler()
    db.ensure_tables_exist()
    # Verify table exists
```

### Test Naming Convention

```python
# test_<module>.py
class Test<Feature>:
    def test_<action>_<scenario>_<expected_result>(self):
        pass
```

Examples:
- `test_create_task_success`
- `test_create_task_empty_title_raises_error`
- `test_list_tasks_filter_by_owner`

### Code Coverage Goals

- **Target:** 80%+
- **API Layer:** 90%
- **Service Layer:** 85%
- **Database Layer:** 75%

```bash
# Generate coverage report
pytest --cov=. --cov-report=html tests/
open htmlcov/index.html

# Check specific file coverage
coverage report -m
```

## Debugging

### Using Python Debugger (pdb)

```python
# In api.py or task_system.py
import pdb

@app.post("/tasks")
async def create_task(payload):
    pdb.set_trace()  # Execution pauses here
    # Use: n (next), s (step), c (continue), p <var> (print)
    ...
```

### Logging at Different Levels

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed debug info")
logger.info("General info")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Enable SQL Query Logging

```bash
# Set PostgreSQL logging
export POSTGRES_INITDB_ARGS="-c log_statement=all"
```

### Local Testing with Docker

```bash
# Start only PostgreSQL
docker run --name postgres_test \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=test_task_management \
  -p 5432:5432 \
  postgres:15

# Run tests locally
export DB_HOST=localhost
pytest tests/ -v

# Cleanup
docker stop postgres_test
docker rm postgres_test
```

## Code Quality Tools

### Formatting with Black

```bash
# Install
pip install black

# Format single file
black api.py

# Format entire project
black .

# Check without modifying
black --check .
```

### Linting with Flake8

```bash
# Install
pip install flake8

# Check for issues
flake8 .

# Show statistics
flake8 --statistics .
```

### Type Checking with mypy

```bash
# Install
pip install mypy

# Check types
mypy --strict .
```

## Common Development Tasks

### Add New API Endpoint

1. Add Pydantic model in `schemas.py`
2. Add business logic in `task_system.py`
3. Add route in `api.py`
4. Add tests in `tests/test_api.py`
5. Run: `pytest tests/test_api.py -v`

### Modify Database Schema

1. Update `ensure_tables_exist()` in `db_handler.py`
2. Handle migration manually (or add migration logic)
3. Update Task model if needed in `task_system.py`
4. Update tests in `tests/test_db_handler.py`
5. Test: `pytest tests/test_db_handler.py -v`

### Fix a Bug

1. Write failing test that reproduces bug
2. Run: `pytest tests/ -v` (confirm failure)
3. Fix the bug in application code
4. Run: `pytest tests/ -v` (confirm fix)
5. Check coverage: `pytest --cov=.`

### Optimize a Slow Endpoint

1. Profile with `cProfile` or logging
2. Identify bottleneck (DB query, logic, etc)
3. Optimize (add index, cache result, etc)
4. Benchmark before/after
5. Run full test suite

```python
# Profile a function
import cProfile
cProfile.run('manager.list_tasks(filter_owner="Alice")')
```

## Contributing Guidelines

### Commit Message Format

```
[TYPE] Brief description (50 chars max)

Longer description if needed (72 chars per line).

- Bullet point details
- More details

Related to issue #123
```

Types: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`

### Pull Request Process

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes with commits
3. Write/update tests
4. Verify coverage: `pytest --cov=.`
5. Run linters: `black . && flake8 .`
6. Push branch and create PR
7. Ensure CI passes
8. Request review

### Code Review Checklist

- [ ] Tests added/updated
- [ ] Code follows PEP8
- [ ] Docstrings added/updated
- [ ] No SQL injection vulnerabilities
- [ ] Error handling added
- [ ] Coverage maintained/improved
- [ ] No hardcoded credentials

## Useful Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run specific test class
pytest tests/test_api.py::TestCreateTask -v

# Run specific test
pytest tests/test_api.py::TestCreateTask::test_create_task_success -v

# Run with coverage
pytest --cov=. --cov-report=html tests/

# Run tests in parallel
pytest -n auto tests/

# Run tests with profiling
pytest tests/ --durations=10

# Watch for changes and re-run
pytest-watch -- tests/ -v

# Show what tests would run (dry run)
pytest tests/ --collect-only

# Run failed tests only
pytest tests/ --lf

# Show print statements
pytest tests/ -v -s
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pytest Documentation](https://docs.pytest.org/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)

---

**Last Updated:** March 30, 2026
