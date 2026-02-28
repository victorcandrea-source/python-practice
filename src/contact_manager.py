class ContactManager: 
    def __init__(self):
        self.contacts_list = [] 

    def add_contact(self, name: str, phone: str, **kwargs):
        new_contact = {
            "name": name,
            "phone": phone,
            "optionals": kwargs
        }
        self.contacts_list.append(new_contact)
        print(f"Contact {name} added successfully!")
        return new_contact 

    def list_all_contacts(self):
        if not self.contacts_list:
            print("No contacts found.")
            return
        for c in self.contacts_list:
            print(f"Name: {c['name']}, Phone: {c['phone']}, Extra: {c['optionals']}")

    def search_contacts(self, search_term: str):
        found = False
        for c in self.contacts_list:
            if search_term == c['name'] or search_term == c['phone']:
                print(f"Found: {c['name']} - {c['phone']}")
                found = True
        
        if not found:
            print("Contact not found.")

    def display_contact_details(self, contact: dict):
        if contact:
            print(f"Detailed View: {contact['name']} | {contact['phone']} | {contact['optionals']}")
        else:
            print("Invalid contact data.")