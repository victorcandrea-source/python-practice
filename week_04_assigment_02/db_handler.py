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
    db_path = os.getenv("TASK_DB_PATH", "task.db")
    try:
        conn = sqlite3.connect(db_path)
        
        # KEY FOR API: This allows us to access data by name: row['title']
        conn.row_factory = sqlite3.Row
        
        # Always ensuring tables are ready
        # If your create_tables function uses "CREATE TABLE IF NOT EXISTS", 
        # you don't even need the 'if not db_exists' check!
        create_tables(conn)
        
        return conn
        
    except sqlite3.Error as e:
        # Instead of just printing, we raise an exception.
        # This tells the FastAPI 'try/except' block that the DB is down.
        print(f"Database connection error: {e}")
        return None


