import sqlite3
import os


def create_tables(conn):
        
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            owner TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

       
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [row[1] for row in cursor.fetchall()]
        if "updated_at" not in columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN updated_at TIMESTAMP")
            cursor.execute("UPDATE tasks SET updated_at = created_at WHERE updated_at IS NULL")
            conn.commit()


def get_db_connection():
    db_exists = os.path.exists("task.db")
    try:
        conn = sqlite3.connect("task.db")
        conn.row_factory = sqlite3.Row
        if not db_exists:
            create_tables(conn)
        else:
            create_tables(conn)
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None


