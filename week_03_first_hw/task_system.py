import json
from datetime import datetime



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
        try:
            with open(self.filename, 'r') as file:
                tasks_data = json.load(file)
                self.tasks = [task(
                    _id=data['id'],
                    _title=data['title'],
                    _description=data['description'],
                    _owner=data['owner'],
                    _status=data['status'],
                    _created_at=data['created_at'],
                    _updated_at=data['updated_at']
                ) for data in tasks_data]
            print(f"Tasks loaded from {self.filename} successfully.")
        except FileNotFoundError:
            print(f"No existing task file found. Starting with an empty task list.")
            self.tasks = [] 
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {self.filename}. Starting with an empty task list.")
            self.tasks = [] 

    def save_task(self):
        tast_as_dict = [t.__dict__ for t in self.tasks] 
        with open(self.filename, 'w') as file:
            json.dump(tast_as_dict, file, indent=4) 
        print(f"Tasks saved to {self.filename} successfully.")
    
    def create_task(self, title: str, owner: str, description: str = ""):
        if not self.tasks:
            new_id = 1
        else:
            new_id = max(t.id for t in self.tasks) + 1
            
        now = datetime.now().isoformat()
        
       
        new_task = task(
            _id=new_id,
            _title=title,
            _description=description,
            _owner=owner,
            _status="CREATED",
            _created_at=now,
            _updated_at=now
        )
        self.tasks.append(new_task)
        print(f"Task created with ID: {new_id}")
        return new_task


    def list_tasks(self, filter_status: str = None, filter_owner: str = None, sort_by: str = "id"):
        if not self.tasks: 
            print("No tasks to display.")
            return None
            
       
        filtered_tasks = self.tasks
        if filter_status:
            filtered_tasks = [t for t in filtered_tasks if t.status.lower() == filter_status.lower()]
        if filter_owner:
            filtered_tasks = [t for t in filtered_tasks if t.owner.lower() == filter_owner.lower()]

        if not filtered_tasks:
            print("No tasks match the given filters.")
            return None

        
        sorted_tasks = sorted(filtered_tasks, key=lambda x: getattr(x, sort_by, getattr(x, 'id')))
        
        for t in sorted_tasks:
            print(f"ID: {t.id}, Title: {t.title}, Owner: {t.owner}, Status: {t.status}, Created At: {t.created_at}, Updated At: {t.updated_at}")
            
        return sorted_tasks
    
    
    def update_task(self, task_id: int, title: str = None, owner: str = None, description: str = None):
        for t in self.tasks:
            if t.id == task_id:
                if title is not None:
                    t.title = title
                if owner is not None:
                    t.owner = owner
                if description is not None:
                    t.description = description
                    
                t.updated_at = datetime.now().isoformat()
                print(f"Task with ID {task_id} has been updated!")
                return t
        print(f"Task with ID {task_id} not found.")
        return None
    
   
    def get_task_by_id(self, task_id: int):
        if not self.tasks:
            print("No tasks available.")
            return None
            
        for t in self.tasks: 
            if t.id == task_id: 
                print(f"Task with ID {task_id} was found.")
                return t
        print(f"Task with ID {task_id} not found.")
        return None

    def change_status(self,task_id: int, new_status: str):
        if not self.tasks:
            print("No tasks available.")
            return None
        for task in self.tasks:
           if task.id == task_id:
                if  not task.status == "CANCELED" or task.status == "BLOCKED":
                    print(f"Task with ID {task_id} cannot change status from {task.status} to {new_status}.")
                    return None
                else:
                    task.status = new_status
                    task.updated_at = datetime.now().isoformat()
                    print(f"Task with ID {task_id} status changed to {new_status}.")
                    return task
        print(f"Task with ID {task_id} not found.")
        return None
