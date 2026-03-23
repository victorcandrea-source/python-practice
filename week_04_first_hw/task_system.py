#import json
from datetime import datetime
from custom_exceptions import *
from db_handler import *



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
        if conn is None:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO tasks (title, description, owner) VALUES (?, ?, ?)",
                           (title, description, owner))
            conn.commit()
            print(f"Task '{title}' created successfully.")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:            
            conn.close()
    
    def list_tasks(self, filter_status: str = None, filter_owner: str = None, sort_by: str = "id"):
        
        conn = get_db_connection()
        if conn is None:
            return
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
            query += f" ORDER BY {sort_by}"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            if not rows:
                print("No tasks match the given filters.")
                return
            for row in rows:
                updated_at = row['updated_at'] if 'updated_at' in row.keys() else row['created_at']
                print(f"ID: {row['id']}, Title: {row['title']}, Owner: {row['owner']}, Status: {row['status']}, Created At: {row['created_at']}, Updated At: {updated_at}")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:            
            conn.close()
    
    
    
    def update_task(self, task_id: int, title: str = None, owner: str = None, description: str = None):
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row is None:
                print(f"Task with ID {task_id} not found.")
                return
            updated_title = title if title else row['title']
            updated_description = description if description else row['description']
            updated_owner = owner if owner else row['owner']
            cursor.execute("UPDATE tasks SET title = ?, description = ?, owner = ?, updated_at = ? WHERE id = ?",
                           (updated_title, updated_description, updated_owner, datetime.now().isoformat(), task_id))
            conn.commit()
            print(f"Task with ID {task_id} has been updated!")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:            
            conn.close()

    def get_task_by_id(self, task_id: int):
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row is None:
                print(f"Task with ID {task_id} not found.")
                return
            updated_at = row['updated_at'] if 'updated_at' in row.keys() else row['created_at']
            print(f"ID: {row['id']}, Title: {row['title']}, Owner: {row['owner']}, Status: {row['status']}, Created At: {row['created_at']}, Updated At: {updated_at}")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:            
            conn.close()
    
    def change_status(self,task_id: int, new_status: str):
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row is None:
                print(f"Task with ID {task_id} not found.")
                return
            current_status = row['status']
            if current_status in ["CANCELED", "BLOCKED"]:
                print(f"Cannot change status from {current_status} to {new_status}.")
                return
            cursor.execute("UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
                           (new_status, datetime.now().isoformat(), task_id))
            conn.commit()
            print(f"Task with ID {task_id} status changed to {new_status}.")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:            
            conn.close()