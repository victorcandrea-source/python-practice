from contact_manager import ContactManager
manager = ContactManager()

# Adăugăm câteva contacte
john = manager.add_contact("John Doe", "1234567890", email="john.doe@example.com")
jane = manager.add_contact("Jane Smith", "0987654321", email="jane.smith@example.com")
popescu = manager.add_contact("Popescu Ion", "5555555555", email="popescu.ion@example.com")
maria = manager.add_contact("Maria Popescu", "4444444444", email="maria.popescu@example.com")

#Afisam toate contactele
manager.list_all_contacts()

# Căutăm un contact după nume
manager.search_contacts("John Doe")

# Căutăm un contact după telefon
manager.search_contacts("0987654321")

# Căutăm un contact inexistent
manager.search_contacts("Nonexistent Contact")

# Afișăm detaliile unui contact specific
manager.display_contact_details(john)

print("bye bye!! :D")