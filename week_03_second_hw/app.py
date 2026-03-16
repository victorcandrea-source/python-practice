from task_system import task_manager
from custom_exceptions import *

def meniu():
    print ("1. Load task from file")
    print ("2. Save task in file")
    print ("3. Create task")
    print ("4. List all task")
    print ("5. Update a task")
    print ("6. Get an task by id")
    print ("7. Change a task by id")
    print ("8. Exit")

if __name__ == "__main__":
    manager = task_manager()
    meniu()
    while True:
        option = int(input("Select an option: "))
        #===("1. Load task from file")===
        if option == 1:
            manager.load_task()

        #===("2. Save task in file")===
        elif option == 2:
            manager.save_task()

        #===("3. Create task")===
        elif option == 3 :
            title = input("Title: ")
            description = input("Description: ")
            owner = input("Owner: ")
            if not title or not description or not owner:
                exception = custom_exception("Title, description and owner cannot be empty")
                print(exception.invalid_input_error())
            manager.create_task(title, description, owner)

        #===("4. List all task")===
        elif option == 4:
            manager.list_tasks()

        #===("5. Update a task")===
        elif option == 5:   
            while True:
                try:
                    task_id = int(input("Task ID: "))
                    break
                except ValueError:
                    print("Invalid input for Task ID. Please enter a valid integer.")
            title = input("New Title (leave empty to keep current): ")
            description = input("New Description (leave empty to keep current): ")
            owner = input("New Owner (leave empty to keep current): ")
            if not task_id or not title or not description:
                exception = custom_exception("Title,description and id need to be fiild or need to be correct!!")
                print(exception.invalid_input_error())
            manager.update_task(task_id, title, description, owner)

        #===("6. Get an task by id")===
        elif option == 6:
            while True:
                try:
                    task_id = int(input("Task ID: "))
                    break
                except ValueError:
                    print("Invalid input for Task ID. Please enter a valid integer.")
            if not task_id:
                exception = custom_exception("Task ID cannot be empty")
                print(exception.invalid_input_error())
            manager.get_task_by_id(task_id)
        
        #===("7. Change a task by id")===
        elif option == 7:
            while True:
                try:
                    task_id = int(input("Task ID: "))
                    break
                except ValueError:
                    print("Invalid input for Task ID. Please enter a valid integer.")
            while True:
                new_status = input("New Status: ")
                if new_status in ["COMPLETED" ,"CREATED", "IN_PROGRESS", "DONE", "CANCELED", "BLOCKED"]:
                    break
                else:
                    print("Invalid status. Please enter one of the following: COMPLETED, IN_PROGRESS, DONE, CANCELED, BLOCKED.")
            if not task_id or not new_status:
                exception = custom_exception("Task ID and new status cannot be empty")
                print(exception.invalid_input_error())
            manager.change_status(task_id, new_status)

        #===("8. Exit")===
        elif option == 8:
            print("Exiting the program. Goodbye!")
            break


        