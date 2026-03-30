"""
Database handler for PostgreSQL.
Manages connections and schema initialization.
"""

import psycopg2
from psycopg2 import sql, Error as PostgreSQLError
from config import Config
from exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)


class DatabaseHandler:
    """Handles PostgreSQL database operations."""

    def __init__(self):
        """Initialize database handler with connection parameters."""
        self.conn_params = Config.get_database_url_psycopg2()

    def get_connection(self):
        """
        Get a new database connection.

        Returns:
            psycopg2 connection object.

        Raises:
            DatabaseError: If connection fails.
        """
        try:
            conn = psycopg2.connect(self.conn_params)
            return conn
        except PostgreSQLError as e:
            logger.error(f"Failed to connect to database: {e}")
            raise DatabaseError(f"Database connection failed: {e}")

    def ensure_tables_exist(self):
        """
        Create tables if they don't exist.
        Called on application startup for auto-initialization.
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Create tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT DEFAULT '',
                    owner VARCHAR(255) NOT NULL,
                    status VARCHAR(50) DEFAULT 'todo',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Create index on owner for faster filtering
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_owner
                ON tasks(owner);
            """)

            # Create index on status for faster filtering
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_status
                ON tasks(status);
            """)

            conn.commit()
            logger.info("Tables created or verified successfully.")

        except PostgreSQLError as e:
            logger.error(f"Failed to create tables: {e}")
            raise DatabaseError(f"Failed to initialize database schema: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()

    def execute_query(self, query: str, params: tuple = ()):
        """
        Execute a SELECT query and return results.

        Args:
            query: SQL query string.
            params: Query parameters as tuple.

        Returns:
            List of tuples (rows) from the query.

        Raises:
            DatabaseError: If query fails.
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
        except PostgreSQLError as e:
            logger.error(f"Query execution failed: {e}")
            raise DatabaseError(f"Query failed: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()

    def execute_update(self, query: str, params: tuple = ()):
        """
        Execute an INSERT/UPDATE/DELETE query.

        Args:
            query: SQL query string.
            params: Query parameters as tuple.

        Returns:
            The ID of the inserted row (for INSERT), or number of rows affected.

        Raises:
            DatabaseError: If query fails.
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

            # Return lastrowid for INSERT, or rowcount for UPDATE/DELETE
            if "INSERT" in query.upper():
                cursor.execute("SELECT lastval();")
                result = cursor.fetchone()
                return result[0] if result else None
            else:
                return cursor.rowcount

        except PostgreSQLError as e:
            logger.error(f"Update execution failed: {e}")
            raise DatabaseError(f"Update failed: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()

    def fetch_one(self, query: str, params: tuple = ()):
        """
        Execute a query and fetch a single row as a dictionary.

        Args:
            query: SQL query string.
            params: Query parameters.

        Returns:
            Dictionary representing the row, or None if no row found.

        Raises:
            DatabaseError: If query fails.
        """
        conn = None
        try:
            conn = self.get_connection()
            # Set row factory to return dictionaries
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()

            if result:
                # Get column names
                col_names = [desc[0] for desc in cursor.description]
                return dict(zip(col_names, result))
            return None

        except PostgreSQLError as e:
            logger.error(f"Fetch one failed: {e}")
            raise DatabaseError(f"Fetch failed: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()

    def fetch_all(self, query: str, params: tuple = ()):
        """
        Execute a query and fetch all rows as dictionaries.

        Args:
            query: SQL query string.
            params: Query parameters.

        Returns:
            List of dictionaries, one per row.

        Raises:
            DatabaseError: If query fails.
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()

            if not results:
                return []

            # Get column names
            col_names = [desc[0] for desc in cursor.description]
            return [dict(zip(col_names, row)) for row in results]

        except PostgreSQLError as e:
            logger.error(f"Fetch all failed: {e}")
            raise DatabaseError(f"Fetch failed: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()


# Global database handler instance
_db_handler = None


def get_db_handler():
    """Get or create the global database handler instance."""
    global _db_handler
    if _db_handler is None:
        # Try to use real PostgreSQL database
        try:
            _db_handler = DatabaseHandler()
            # Test connection
            _db_handler.ensure_tables_exist()
            logger.info("Using PostgreSQL database")
        except Exception as e:
            # Fall back to mock database if PostgreSQL unavailable
            logger.warning(
                f"PostgreSQL unavailable ({e}), falling back to mock in-memory database"
            )
            from mock_db import get_mock_db_handler

            _db_handler = get_mock_db_handler()
    return _db_handler
