"""
Pytest configuration and fixtures for API tests
"""

import pytest
import os
import sqlite3
import sys
from pathlib import Path

# Make sure we can import from the parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

TEST_DB_PATH = str(Path(__file__).parent / "tasks_test.db")


def pytest_configure(config):
    """Set environment variables before any tests run"""
    os.environ["TASK_DB_PATH"] = TEST_DB_PATH


@pytest.fixture(scope="function", autouse=True)
def reset_test_database():
    """
    Reset the test database before each test.
    Removes the test DB file to force a fresh start.
    """
    # Remove test DB if it exists
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    yield
    
    # Cleanup after test
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture
def test_client(reset_test_database):
    """Create a test client with isolated test database"""
    from fastapi.testclient import TestClient
    from api import app
    
    client = TestClient(app)
    return client
