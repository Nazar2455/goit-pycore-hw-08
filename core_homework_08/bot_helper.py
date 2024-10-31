from collections import UserDict
from datetime import datetime, timedelta
import re
import pickle

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        self.value = value.strip()

    def value(self):
        return self._value()

class Birthday(Field):
    def __init__(self, value):
        date_pattern = r"^\d{2}\.\d{2}\.\d{4}$"

        if not re.match(date_pattern, value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

        try:
            date_object = datetime.strptime(value, "%d.%m.%Y")

            if not (1 <= date_object.month <= 12):
                raise ValueError("Invalid month. Month must be between 1 and 12.")
            
            current_year = datetime.now().year

            if date_object.year > current_year or date_object.year <= 0:
                raise ValueError(f"Invalid year. Year must be between 1 and {current_year}.")

            if date_object.year >= 2025:
                raise ValueError("Year cannot be 2025 or more.")

            if date_object > datetime.now():
                raise ValueError("Birthday cannot be in the future.")
            
            self.value = value
        except ValueError:
            raise ValueError("Invalid date. Make sure the date is real.")

class Phone(Field):
    def __init__(self, value):
        self._validate_phone(value)
        super().__init__(value)

    def _validate_phone(self, phone):
        if not phone.isdigit():
            raise ValueError(f"Phone number must contain only digits. Provided: {phone}")
        if len(phone) != 10:
            raise ValueError(f"Phone number must contain exactly 10 digits. Provided: {phone}")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_to_remove = None
        for p in self.phones:
            if p.value == phone:
                phone_to_remove = p
                break
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
            raise ValueError(f"Phone {phone} not found.")

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = None
        for p in self.phones:
            if p.value == old_phone:
                phone_to_edit = p
                break
        if phone_to_edit:
            if old_phone == new_phone:
                raise ValueError("New phone number cannot be the same as the old one.")
            if not new_phone.isdigit():
                raise ValueError(f"Phone number must contain only digits. Provided: {new_phone}")
            if len(new_phone) != 10:
                raise ValueError(f"Phone number must contain exactly 10 digits. Provided: {new_phone}")
            phone_to_edit.value = new_phone
        else:
            raise ValueError(f"Phone {old_phone} not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones) if self.phones else "No phones"
        birthday = self.birthday.value if self.birthday else "No birthday"
        return f"Contact name: {self.name.value}, Phones: {phones}, Birthday: {birthday}"

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)
        
    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Record with name '{name}' not found.")
        
    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        next_week = today + timedelta(days=7)

        upcoming_birthdays = []

        for name, record in self.data.items():
            if record.birthday:
                birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y")
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year.date() < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if today <= birthday_this_year.date() <= next_week:
                    if birthday_this_year.weekday() == 5:
                        birthday_this_year += timedelta(days=2)
                    elif birthday_this_year.weekday() == 6:
                        birthday_this_year += timedelta(days=1)

                    upcoming_birthdays.append({
                        "name": name,
                        "birthday": birthday_this_year.strftime("%d.%m.%Y")
                    })
        
        return upcoming_birthdays

    def __str__(self):
        if not self.data:
            return "Address Book is empty."

        result = []
        for record in self.data.values():
            phones = ', '.join(phone.value for phone in record.phones) if record.phones else "No phones"
            birthdays = record.birthday.value if record.birthday else "No birthday"
            result.append(f"Name: {record.name.value}, Phones: {phones}, Birthday: {birthdays}")
        
        return "\n".join(result)

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Error: {str(e)}"
        except IndexError:
            return "Enter the argument for the command"
        except KeyError:
            return "No element with this key"

    return inner

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return f"Contact {name} not found."
    record.edit_phone(old_phone, new_phone)
    return "Contact changed"

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return f"Contact {name} not found."
    return f"Phones for {name}: {', '.join(phone.value for phone in record.phones)}"

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if not record:
        return f"Contact {name} not found."
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return f"Contact {name} not found"
    return record.birthday

@input_error
def birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    
    if not upcoming_birthdays:
        return "No upcoming birthdays in the next 7 days."

    result = ["Upcoming Birthdays:"]
    for birthday_info in upcoming_birthdays:
        name = birthday_info["name"]
        birthday = datetime.strptime(birthday_info["birthday"], "%d.%m.%Y").date()
        days_left = (birthday - datetime.today().date()).days
        result.append(f"{name} - {birthday.strftime('%d.%m.%Y')} (in {days_left} days)")
    
    return "\n".join(result)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "all":
            if not book:
                print("No contacts found.")
            print(str(book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            if not book:
                print("No contacts found.")
            print(birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()