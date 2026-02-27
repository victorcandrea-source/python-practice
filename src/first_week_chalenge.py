from datetime import datetime, date

while True:
    data_input = input("Enter your date of birth (DD.MM.YYYY.): ")
    try:
        birthdate = datetime.strptime(data_input, "%d.%m.%Y").date()
        break
    except ValueError:
        print("Invalid date format. Please enter the date in the format DD.MM.YYYY.")
name = input("Enter your name: ")
country = input("Enter your country: ")
azi = date.today()
age = azi.year - birthdate.year - ((azi.month, azi.day) < (birthdate.month, birthdate.day))
if age >= 18:
    print(f"Congratulations,{name}, you are old enough to vote in {country}!")
    print(f"Congratulations,{name}, you are old enough to drive in {country}!")
else :
    print(f"Sorry,{name}, you are not old enough to vote in {country}.")
    print(f"Sorry,{name}, you are not old enough to drive in {country}.")