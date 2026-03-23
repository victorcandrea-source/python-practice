import unittest
import os
import json
from datetime import datetime
from task_system import task_manager, task 

class TestTaskManager(unittest.TestCase):

    def setUp(self):
        self.test_filename = "test_tasks.json"
        self.manager = task_manager(self.test_filename)
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    # --- 5. Unit Tests for Core Functionality (Happy Path) ---

    def test_create_task_sets_status_and_id(self):
        new_task = self.manager.create_task("Test Title", "Andrei")
        self.assertIsNotNone(new_task)
        self.assertEqual(new_task.status, "CREATED")
        self.assertEqual(new_task.id, 1)

    def test_update_task_fields_and_timestamp(self):
        t = self.manager.create_task("Old Title", "Andrei")
        old_update_time = t.updated_at
        
        updated = self.manager.update_task(t.id, title="New Title", description="New Desc")
        self.assertEqual(updated.title, "New Title")
        self.assertEqual(updated.description, "New Desc")
        self.assertNotEqual(updated.updated_at, old_update_time)

    def test_change_status_valid(self):
        t = self.manager.create_task("Status Task", "Mihai")
        result = self.manager.change_status(t.id, "IN_PROGRESS")
        self.assertIsNotNone(result)
        self.assertEqual(result.status, "IN_PROGRESS")

    def test_list_tasks_filtering(self):
        self.manager.create_task("Task 1", "Andrei")
        self.manager.create_task("Task 2", "Maria")
        
        filtered = self.manager.list_tasks(filter_owner="Maria")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].owner, "Maria")

    def test_save_and_load_persistence(self):
        self.manager.create_task("Task Persistent", "Admin")
        self.manager.save_task()
        
        new_manager = task_manager(self.test_filename)
        new_manager.load_task()
        self.assertEqual(len(new_manager.tasks), 1)
        self.assertEqual(new_manager.tasks[0].title, "Task Persistent")
        self.assertIsInstance(new_manager.tasks[0], task)

    # --- 6. Unit Tests for Error Handling (Failure Path) ---

    def test_create_task_with_empty_inputs(self):
        result = self.manager.create_task(None, "Andrei")
        self.assertIsNone(result)

    def test_update_non_existent_task_id(self):
        result = self.manager.update_task(999, title="N/A")
        self.assertIsNone(result)

    def test_get_task_by_id_empty_list(self):
        result = self.manager.get_task_by_id(1)
        self.assertIsNone(result)

    def test_load_from_corrupted_json(self):
        with open(self.test_filename, 'w') as f:
            f.write("{ 'invalid': json }")
        
        self.manager.load_task()
        self.assertEqual(len(self.manager.tasks), 0)

    def test_change_status_not_found(self):
        self.manager.create_task("Existent", "Ion")
        result = self.manager.change_status(10, "DONE")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()