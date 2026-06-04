import pickle
from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def edit_phone(self, old_number, new_number):
        phone_to_edit = self.find_phone(old_number)
        if not phone_to_edit:
            raise ValueError(f"Phone number {old_number} not found.")
        new_phone = Phone(new_number)
        idx = self.phones.index(phone_to_edit)
        self.phones[idx] = new_phone

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday_string):
        self.birthday = Birthday(birthday_string)

    def __str__(self):
        birthday_info = f", birthday: {self.birthday}" if self.birthday else ""
        phones_info = ", ".join(p.value for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_info}{birthday_info}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today().date()

        for record in self.data.values():
            if not record.birthday:
                continue

            bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            bday_this_year = bday.replace(year=today.year)

            if bday_this_year < today:
                bday_this_year = bday_this_year.replace(year=today.year + 1)

            if today <= bday_this_year <= today + timedelta(days=6):
                congratulation_date = bday_this_year

                if congratulation_date.weekday() == 5:  # Субота
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:  # Неділя
                    congratulation_date += timedelta(days=1)

                upcoming_birthdays.append({
                    "name": record.name.value,
                    "birthday": congratulation_date.strftime("%d.%m.%Y")
                })

        return upcoming_birthdays

    def __str__(self):
        if not self.data:
            return "Address book is empty."
        return "\n".join(str(record) for record in self.data.values())


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return AddressBook()


#
# if __name__ == "__main__":
#     book = AddressBook()
#
#     john_record = Record("John")
#     john_record.add_phone("1234567890")
#     john_record.add_phone("5555555555")
#
#     book.add_record(john_record)
#
#     jane_record = Record("Jane")
#     jane_record.add_phone("9876543210")
#     book.add_record(jane_record)
#
#     print(book)
#
#     john = book.find("John")
#     john.edit_phone("1234567890", "1112223333")
#
#     print(john)
#
#     found_phone = john.find_phone("5555555555")
#     print(f"{john.name}: {found_phone}")
#
#     book.delete("Jane")


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e) if str(e) else "Give me name and phone please."
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Enter user name."

    return inner


def parse_input(user_input):
    if not user_input.strip():
        return "", []
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 1:
        raise IndexError
    name = args[0]
    phone = args[1] if len(args) > 1 else None

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
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    return f"{name}: {'; '.join(p.value for p in record.phones)}"


def show_all(book: AddressBook):
    return str(book)


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record or not record.birthday:
        return f"Birthday for contact '{name}' not found."
    return f"{name}'s birthday: {record.birthday}"


def birthdays(book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays next week."
    return "\n".join(f"{item['name']}: celebrate on {item['birthday']}" for item in upcoming)


def main():

    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        elif command == "":
            continue

        else:
            print("Invalid command.")

    save_data(book)


if __name__ == "__main__":
    main()
