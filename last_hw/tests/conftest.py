"""
Pytest configuration and fixtures for comprehensive testing.
Provides isolated database and test client fixtures.
"""

import pytest
import os
import sys
from pathlib import Path

# Make sure we can import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set environment variables for testing before any imports
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_USER"] = "postgres"
os.environ["DB_PASSWORD"] = "postgres"
os.environ["DB_NAME"] = "test_task_management"


@pytest.fixture(scope="session")
def test_db_setup():
    """
    Session-scoped fixture to set up the test database.
    Creates test database before all tests and cleans up after.
    """
    import psycopg2
    from psycopg2 import sql

    # Connect to default postgres database to create test database
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        dbname="postgres",
    )
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Drop test database if it exists
        cursor.execute("DROP DATABASE IF EXISTS test_task_management;")
        # Create test database
        cursor.execute("CREATE DATABASE test_task_management;")
        print("Test database created successfully.")
    except Exception as e:
        print(f"Warning: Could not set up test database: {e}")
    finally:
        cursor.close()
        conn.close()

    yield

    # Cleanup after all tests
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            dbname="postgres",
        )
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("DROP DATABASE IF EXISTS test_task_management;")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Warning: Could not clean up test database: {e}")


@pytest.fixture
def test_client(test_db_setup):
    """
    Function-scoped fixture providing FastAPI TestClient.
    Creates fresh database tables for each test.
    """
    from fastapi.testclient import TestClient
    from api import app
    from task_system import TaskManager

    # Ensure tables exist for this test
    try:
        manager = TaskManager()
    except Exception as e:
        print(f"Error during test setup: {e}")

    client = TestClient(app)
    return client


@pytest.fixture
def task_manager():
    """Fixture providing TaskManager instance for unit tests."""
    from task_system import TaskManager

    manager = TaskManager()
    return manager


@pytest.fixture
def sample_task_data():
    """Fixture providing sample task data for testing."""
    return {
        "title": "Test Task",
        "owner": "Alice",
        "description": "This is a test task",
    }


@pytest.fixture
def multiple_tasks_data():
    """Fixture providing multiple sample tasks for testing."""
    return [
        {
            "title": "Task 1",
            "owner": "Alice",
            "description": "First task",
        },
        {
            "title": "Task 2",
            "owner": "Bob",
            "description": "Second task",
        },
        {
            "title": "Task 3",
            "owner": "Alice",
            "description": "Third task",
        },
    ]
