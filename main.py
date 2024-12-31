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
    def is_valid(self):
        return self.value.isdigit() and len(self.value) == 10
    
class Birthday(Field):
    def __init__(self, value):
      if not value:
          raise ValueError("Birthday value cannot be None.")
      try:
          self.value = datetime.strptime(value, "%d.%m.%Y")
      except ValueError:
          raise ValueError("Invalid date format. Use DD.MM.YYYY")        
        
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birhday: {self.birthday.value.strftime('%d.%m.%Y') if self.birthday else "Not avaliable"}"

    def add_phone(self, phone_value):
        phone = Phone(phone_value)
        if phone.is_valid():
            self.phones.append(phone)
        else:
            raise ValueError("Phone number should contain exactly 10 digits.")
        
    def add_birthday(self, bd_date):
        birthday = Birthday(bd_date)
        if birthday:
            self.birthday =  birthday
            return f"Birthday was added."

    def remove_phone(self, phone_value):
        phone = self.find_phone(phone_value)
        if phone:
            self.phones.remove(phone)
            return f"Phone {phone_value} removed."
        raise ValueError(f"Phone {phone_value} not found.")

    def edit_phone(self, old_phone_value, new_phone_value):
        phone = self.find_phone(old_phone_value)
        if phone:
            if not Phone(new_phone_value).is_valid():
                raise ValueError("New phone number should contain exactly 10 digits.")
            phone.value = new_phone_value
            return f"Phone {old_phone_value} changed to {new_phone_value}."
        raise ValueError(f"Phone {old_phone_value} not found.")

    def find_phone(self, phone_value):
        for phone in self.phones:
            if phone.value == phone_value:
                return phone
        return None

class AddressBook(UserDict):
    def __init__(self):
        super().__init__()

    def add_record(self, record):
        if not isinstance(record, Record):
            raise TypeError("Only Record objects can be added.")
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        record = self.find(name)
        if record:
            del self.data[name]
            return f"Record for {name} deleted."
        raise ValueError(f"Record for {name} not found.")
    
    def get_upcoming_birthdays(self):
        current_day = datetime.today().date()
        one_week_later = current_day + timedelta(days=7)

        birthdays_next_week = {}

        for record in self.data.values():
          if record.birthday:
              birthday_date = record.birthday.value.date()
              birthday_this_year = birthday_date.replace(year=current_day.year)

              if birthday_this_year < current_day:
                  birthday_this_year = birthday_this_year.replace(year=current_day.year + 1)

              if current_day <= birthday_this_year <= one_week_later:
                  weekday = birthday_this_year.strftime("%A") 
                  if weekday not in birthdays_next_week:
                      birthdays_next_week[weekday] = []
                  birthdays_next_week[weekday].append(record.name.value)
        return birthdays_next_week

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError) as e:
            print(e)
    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_contact(args, book):
    if len(args) < 1:
        raise ValueError("Please provide a name.")
    name = args[0]
    phone = args[1] if len(args) > 1 else None
    if name not in book:
        book.add_record(Record(name))
    if phone:
        book.find(name).add_phone(phone)
    print(f"Contact {'updated' if phone else 'added'}: {name}")

@input_error
def change_contact(args, book):
    if len(args) < 3:
        raise ValueError("Please provide a name, the phone number to edit, and the new phone number.")
    name, old_phone, new_phone = args
    if name in book:
        print(book[name].edit_phone(old_phone, new_phone))
    else:
        raise KeyError(f"Name '{name}' not found in contacts.")

@input_error
def remove_phone(args, book):
    if len(args) < 2:
        raise ValueError("Please provide both a name and a phone number to remove.")
    name, phone = args
    if name in book:
        print(book[name].remove_phone(phone))
    else:
        raise KeyError(f"Name '{name}' not found in contacts.")


def show_all(book):
    if book:
        print("Contacts list:")
        for name, phone in book.items():
            print(f"{name}: {phone}")
    else:
        print("Contact list is empty.")

@input_error
def add_birthday_data(args, book):
    if len(args) < 2:
        raise ValueError("Please provide a name and Birthday date.")
    name = args[0]
    birthday = args[1] if len(args) > 1 else None
    if name in book:
        print(book[name].add_birthday(birthday))
    else:
        raise KeyError(f"Name '{name}' not found in contacts.")

@input_error
def show_birthday(args, book):
    if len(args) < 1:
        raise ValueError("Please provide a name.")
    name = args[0]
    data = book.find(name)
    if data:
        if data.birthday and data.birthday.value:
            print(f"Birthday date for '{name}' is {data.birthday.value.strftime('%d.%m.%Y')}")
        else:
            print(f"'{name}' does not have a birthday set.")
    else:
        raise KeyError(f"Contact '{name}' not found in the address book.")

def all_birthdays(book):
    if book:
        try:
            upcoming = book.get_upcoming_birthdays()
            if upcoming:
                print("Upcoming Birthdays:")
                for day, names in upcoming.items():
                    print(f"{day}: {', '.join(names)}")
            else:
                print("No upcoming birthdays in the next week.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("Contact list is empty.")



def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Goodbye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            add_contact(args, book)
        elif command == "change":
            change_contact(args, book)
        elif command == "remove_phone":
            remove_phone(args, book)
        elif command == "all":
            show_all(book)
        elif command == "add-birthday":
            add_birthday_data(args, book)
        elif command == "show-birthday":
            show_birthday(args, book)
        elif command == "birthdays":
            all_birthdays(book)
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
