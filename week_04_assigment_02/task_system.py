from datetime import datetime
from db_handler import *
from exceptions import TaskNotFoundError, InvalidStatusTransitionError, InvalidInputError



# ==========================================
# 1. Clasa Task
# ==========================================

class task:
    def __init__(self, _id,_title, _description,_owner, _status,_created_at, _updated_at):
        self.id = _id
        self.title = _title
        self.description = _description
        self.owner = _owner
        self.status = _status
        self.created_at = _created_at
        self.updated_at = _updated_at

    def __str__(self):
        return f"[{self.id}] {self.title} | Owner: {self.owner} | Status: {self.status}"

# ==========================================
# 2. Clasa TaskManager
# ==========================================

class task_manager:
    def __init__(self, filename="tasks.json"):
        self.tasks = []
        self.filename = filename

    def load_task(self):
        conn = get_db_connection()
        if conn is None:
            print("Failed to connect to the database. Tasks not loaded.")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM tasks")
            rows = cursor.fetchall()
            self.tasks = []
            for row in rows:
                updated_at = row['updated_at'] if 'updated_at' in row.keys() else row['created_at']
                self.tasks.append(task(
                    _id=row['id'],
                    _title=row['title'],
                    _description=row['description'],
                    _owner=row['owner'],
                    _status=row['status'],
                    _created_at=row['created_at'],
                    _updated_at=updated_at
                ))
            print(f"Tasks loaded from database successfully.")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.tasks = []
        finally:            
            conn.close()
        

    def save_task(self):
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()   
        try:  
            for t in self.tasks:
                cursor.execute("INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)",
                               (t.title, t.description, t.status))
            conn.commit()
            print(f"Tasks saved to database successfully.")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    
    def create_task(self, title: str, owner: str, description: str = ""):
        conn = get_db_connection()
        if not conn:
            raise Exception("Database connection failed") # Tell FastAPI something went wrong

        cursor = conn.cursor()
        try:
            # 1. Generate timestamps in Python (simplest way to keep things consistent)
            now = datetime.now().isoformat()
            status = "todo"

            # 2. Update your SQL to include the new fields
            query = """
                INSERT INTO tasks (title, description, owner, status, created_at, updated_at) 
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (title, description, owner, status, now, now))
            conn.commit()

            # 3. Get the ID of the row we just inserted
            task_id = cursor.lastrowid

            # 4. Return a dictionary that matches your TaskResponse schema exactly
            return {
                "id": task_id,
                "title": title,
                "owner": owner,
                "description": description,
                "status": status,
                "created_at": now,
                "updated_at": now
            }
        finally:
            conn.close()
    
    def list_tasks(self, filter_status: str = None, filter_owner: str = None, sort_by: str = "id"):
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed")
        
        # Ensure your connection returns rows as dictionaries (row_factory)
        cursor = conn.cursor()
        try:
            query = "SELECT * FROM tasks"
            conditions = []
            params = []
            
            if filter_status:
                conditions.append("status = ?")
                params.append(filter_status)
            if filter_owner:
                conditions.append("owner = ?")
                params.append(filter_owner)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            # Validation: Only allow sorting by specific columns to prevent SQL injection
            allowed_sort = ["id", "title", "owner", "status", "created_at"]
            if sort_by not in allowed_sort:
                sort_by = "id"
                
            query += f" ORDER BY {sort_by}"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Instead of printing, return the rows as a list of dicts
            # FastAPI/Pydantic will handle the formatting automatically
            return [dict(row) for row in rows]
            
        finally:            
            conn.close()
    
    
    
    def update_task(self, task_id: int, title: str = None, owner: str = None, description: str = None):
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row is None:
                raise TaskNotFoundError(f"Task with ID {task_id} not found.")
            
            # Check if at least one field is being updated
            if title is None and owner is None and description is None:
                raise InvalidInputError("At least one field (title, owner, or description) must be provided for update.")
            
            updated_title = title if title else row['title']
            updated_description = description if description else row['description']
            updated_owner = owner if owner else row['owner']
            now = datetime.now().isoformat()
            cursor.execute("UPDATE tasks SET title = ?, description = ?, owner = ?, updated_at = ? WHERE id = ?",
                           (updated_title, updated_description, updated_owner, now, task_id))
            conn.commit()
            return {
                "id": task_id,
                "title": updated_title,
                "owner": updated_owner,
                "description": updated_description,
                "status": row['status'],
                "created_at": row['created_at'],
                "updated_at": now,
            }
            
        except sqlite3.Error as e:
            raise Exception(f"Database error: {e}")
        finally:            
            conn.close()

    def get_task_by_id(self, task_id: int):
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row is None:
                raise TaskNotFoundError(f"Task with ID {task_id} not found.")
            updated_at = row['updated_at'] if 'updated_at' in row.keys() else row['created_at']
            return {
                "id": row['id'],
                "title": row['title'],
                "owner": row['owner'],
                "description": row['description'],
                "status": row['status'],
                "created_at": row['created_at'],
                "updated_at": updated_at,
            }
        except sqlite3.Error as e:
            raise Exception(f"Database error: {e}")
        finally:            
            conn.close()
    
    def change_status(self, task_id: int, new_status: str):
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row is None:
                raise TaskNotFoundError(f"Task with ID {task_id} not found.")
            current_status = row['status']
            if current_status in ["canceled", "blocked"]:
                raise InvalidStatusTransitionError(f"Cannot change status from {current_status} to {new_status}.")
            now = datetime.now().isoformat()
            cursor.execute("UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
                           (new_status, now, task_id))
            conn.commit()
            return {
                "id": task_id,
                "title": row['title'],
                "owner": row['owner'],
                "description": row['description'],
                "status": new_status,
                "created_at": row['created_at'],
                "updated_at": now,
            }
        except sqlite3.Error as e:
            raise Exception(f"Database error: {e}")
        finally:            
            conn.close()