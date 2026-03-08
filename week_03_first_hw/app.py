from task_system import task_manager

def meniu():
    print("\nTask Manager")
    print("1. Load tasks from file")
    print("2. Save tasks to file")
    print("3. Create a new task")
    print("4. View all tasks")
    print("5.Update task")
    print("6.Get task by id")
    print("7.Change task status")
    print("8. Exit")

if __name__ == "__main__":
    meniu()
    manager = task_manager()
    while True:
        choice = input("Select an option: ")
        if choice == '1':
            manager.load_task()
        elif choice == '2':
            manager.save_task()
        elif choice == '3':
            title = input("Enter task title: ")
            owner = input("Enter task owner: ")
            description = input("Enter task description (optional): ")
            manager.create_task(title, owner, description)
        elif choice == '4':
            for t in manager.tasks:
                print(t)
        elif choice == '8':
            print("Exiting...")
            break
        elif choice == '5':
            task_id = int(input("Enter task ID to update: "))
            manager.update_task(task_id)
        elif choice == '6':
            task_id = int(input("Enter task ID to view: "))
            manager.get_task_by_id(task_id)
        elif choice == '7':
            task_id = int(input("Enter task ID to change status: "))
            new_status = input("Enter new status (CREATED, IN_PROGRESS, COMPLETED): ").upper()
            manager.change_status(task_id, new_status)
        else:
            print("Invalid option. Please try again.")