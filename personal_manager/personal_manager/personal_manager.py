import pickle
import re
from collections import UserDict
from datetime import datetime, timedelta
from difflib import get_close_matches
from pathlib import Path
from typing import Dict, List, Optional

from pick import pick

from sort_files import sort_files_entry_point


class InvalidPhoneNumber(Exception):
    """Exception in case of incorrect phone number input"""


class InvalidEmailAddress(Exception):
    """Exception in case of incorrect E-mail input"""


class Field:
    """Field class is a parent for all fields in Record class"""
    def __init__(self, value):
        self.value = value


class Name(Field):
    """Name class for storage name's field"""

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value.capitalize()


class Phone(Field):
    """Phone class for storage phone's field"""

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if len(value) == 13:
            self._value = value
        else:
            raise InvalidPhoneNumber

    def __str__(self) -> str:
        return self.value


class Email(Field):
    """Email class for storage email's field"""

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.__check_email(value):
            self._value = value
        else:
            raise InvalidEmailAddress

    def __check_email(self, email: str) -> bool:
        matched = re.match(r"[a-z][a-z|\d._]{1,}@[a-z]{1,}\.\w{2,}", email, re.IGNORECASE)
        return bool(matched)

    def __str__(self) -> str:
        return self.value


class Tag(Field):
    """Tag class for storage tag's field"""

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Note(Field):
    """Note class for storage note's field"""
    def __init__(self, value, tags: Optional[List[str]] = None):
        super().__init__(value)
        self._created_at = datetime.today()
        self.tag = []
        if tags:
            for one_tag in tags:
                self.tag.append(Tag(one_tag))

    def __str__(self) -> str:
        if self.tag:
            return ", ".join([f"created at {str(self._created_at)}:", \
                self.value, f"tags: {', '.join([tag.value for tag in self.tag])}"])
        else:
            return f"created at {str(self._created_at)}: {self.value}"


class Address(Field):
    """Address class for storage address's field"""

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self) -> str:
        return self.value


class Birthday(Field):
    """Birthday class for storage birthday's field"""

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        try:
            self._value = datetime.strptime(value, "%d.%m.%Y").strftime("%d.%m.%Y")
        except ValueError:
            print(f" \"{value}\" --> Incorrect input format. Record can’t be made.")
            self._value = ''

    def __str__(self) -> str:
        return self.value


class Record:
    """Record class responsible for the logic of adding/removing/editing fields
    Only one name but many phone numbers"""

    def __init__(self, name: str, phone: Optional[List[str]] = None,\
        birthday: Optional[str] = None, address: Optional[List[str]] = None,\
        email: Optional[List[str]] = None, note: Optional[List[str]] = None) -> None:
        self.name = Name(name)
        self.phone = []
        for one_phone in phone:
            try:
                self.phone.append(Phone(one_phone))
            except InvalidPhoneNumber:
                print(f"The phone number \"{one_phone}\" is invalid. Record can’t be made.")
        self.address = []
        for one_address in address:
            self.address.append(Address(one_address))
        self.email = []
        for one_email in email:
            try:
                self.email.append(Email(one_email))
            except InvalidEmailAddress:
                print(f"The email \"{one_email}\" is invalid. Record can’t be made.")
        if birthday:
            self.birthday = Birthday(birthday)
        self.note = []
        for one_note in note:
            self.note.append(Note(one_note))

    def get_phone_index(self, check_number: str) -> Optional[int]:
        """This function returns phone number's index. If number not found - returns None"""
        try:
            return [one_phone.value for one_phone in self.phone].index(check_number)
        except ValueError:
            return None

    def days_to_birthday(self) -> str:
        """Returns how many days left till next birthday"""

        if self.birthday.value:
            current_date = datetime.today().date()
            birthday = datetime.strptime(self.birthday.value, "%d.%m.%Y").replace(year=current_date.year).date()
            if birthday < current_date:
                birthday = birthday.replace(year=birthday.year + 1)
            days = (birthday - current_date).days
            return f"{days} days left till next birthday"
        return ""

    def add_phone(self, phone_number: str) -> None:
        index = self.get_phone_index(phone_number)
        if not index:
            try:
                self.phone.append(Phone(phone_number))
            except InvalidPhoneNumber:
                print(f"The phone number {phone_number} is invalid")

    def delete_phone(self, phone: str) -> None:
        index = self.get_phone_index(phone)
        if index:
            self.phone.pop(index)

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        index = self.get_phone_index(old_phone)
        if index and not self.get_phone_index(new_phone):
            try:
                self.phone[index] = Phone(new_phone)
            except InvalidPhoneNumber:
                print(f"The phone number {new_phone} is invalid")
        else:
            print(f"Old phone \"{old_phone}\" not found or new phone \"{new_phone}\" is already exists")

    def __str__(self) -> str:
        result = []
        for name, obj in self.__dict__.items():
            try:
                result.append(f"{name.upper():<10}: {obj.value}")
            except AttributeError:
                for val in obj:
                    result.append(f"{name.upper():<10}: {val}")
        return "\n".join(result)


class AddressBook(UserDict):
    """Add new instance of Record class in AddressBook"""

    def __get_params(self, params: Dict[str,str], msg: str = None) -> List[str]:
        msg = "Please enter the " if not msg else msg
        params_keys = list(params.keys())
        for index in range(len(params)):
            obj_name = params_keys[index]
            """If one of the parameters specified in the array is requested, 
            the input string must be split by the ";" and convert to array."""
            if obj_name in ["phones", "addresses", "emails", "notes", "tags"]:
                params[obj_name] = input(f"{msg}{obj_name}. Separator symbol for {obj_name} is \";\": ").split(";")
            else:
                params[obj_name] = input(f"{msg}{obj_name}: ")
        return params.values()

    def add_record(self) -> None:
        new_record = Record(*self.__get_params({"name": "", "phones": "", "birthday": "", "addresses": "", "emails": "", "notes": ""}))
        while not new_record.name.value:
            name_value = ''.join(self.__get_params({"name": ""}, "Username not recorded. Please, enter the ")).strip()
            if name_value:
                new_record.name.value = name_value
        while not hasattr(new_record, "birthday") or not new_record.birthday.value:
            birthday_value = ''.join(self.__get_params({"date of birth": ""}, \
                "Date of birth not recorded. Please enter the correct ")).strip()
            if birthday_value:
                new_record.birthday = Birthday(birthday_value)
        self.data[new_record.name.value] = new_record

    def _edit_name(self, record: Record) -> None:
        print(f"The following user names are registered in the address book: {[name for name in self.data]}")
        new_name = ''.join(self.__get_params({"new name of user": ""})).strip().capitalize()
        if new_name:
            if not self.data.get(new_name):
                old_name = record.name.value
                self.data[new_name] = self.data.pop(old_name)
                record.name.value = new_name
            else:
                print(f"The username {new_name} is already registered in the address book. Choose something else.")
        else:
            print("You have not provided a new username.")

    def _edit_phone(self, record: Record) -> None:
        option, index = pick([phone.value for phone in record.phone], \
            "Select the phone number you want to edit.", indicator="=>")
        print(f"You have selected: {option}")
        new_number = ''.join(self.__get_params({"new phone number": ""})).strip()
        if new_number:
            try:
                record.phone[index].value = new_number
            except InvalidPhoneNumber:
                print("You entered an invalid phone number.This data is not recorded.")
        else:
            print("You have not provided a new phone number.")

    def _edit_birthday(self, record: Record) -> None:
        print(f"Current birthday of user \"{record.name.value}\" is: {record.birthday.value}")
        new_birthday = ''.join(self.__get_params({"birthday of user": ""})).strip()
        if new_birthday:
            record.birthday.value = new_birthday
        else:
            print("You have not provided a new birthday.")

    def _edit_address(self, record: Record) -> None:
        option, index = pick([address.value for address in record.address], \
            "Select the address you want to edit.", indicator="=>")
        print(f"You have selected: {option}")
        new_address = ''.join(self.__get_params({"new address": ""})).strip()
        if new_address:
            record.address[index].value = new_address

    def _edit_email(self, record: Record) -> None:
        option, index = pick([email.value for email in record.email], \
            "Select the email you want to edit.", indicator="=>")
        print(f"You have selected: {option}")
        new_email = ''.join(self.__get_params({"new email": ""})).strip()
        if new_email:
            try:
                record.email[index].value = new_email
            except InvalidEmailAddress:
                print("You entered an invalid email address.This data is not recorded.")
        else:
            print("You have not provided a new email.")

    def _edit_tag(self, record: Record) -> None:
        note_option, note_index = pick([note.value for note in record.note], \
            "Select the note for which you want to edit tags.", indicator="=>")
        base_msg = f"You have selected the note {note_option} which contains the following tags: "
        print(f"{base_msg}{[tag.value for tag in record.note[note_index].tag]}")
        new_tags = self.__get_params({"tags": ""})
        if new_tags:
            record.note[note_index].tag = []
            for new_tag in new_tags:
                record.note[note_index].tag.append(Tag(new_tag))

    def edit_record(self) -> None:
        option = pick([name for name in self.data], \
            "Select the name of the user whose data you want to edit.", indicator="=>")[0]
        contact = self.data.get(option)
        if contact:
            function_names = [self._edit_name, self._edit_phone, self._edit_birthday, \
                self._edit_address, self._edit_email, self.edit_note, self._edit_tag]
            description_function = ["Edit user name", "Edit phone", \
                "Edit birthday", "Edit addresses", "Edit emails", \
                "Edit notes", "Edit tags", "FINISH EDITING"]
            base_msg = f"Select what information for the user {contact.name.value} you would like to change.\n{'='*60}"
            option, index = pick(description_function, base_msg, indicator="=>")
            while index != len(description_function)-1:
                print(f"You have selected an {option} option.\nLet's continue.\n{'='*60}")
                function_names[index](contact)
                option, index = pick(description_function, base_msg, indicator="=>")

    def add_tags(self) -> None:
        name_contact = ''.join(self.__get_params({"name of contact": ""})).capitalize()
        contact = self.data.get(name_contact)
        if contact:
            note_index = pick([note.value for note in contact.note], "Select the note where you want to add tags:", indicator="=>")[1]
            tags = contact.note[note_index].tag
            base_msg = f"Specify tags that you want to add to the selected note by {name_contact}. "
            end_msg = f"Separator character for tags is \";\": "
            if tags:
                middle_msg = f"This note already contains the following tags: {[tag.value for tag in tags]}. "
                tags = input(f"{base_msg}{middle_msg}{end_msg}").split(";")
            else:
                tags = input(f"{base_msg}{end_msg}").split(";")
            for tag in tags:
                contact.note[note_index].tag.append(Tag(tag))
        else:
            print(f"The user {name_contact} was not found in the address book.")

    def del_contact(self) -> None:
        name_contact = ''.join(self.__get_params({"contact": ""})).capitalize()
        if self.data.get(name_contact):
            self.data.pop(name_contact)
            print(f"Contact {name_contact} was removed!")
        else:
            print(f"Contact {name_contact} not found!")

    def holidays_period(self) -> None:
        result = []
        try:
            period = int(''.join(self.__get_params({"period": ""})))
        except ValueError:
            print('Only number allowed!')
        else:
            if period > 365:
                period = 365
            day_today = datetime.now()
            day_today_year = day_today.year
            end_period = day_today + timedelta(days=period+1)
            print(f"Found birthdays for {period} days period: ")
            for name, rec in self.data.items():
                date = datetime.strptime(rec.birthday.value, '%d.%m.%Y').replace(year=end_period.year)
                if day_today_year < end_period.year:
                    if day_today <= date.replace(year=day_today_year) or date <= end_period:
                        result.append(f"{name}: {rec}")
                else:
                    if day_today <= date.replace(year=day_today_year) <= end_period:
                        result.append(f"{name}: {rec}")
            if not result:
                result.append(f"No contacts with birthdays for this period.")
            print('\n'.join(result))

    def find_contact(self) -> None:
        search_info = ''.join(self.__get_params({"search info": ""}))
        result = [f"Search results for string \"{search_info}\": "]
        flag_found = False
        for name, rec in self.data.items():
            phones = [one_phone.value for one_phone in rec.phone]
            notes = [one_note.value for one_note in rec.note]
            emails = [one_email.value for one_email in rec.email if search_info in one_email.value]
            if search_info in phones or \
                    len(list(filter(lambda one_phone: one_phone.startswith(search_info), phones))) or \
                    search_info.capitalize() in name or \
                    search_info in rec.birthday.value or search_info in notes or emails:
                result.append(f"{name}, {rec}")
                flag_found = True
        if not flag_found:
            result.append("No information found.")
        print('\n'.join(result))

    def sort_files(self) -> str:
        return sort_files_entry_point((''.join(self.__get_params({"path": ""}))))

    def iterator(self, n: str = 1) -> List[str]:
        separator, enter = "="*60, "\n"
        yield from ([f"{separator}: {enter}{rec}" for name, \
            rec in list(self.items())[i: i + n]] for i in range(0, len(self), n))

    def save_data(self, filename: str) -> None:
        try:
            with open(filename, "wb") as fn:
                pickle.dump(self.data, fn)
            print(f"Saving to file \"{filename}\" is successful")
        except (FileNotFoundError, AttributeError, MemoryError):
            print(f"An error occurred while saving the file \"{filename}\"")

    def load_data(self, filename: str) -> None:
        try:
            with open(filename, 'rb') as fn:
                self.data = pickle.load(fn)
            print(f"Loading from file \"{filename}\" is successful")
        except (FileNotFoundError, AttributeError, MemoryError):
            print(f"An error occurred while opening the file \"{filename}\"")

    def _find_contact(self, message: str) -> Optional[Record]:
        name_contact = ''.join(self.__get_params({message: ""})).capitalize()
        record: Optional[Record] = self.data.get(name_contact)
        if record:
            return record
        print("There is no contact with provided name.")

    def print_record_notes(self, record: Record) -> None:
        if record:
            if record.note:
                for note in record.note:
                    print(note)

    def add_note(self) -> None:
        record = self._find_contact("contact to add a note")
        if record:
            note, tags = self.__get_params({"note": "", "tags": ""})
            record.note.append(Note(note, tags))
            print("Note was added.")

    def print_notes(self) -> None:
        record = self._find_contact("contact to display")
        if record:
            self.print_record_notes(record)

    def edit_note(self, rec: Optional[Record] = None) -> None:
        record = rec
        if not record:
            record = self._find_contact("contact to edit")
        if record:
            notes = [note.value for note in record.note]
            index = pick(notes, "Select the note you want to edit.", indicator="=>")[1]
            note, tags = self.__get_params({"note": "", "tags": ""})
            record.note[index] = Note(note, tags)
            print("Note was edited.")

    def del_note(self) -> None:
        record = self._find_contact("contact")
        if record:
            notes = [note.value for note in record.note]
            index = pick(notes, "Select the note you want to delete.", indicator="=>")[1]
            del record.note[index]
            print("Note was deleted.")

    def find_sort_note(self) -> None:
        found_tag = False
        tag_name = "".join(self.__get_params({"tag name": ""}))
        for name, rec in self.data.items():
            filtered_notes = []
            for note in rec.note:
                if tag_name in [tag.value for tag in note.tag]:
                    filtered_notes.append(note)
                    found_tag = True
            for sorted_note in sorted(filtered_notes, key=lambda note: note._created_at, reverse=True):
                print(sorted_note)
        if not found_tag:
            print("Sorry, we could not find notes for the tag you specified.")

    def show_contacts(self, items_count: str = 1):
        for contacts in self.iterator(items_count):
            print(*contacts)

    def show_commands(self) -> None:
        """Displaying commands with the ability to execute them"""

        option, index = pick(commands_desc, \
            f"Command name and description. Select command.\n{'='*60}", indicator="=>")
        print(f"You have chosen a command: {option}.\nLet's continue.\n{'='*60}")
        functions_list[index]()


class CommandHandler:

    def __call__(self, command: str) -> bool:
        if command in exit_commands:
            return False
        elif command in action_commands:
            commands_func[command]()
            return True
        command = get_close_matches(command, action_commands + exit_commands)
        in_exit = not set(command).isdisjoint(exit_commands)
        if in_exit:
            return False
        in_action = not set(command).isdisjoint(action_commands)
        if in_action:
            if len(command) == 1:
                commands_func[command[0]]()
            elif len(command) > 1:
                command = pick(command, TITLE, indicator="=>")[0]
                print(f"You have selected the {command} command. Let's continue.")
                commands_func[command]()
        else:
            print("Sorry, I could not recognize this command!")
        return True


book = AddressBook()
TITLE = "We have chosen several options from the command you provided.\nPlease choose the one that you need."
action_commands = ["help", "add_contact", "edit_record", "holidays_period", "print_notes", "add_note", \
    "edit_note", "del_note", "find_note", "add_tag", "sort_files", "find_contact", "del_contact", "show_contacts"]
description_commands = ["Display all commands", "Add user to the address book", \
    "Edit information for the specified user", "Amount of days where we are looking for birthdays", \
    "Show notes for the specified user", "Add notes to the specified user", "Edit the notes for the specified user", \
    "Delete the notes for the specified user", "Find notes for specified user", \
    "Add tag for the specified user", "Sorts files in the specified directory", \
    "Search for the specified user by name", "Delete the specified user", \
    "Show all contacts in address book", "Exit from program"]
exit_commands = ["good_bye", "close", "exit"]
functions_list = [book.show_commands, book.add_record, book.edit_record, book.holidays_period, \
    book.print_notes, book.add_note, book.edit_note, book.del_note, book.find_sort_note, book.add_tags, \
    book.sort_files, book.find_contact, book.del_contact, book.show_contacts, exit]
commands_func = {cmd: func for cmd, func in zip(action_commands, functions_list)}
commands_desc = [f"{cmd:<15} -  {desc}" for cmd, desc in zip(action_commands + [', '.join(exit_commands)], description_commands)]

if __name__ == "__main__":
    current_script_path = Path(__file__).absolute()
    file_bin_name = f"{current_script_path.stem}.bin"
    data_file = current_script_path.parent.joinpath(file_bin_name)
    """get data file from current directory"""
    book.load_data(data_file)
    command = CommandHandler()
    input_msg = input("Hello, please enter the command: ").lower().strip()
    while command(input_msg):
        input_msg = input("Please enter the command: ").lower().strip()
    book.save_data(data_file)
    print("Have a nice day... Good bye!")

