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
    """Exception for phone number verification."""


class InvalidEmailAddress(Exception):
    """Exception for email verification"""

class Field:
    """Field class is parent for all fields in Record class"""
    def __init__(self, value):
        self.value = value


class Name(Field):
    """Name class for storage name"s field"""

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value.capitalize()


class Phone(Field):
    """Phone class for storage phone"s field"""

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
        return f"Phone: {self.value}"


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
        return f"Email: {self.value}"


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
            return f"note (created: {self._created_at}): {self.value}, tags: {[tag.value for tag in self.tag]}"
        else:
            return f"note (created: {self._created_at}): {self.value}"


class Address(Field):
    """Address class for storage address's field"""

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self) -> str:
        return f"Address: {self.value}"


class Birthday(Field):
    """Birthday class for storage birthday"s field"""

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        try:
            self._value = datetime.strptime(value, "%d.%m.%Y").strftime("%d.%m.%Y")
        except ValueError:
            print(f"Date of birth \"{value}\" is indicated incorrectly. It was not recorded.")
            self._value = ''


class Record:
    """Record class responsible for the logic of adding/removing/editing fields
    Only one name but many phone numbers"""

    def __init__(self, name: str, phone: Optional[List[str]] = None, birthday: Optional[str] = None, address: Optional[List[str]] = None, email: Optional[List[str]] = None, note: Optional[List[str]] = None) -> None:
        self.name = Name(name)
        self.phone = []
        for one_phone in phone:
            try:
                self.phone.append(Phone(one_phone))
            except InvalidPhoneNumber:
                print(f"The phone number \"{one_phone}\" is invalid. It was not recorded.")
        self.address = []
        for one_address in address:
            self.address.append(Address(one_address))
        self.email = []
        for one_email in email:
            try:
                self.email.append(Email(one_email))
            except InvalidEmailAddress:
                print(f"The email \"{one_email}\" is invalid. It was not recorded.")
        if birthday:
            self.birthday = Birthday(birthday)
        self.note = []
        for one_note in note:
            self.note.append(Note(one_note))

    def get_phone_index(self, check_number: str) -> Optional[int]:
        """The function checks the user"s phone number. If the number is found, it returns its index; otherwise, None is."""
        try:
            return [one_phone.value for one_phone in self.phone].index(check_number)
        except ValueError:
            return None

    def days_to_birthday(self) -> str:
        """return number of days until the next birthday"""

        if self.birthday.value:
            current_date = datetime.today().date()
            birthday = datetime.strptime(self.birthday.value, "%d.%m.%Y").replace(year=current_date.year).date()
            if birthday < current_date:
                birthday = birthday.replace(year=birthday.year + 1)
            days = (birthday - current_date).days
            return f"{days}"
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
            print(f"Old phone \"{old_phone}\" not found or new phone \"{new_phone}\" is present")

    def __str__(self) -> str:
        result = f"Record of {self.name.value}"
        if self.phone:
            for one_phone in self.phone:
                result += f": {one_phone}"
        if self.address:
            for one_address in self.address:
                result += f", {one_address}"
        if self.email:
            for one_email in self.email:
                result += f", {one_email}"
        if self.birthday.value:
            result += f", Birthday: {self.birthday.value}"
            result += f", From current date to birthday: {self.days_to_birthday()} day(s)"
        for one_note in self.note:
            result += f", {one_note}"
        return result

class AddressBook(UserDict):
    """Add new instance of Record class in AddressBook"""

    def __get_params(self, params: Dict[str,str]) -> List[str]:
        msg = "Please enter the "
        params_keys = list(params.keys())
        for index in range(len(params)):
            obj_name = params_keys[index]
            """If one of the parameters specified in the array is requested, the input string must be split by the ";" and convert to array."""
            if obj_name in ["phone", "address", "email", "notes", "tags"]:
                params[obj_name] = input(f"{msg}{obj_name}. Separator character for {obj_name} is \";\": ").split(";")
            else:
                params[obj_name] = input(f"{msg}{obj_name}: ")
        return params.values()

    def add_record(self) -> None:
        new_record = Record(*self.__get_params({"name": "", "phone": "", "birthday": "", "address": "", "email": "", "notes": ""}))
        self.data[new_record.name.value] = new_record

    def add_tags(self) -> None:
        name_contact = ''.join(self.__get_params({"name of contact": ""})).capitalize()
        contact = self.data.get(name_contact)
        if contact:
            note_index = pick([note.value for note in contact.note], "Select the note where you want add tags:", indicator="=>")[1]
            tags = contact.note[note_index].tag
            if tags:
                tags = input(f"Specify the tags that you want to add to the selected note by {name_contact}. This note already contains the following tags: {[tag.value for tag in tags]}. Separator character for tags is \";\": ").split(";")
            else:
                tags = input(f"Specify the tags that you want to add to the selected note by {name_contact}. Separator character for tags is \";\": ").split(";")
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
            print(f"Search results for birthdays for a period of {period} days:")
            for name, rec in self.data.items():
                date = datetime.strptime(rec.birthday.value, '%d.%m.%Y').replace(year=end_period.year)
                if day_today_year < end_period.year:
                    if day_today <= date.replace(year=day_today_year) <= end_period or day_today <= date <= end_period:
                        result.append(f"{name}: {rec}")
                else:
                    if day_today <= date.replace(year=day_today_year) <= end_period:
                        result.append(f"{name}: {rec}")
            if not result:
                result.append(f"No contacts found with birthdays for the specified period.")
            print('\n'.join(result))

    def find_contact(self) -> None:
        search_info = ''.join(self.__get_params({"search info": ""}))
        result = [f"Search results for string \"{search_info}\":"]
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
        yield from ([f"{name}: {rec}" for name, rec in list(self.items())[i: i + n]] for i in range(0, len(self), n))

    def save_data(self, filename: str) -> None:
        try:
            with open(filename, "wb") as fn:
                pickle.dump(self.data, fn)
            print(f"Saving to file \"{filename}\" is successfully")
        except (FileNotFoundError, AttributeError, MemoryError):
            print(f"An error occurred while saving the file \"{filename}\"")

    def load_data(self, filename: str) -> None:
        try:
            with open(filename, 'rb') as fn:
                self.data = pickle.load(fn)
            print(f"Loading from file \"{filename}\" is successfully")
        except (FileNotFoundError, AttributeError, MemoryError):
            print(f"An error occurred while opening the file \"{filename}\"")

    def _find_contact(self, message: str) -> Optional[Record]:
        name_contact = ''.join(self.__get_params({message: ""})).capitalize()
        record: Optional[Record] = self.data.get(name_contact)
        if record:
            return record
        print("There is no contact with proved name.")

    def print_record_notes(self, record: Record) -> None:
        if record:
            if len(record.note) == 0:
                print("There is no notes for this contact.")
            else:
                for index, note in enumerate(record.note):
                    print(f"[{index}] {note}")

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

    def edit_note(self) -> None:
        record = self._find_contact("contact to edit")
        if record:
            print("Notes:")
            self.print_record_notes(record)
            index = int(''.join(self.__get_params({"note index you want to edit": ""})))
            if index >= len(record.note) or index < 0:
                print("Provided index is invalid")
            else:
                note, tags = self.__get_params({"note": "", "tags": ""})
                record.note[index] = Note(note, tags)
                print("Note was edited.")

    def del_note(self) -> None:
        record = self._find_contact("contact")
        if record:
            print("Notes:\n")
            self.print_record_notes(record)
            index = int(''.join(self.__get_params({"note index you want to delete": ""})))
            if index >= len(record.note) or index < 0:
                print("Provided index is invalid")
            else:
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

    def show_commands(self) -> None:
        """Displaying commands with the ability to execute them"""

        option, index = pick(commands_desc, f"Command name and description. Select a command and it will be executed.\n{'='*60}", indicator="=>")
        print(f"You have chosen a command: {option}.\nLet's continue.\n{'='*60}")
        functions_list[index]()


class CommandHandler:

    def __call__(self, command: str) -> bool:
        cmd = command
        if cmd in exit_commands:
            return False
        elif cmd in action_commands:
            commands_func[cmd]()
            return True
        cmd = get_close_matches(cmd, action_commands + exit_commands)
        in_exit = not set(cmd).isdisjoint(exit_commands)
        if in_exit:
            return False
        in_action = not set(cmd).isdisjoint(action_commands)
        if in_action:
            if len(cmd) == 1:
                commands_func[cmd[0]]()
            elif len(cmd) > 1:
                cmd = pick(cmd, TITLE, indicator="=>")[0]
                print(f"You have selected the {cmd} command. Let's continue.")
                commands_func[cmd]()
        else:
            print("Sorry, I could not recognize the entered command!")
        return True


def  cmd_edit_contact():
    print("Sorry, command not implemented :)")

book = AddressBook()
TITLE = "We have chosen several options from the command you provided.\nPlease choose the one that you need."
action_commands = ["help", "add_contact", "holidays_period", "print_notes", "add_note", "edit_note", "del_note", "find_note", "add_tag", "sort_files", "find_contact", "edit_contact", "del_contact"]
description_commands = ["Display all commands", "Adding a user to the address book", "The number of days from today where we are looking for birthdays", "Show notes of the specified user", "Add notes to the specified user", "Edit the notes of the specified user", "Delete the notes of the specified user", "Search for the notes of the specified user", "Add tag for the specified user", "Sorts files in the specified directory", "Search for the specified contact by name", "Editing the data of the specified contact", "Delete the specified contact", "Exit from program"]
exit_commands = ["good_bye", "close", "exit"]
functions_list = [book.show_commands, book.add_record, book.holidays_period, book.print_notes, book.add_note, book.edit_note, book.del_note, book.find_sort_note, book.add_tags, book.sort_files, book.find_contact, cmd_edit_contact, book.del_contact, exit]
commands_func = {cmd: func for cmd, func in zip(action_commands, functions_list)}
commands_desc = [f"{cmd:<15} -  {desc}" for cmd, desc in zip(action_commands + [', '.join(exit_commands)], description_commands)]

if __name__ == "__main__":
    current_script_path = Path(__file__).absolute()
    file_bin_name = f"{current_script_path.stem}.bin"
    data_file = current_script_path.parent.joinpath(file_bin_name)
    """get data file from current directory"""
    book.load_data(data_file)
    cmd = CommandHandler()
    input_msg = input("Hello, please enter the command: ").lower().strip()
    while cmd(input_msg):
        input_msg = input("Please enter the command: ").lower().strip()
    book.save_data(data_file)
    print("Have a nice day... Good bye!")
