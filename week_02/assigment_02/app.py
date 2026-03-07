from data_store import *

UNDO_STACK = []

def process_next_event():
    if not EVENT_LOG:
        print("No events to process.")
        return None
    
    next_event = EVENT_LOG.pop(0)
    print(f"Processing event: {next_event['name']} with priority {next_event['pryoriti']}")
    return next_event

def push_to_undo(event_id):
    if not any(event['id'] == event_id for event in EVENT_LOG):
        print(f"Event with ID {event_id} not found.")
        return None
    
    UNDO_STACK.append(event_id)
    print(f"Event with ID {event_id} added to undo stack.")
    
def undo_last_event():
    if not UNDO_STACK:
        print ("No events to undo.")
        return None
    last_event_id = UNDO_STACK.pop()
    for i, event in enumerate(EVENT_LOG):
        if event['id'] == last_event_id:
            EVENT_LOG.pop(i) 
            print(f"Event with ID {last_event_id} has been undone.")
            break

def list_events(sort_by: str = 'id'):
    if not EVENT_LOG:
        print("No events to display.")
        return None
    sorted_events = sorted(EVENT_LOG, key=lambda x: x.get(sort_by, 'id'))
    for event in sorted_events:
        print(f"ID: {event['id']}, Name: {event['name']}, Priority: {event['pryoriti']}")


if __name__ == "__main__":
    
    while True:
        print("\n"+"Event Management System")
        print("="*30)
        print("1. Add Event")
        print("2. Process Next Event")
        print("3. Undo Last Event")
        print("4. List Events")
        print("5. Exit")
        print ("="*30)
        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter event name: ")
            priority = input("Enter event priority (LOW, MEDIUM, HIGH): ").upper()
            if not priority:
                priority = 'LOW'
            note = input("Enter additional note (optional): ")
            extra_args = {}
            if note:
                extra_args['note'] = note
            new_event = add_event(name, priority, **extra_args)
            print(f"Event added: {new_event}")
            push_to_undo(new_event['id'])
        elif choice == '2':
            print("Processing next event...")
            process_next_event()
        elif choice == '3':
            print ("Undoing last event...")
            undo_last_event()
        elif choice == '4':
            print("Listing events...")
            list_events()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")