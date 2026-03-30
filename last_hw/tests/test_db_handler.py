"""
Unit tests for DatabaseHandler - database layer tests.
Tests database operations and connection handling.
"""

import pytest
from db_handler import DatabaseHandler, get_db_handler
from exceptions import DatabaseError


# ==========================================
# Database Handler Initialization Tests
# ==========================================


class TestDatabaseHandlerInitialization:
    """Tests for DatabaseHandler initialization."""

    def test_database_handler_creation(self):
        """Test creating DatabaseHandler instance."""
        db = DatabaseHandler()
        assert db is not None
        assert hasattr(db, "conn_params")

    def test_get_db_handler_singleton(self):
        """Test that get_db_handler returns singleton instance."""
        db1 = get_db_handler()
        db2 = get_db_handler()
        # Should be same instance (singleton pattern)
        assert db1 is db2

    def test_database_url_construction(self):
        """Test PostgreSQL connection URL construction."""
        db = DatabaseHandler()
        url = db.conn_params
        assert isinstance(url, str)
        assert "host=" in url
        assert "port=" in url
        assert "user=" in url
        assert "dbname=" in url


# ==========================================
# Table Creation Tests
# ==========================================


class TestDatabaseHandlerTableCreation:
    """Tests for automatic table creation."""

    def test_ensure_tables_exist_creates_tasks_table(self):
        """Test that ensure_tables_exist creates tasks table."""
        db = DatabaseHandler()
        # This should not raise any exception
        db.ensure_tables_exist()

    def test_ensure_tables_exist_idempotent(self):
        """Test that ensure_tables_exist can be called multiple times safely."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        # Should not fail calling it again
        db.ensure_tables_exist()

    def test_tasks_table_has_correct_columns(self):
        """Test that tasks table has all required columns."""
        db = DatabaseHandler()
        db.ensure_tables_exist()

        # Query table structure
        query = """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'tasks'
            ORDER BY ordinal_position;
        """
        results = db.execute_query(query)

        column_names = [row[0] for row in results]
        assert "id" in column_names
        assert "title" in column_names
        assert "description" in column_names
        assert "owner" in column_names
        assert "status" in column_names
        assert "created_at" in column_names
        assert "updated_at" in column_names

    def test_tasks_table_has_id_primary_key(self):
        """Test that id column is primary key."""
        db = DatabaseHandler()
        db.ensure_tables_exist()

        query = """
            SELECT column_name
            FROM information_schema.table_constraints
            WHERE table_name = 'tasks'
            AND constraint_type = 'PRIMARY KEY';
        """
        results = db.execute_query(query)
        assert len(results) > 0


# ==========================================
# Execute Query Tests
# ==========================================


class TestDatabaseHandlerExecuteQuery:
    """Tests for execute_query method."""

    def test_execute_query_select_all_from_empty_table(self):
        """Test SELECT from empty tasks table."""
        db = DatabaseHandler()
        db.ensure_tables_exist()

        # Clear any existing data
        db.execute_update("DELETE FROM tasks;")

        query = "SELECT * FROM tasks;"
        results = db.execute_query(query)
        assert isinstance(results, list)
        assert len(results) == 0

    def test_execute_query_with_parameters(self):
        """Test query execution with parameters."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        # Insert a task
        insert_query = """
            INSERT INTO tasks (title, owner, status)
            VALUES (%s, %s, %s);
        """
        db.execute_update(insert_query, ("Test", "Alice", "todo"))

        # Query with parameter
        query = "SELECT * FROM tasks WHERE owner = %s;"
        results = db.execute_query(query, ("Alice",))
        assert len(results) == 1


# ==========================================
# Execute Update Tests
# ==========================================


class TestDatabaseHandlerExecuteUpdate:
    """Tests for execute_update method."""

    def test_execute_update_insert_returns_id(self):
        """Test INSERT returns the new row ID."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        query = """
            INSERT INTO tasks (title, owner, status)
            VALUES (%s, %s, %s);
        """
        result_id = db.execute_update(query, ("Test Task", "Alice", "todo"))
        assert isinstance(result_id, int)
        assert result_id > 0

    def test_execute_update_insert_increments_id(self):
        """Test that multiple inserts get incrementing IDs."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        query = """
            INSERT INTO tasks (title, owner, status)
            VALUES (%s, %s, %s);
        """
        id1 = db.execute_update(query, ("Task 1", "Alice", "todo"))
        id2 = db.execute_update(query, ("Task 2", "Bob", "todo"))

        assert id2 > id1

    def test_execute_update_delete_returns_rowcount(self):
        """Test DELETE returns number of rows affected."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        # Insert task
        insert_query = """
            INSERT INTO tasks (title, owner, status)
            VALUES (%s, %s, %s);
        """
        task_id = db.execute_update(insert_query, ("Task", "Alice", "todo"))

        # Delete task
        delete_query = "DELETE FROM tasks WHERE id = %s;"
        rowcount = db.execute_update(delete_query, (task_id,))
        assert rowcount == 1

    def test_execute_update_update_returns_rowcount(self):
        """Test UPDATE returns number of rows affected."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        # Insert task
        insert_query = """
            INSERT INTO tasks (title, owner, status)
            VALUES (%s, %s, %s);
        """
        task_id = db.execute_update(insert_query, ("Task", "Alice", "todo"))

        # Update task
        update_query = "UPDATE tasks SET title = %s WHERE id = %s;"
        rowcount = db.execute_update(update_query, ("New Title", task_id))
        assert rowcount == 1


# ==========================================
# Fetch One Tests
# ==========================================


class TestDatabaseHandlerFetchOne:
    """Tests for fetch_one method."""

    def test_fetch_one_existing_row(self):
        """Test fetching a single existing row."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        # Insert task
        insert_query = """
            INSERT INTO tasks (title, owner, status)
            VALUES (%s, %s, %s);
        """
        task_id = db.execute_update(
            insert_query, ("Test Task", "Alice", "todo")
        )

        # Fetch it
        query = "SELECT * FROM tasks WHERE id = %s;"
        result = db.fetch_one(query, (task_id,))

        assert result is not None
        assert isinstance(result, dict)
        assert result["title"] == "Test Task"
        assert result["owner"] == "Alice"

    def test_fetch_one_non_existent_returns_none(self):
        """Test fetching non-existent row returns None."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        query = "SELECT * FROM tasks WHERE id = %s;"
        result = db.fetch_one(query, (999,))
        assert result is None

    def test_fetch_one_returns_dict_with_column_names(self):
        """Test that fetch_one returns dictionary with column names as keys."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        insert_query = """
            INSERT INTO tasks (title, description, owner, status)
            VALUES (%s, %s, %s, %s);
        """
        task_id = db.execute_update(
            insert_query, ("Test", "Desc", "Alice", "todo")
        )

        query = "SELECT * FROM tasks WHERE id = %s;"
        result = db.fetch_one(query, (task_id,))

        assert "id" in result
        assert "title" in result
        assert "description" in result
        assert "owner" in result
        assert "status" in result


# ==========================================
# Fetch All Tests
# ==========================================


class TestDatabaseHandlerFetchAll:
    """Tests for fetch_all method."""

    def test_fetch_all_empty_table(self):
        """Test fetching all from empty table."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        query = "SELECT * FROM tasks;"
        results = db.fetch_all(query)

        assert isinstance(results, list)
        assert len(results) == 0

    def test_fetch_all_multiple_rows(self):
        """Test fetching all rows from table."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        # Insert multiple tasks
        insert_query = """
            INSERT INTO tasks (title, owner, status)
            VALUES (%s, %s, %s);
        """
        db.execute_update(insert_query, ("Task 1", "Alice", "todo"))
        db.execute_update(insert_query, ("Task 2", "Bob", "todo"))

        # Fetch all
        query = "SELECT * FROM tasks;"
        results = db.fetch_all(query)

        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(row, dict) for row in results)

    def test_fetch_all_with_filter(self):
        """Test fetch_all with WHERE clause."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        insert_query = """
            INSERT INTO tasks (title, owner, status)
            VALUES (%s, %s, %s);
        """
        db.execute_update(insert_query, ("Alice Task 1", "Alice", "todo"))
        db.execute_update(insert_query, ("Alice Task 2", "Alice", "todo"))
        db.execute_update(insert_query, ("Bob Task", "Bob", "todo"))

        # Fetch Alice's tasks
        query = "SELECT * FROM tasks WHERE owner = %s;"
        results = db.fetch_all(query, ("Alice",))

        assert len(results) == 2
        for row in results:
            assert row["owner"] == "Alice"

    def test_fetch_all_with_order_by(self):
        """Test fetch_all with ORDER BY clause."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        insert_query = """
            INSERT INTO tasks (title, owner, status)
            VALUES (%s, %s, %s);
        """
        db.execute_update(insert_query, ("Zebra", "Alice", "todo"))
        db.execute_update(insert_query, ("Apple", "Bob", "todo"))
        db.execute_update(insert_query, ("Banana", "Charlie", "todo"))

        # Fetch all ordered by title
        query = "SELECT * FROM tasks ORDER BY title;"
        results = db.fetch_all(query)

        titles = [row["title"] for row in results]
        assert titles == ["Apple", "Banana", "Zebra"]


# ==========================================
# Connection Error Handling Tests
# ==========================================


class TestDatabaseHandlerErrorHandling:
    """Tests for error handling in database operations."""

    def test_get_connection_handles_invalid_params(self):
        """Test that invalid connection params raise DatabaseError."""
        db = DatabaseHandler()
        # Temporarily set invalid params
        db.conn_params = "invalid connection string"

        with pytest.raises(DatabaseError):
            db.get_connection()

    def test_execute_query_with_invalid_sql_raises_error(self):
        """Test that invalid SQL raises DatabaseError."""
        db = DatabaseHandler()
        db.ensure_tables_exist()

        with pytest.raises(DatabaseError):
            db.execute_query("INVALID SQL SYNTAX;")

    def test_execute_update_with_invalid_sql_raises_error(self):
        """Test that invalid UPDATE SQL raises DatabaseError."""
        db = DatabaseHandler()
        db.ensure_tables_exist()

        with pytest.raises(DatabaseError):
            db.execute_update("INVALID SQL SYNTAX;")

    def test_fetch_one_with_invalid_sql_raises_error(self):
        """Test that invalid SELECT in fetch_one raises DatabaseError."""
        db = DatabaseHandler()
        db.ensure_tables_exist()

        with pytest.raises(DatabaseError):
            db.fetch_one("INVALID SQL;")

    def test_fetch_all_with_invalid_sql_raises_error(self):
        """Test that invalid SELECT in fetch_all raises DatabaseError."""
        db = DatabaseHandler()
        db.ensure_tables_exist()

        with pytest.raises(DatabaseError):
            db.fetch_all("INVALID SQL;")


# ==========================================
# Data Persistence Tests
# ==========================================


class TestDatabaseHandlerDataPersistence:
    """Tests for data persistence across operations."""

    def test_inserted_data_persists_across_connections(self):
        """Test that data inserted remains after closing connection."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        # Insert data
        insert_query = """
            INSERT INTO tasks (title, owner, status)
            VALUES (%s, %s, %s);
        """
        task_id = db.execute_update(
            insert_query, ("Persistent Task", "Alice", "todo")
        )

        # Fetch data (new connection automatically)
        query = "SELECT * FROM tasks WHERE id = %s;"
        result = db.fetch_one(query, (task_id,))

        assert result is not None
        assert result["title"] == "Persistent Task"

    def test_updated_data_reflects_in_subsequent_queries(self):
        """Test that UPDATE is reflected in subsequent queries."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        # Insert
        insert_query = """
            INSERT INTO tasks (title, owner, status)
            VALUES (%s, %s, %s);
        """
        task_id = db.execute_update(insert_query, ("Original", "Alice", "todo"))

        # Update
        update_query = "UPDATE tasks SET title = %s WHERE id = %s;"
        db.execute_update(update_query, ("Updated", task_id))

        # Verify update
        query = "SELECT * FROM tasks WHERE id = %s;"
        result = db.fetch_one(query, (task_id,))

        assert result["title"] == "Updated"

    def test_deleted_data_no_longer_in_queries(self):
        """Test that DELETE removes data from queries."""
        db = DatabaseHandler()
        db.ensure_tables_exist()
        db.execute_update("DELETE FROM tasks;")

        # Insert
        insert_query = """
            INSERT INTO tasks (title, owner, status)
            VALUES (%s, %s, %s);
        """
        task_id = db.execute_update(insert_query, ("Task to Delete", "Alice", "todo"))

        # Delete
        delete_query = "DELETE FROM tasks WHERE id = %s;"
        db.execute_update(delete_query, (task_id,))

        # Verify deletion
        query = "SELECT * FROM tasks WHERE id = %s;"
        result = db.fetch_one(query, (task_id,))

        assert result is None
