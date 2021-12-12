import pickle
import re
from collections import UserDict
from datetime import datetime, timedelta
from difflib import get_close_matches
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from sort_files import sort_files_entry_point
from pick import pick

"""standard_input is used to simulate user input. Use in vscode."""
def standard_input():
    yield "add_contact"
    yield "Vasya"
    yield "067-342-54-22;123-567-01-02;456-123-34-56"
    yield "09.01.1990"
    yield "Lvivska st., Lviv, 32/56;Kyivska st., Kyiv, 56/42"
    yield "This is first note in record;This is second note in record"
    yield "add_contact"
    yield "Petya"
    yield "066-142-44-11;096-342-33-76;044-322-11-43"
    yield "23.11.2003"
    yield "Orlova st., Lviv, 22/134;Uzviz st., Kyiv, 156/24"
    yield "I'll be in Lviv for a coffee.;I will be in Kiev, I will go to Khreshchatyk."
    yield "holidays_period"
    yield "30"
    yield "add_tag"
    yield "Vasya"
    yield "tag-1;tag-2"
    yield "add_tag"
    yield "Vasya"
    yield "tag-3;tag-4"
    yield "add_tag"
    yield "Petya"
    yield "coffee;Khreshchatyk"
    yield "exit"


class InvalidPhoneNumber(Exception):
    """Exception for phone number verification."""


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

    def __str__(self):
        return f"Phone: {self.value}"


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
        self.__created_at = datetime.today()
        self.tag = []
        if tags:
            for one_tag in tags:
                self.tag.append(Tag(one_tag))

    def __str__(self):
        if self.tag:
            return f"note (created: {self.__created_at}): {self.value}, tags: {'; '.join(self.tag)}"
        else:
            return f"note (created: {self.__created_at}): {self.value}"


class Address(Field):
    """Address class for storage address's field"""

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self):
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

    def __init__(self, name: str, phone: Optional[List[str]] = None, birthday: Optional[List[str]] = None, address: Optional[List[str]] = None, note: Optional[List[str]] = None) -> None:
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
            return f"{days} day(s)"
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

    def __str__(self):
        result = f"Record of {self.name.value}"
        if self.phone:
            for one_phone in self.phone:
                result += f": {one_phone}"
        if self.address:
            for one_address in self.address:
                result += f", {one_address}"
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
            if obj_name in ["phone", "address", "note"]:
                params[obj_name] = input(f"{msg}{obj_name}. Separator character for {obj_name} is \";\": ").split(";")
            else:
                params[obj_name] = input(f"{msg}{obj_name}: ")
        return params.values()

    def add_record(self) -> None:
        new_record = Record(*self.__get_params({"name": "", "phone": "", "birthday": "", "address": "", "note": ""}))
        self.data[new_record.name.value] = new_record

    def add_tags(self) -> None:
        name_contact = ''.join(self.__get_params({"name of contact": ""})).capitalize()
        contact = self.data.get(name_contact)
        if contact:
            note_index = pick([note.value for note in contact.note], "Select the note where you want add tags:", indicator="=>")[1]
            tags = contact.note[note_index].tag
            if tags:
                tags = input(f"Specify the tags that you want to add to the selected note by {name_contact}. This note already contains the following tags: {tags}. Separator character for tags is \";\": ").split(";")
                contact.note[note_index].tag.extend(tags)
            else:
                tags = input(f"Specify the tags that you want to add to the selected note by {name_contact}. Separator character for tags is \";\": ").split(";")
                contact.note[note_index].tag = tags
        else:
            print(f"The user {name_contact} was not found in the address book.")

    def del_contact(self) -> None:
        contact = ''.join(self.__get_params({"contact": ""}))
        contact = contact.capitalize()
        if self.data.get(contact):
            self.data.pop(contact)
            print(f"Contact {contact} was removed!")
        else:
            print(f"Contact {contact} not found!")

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

    def find_record(self, value: str) -> Optional[Record]:
        return self.data.get(value.capitalize())

    def delete_record(self, value: str) -> None:
        value = value.capitalize()
        if self.data.get(value):
            self.data.pop(value)

    def find_info(self, search_info: str) -> str:
        result = [f"Search results for string \"{search_info}\":"]
        flag_found = False
        for name, rec in self.data.items():
            phones = [one_phone.value for one_phone in rec.phone]
            if search_info in phones or \
                    len(list(filter(lambda one_phone: one_phone.startswith(search_info), phones))) or \
                    search_info.capitalize() in name or \
                    search_info in rec.birthday.value:
                result.append(f"{name}, {rec}")
                flag_found = True
        if not flag_found:
            result.append("No information found.")
        return '\n'.join(result)

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


def  cmd_save_note():
     ''''''
def  cmd_edit_note():
    ''''''
def  cmd_del_note():
     ''''''
def  cmd_sort_note():
    ''''''
def  cmd_find_note():
    ''''''
def  cmd_find_contact():
    ''''''
def  cmd_edit_contact():
    ''''''

book = AddressBook()
TITLE = "We have chosen several options from the command you provided.\nPlease choose the one that you need."
action_commands = ["add_contact", "holidays_period", "save_note ", "edit_note", "del_note", "sort_note", "find_note", "add_tag", "sort_files", "find_contact", "edit_contact", "del_contact"]
exit_commands = ["good_bye", "close", "exit"]
functions_list = [book.add_record, book.holidays_period, cmd_save_note, cmd_edit_note, cmd_del_note, cmd_sort_note, cmd_find_note, book.add_tags, book.sort_files, cmd_find_contact, cmd_edit_contact, book.del_contact]
commands_func = {cmd: func for cmd, func in zip(action_commands, functions_list)}

if __name__ == "__main__":
    current_script_path = Path(__file__).absolute()
    file_bin_name = f"{current_script_path.stem}.bin"
    data_file = current_script_path.parent.joinpath(file_bin_name)
    """get data file from current directory"""
    book.load_data(data_file)
    cmd = CommandHandler()
    #re.sub(r" +", " ", input("Hello, please enter the command: ")
    input_msg = input("Hello, please enter the command: ").lower().strip()
    while cmd(input_msg):
        input_msg = input("Please enter the command: ").lower().strip()
    print("Have a nice day... Good bye!")
    book.save_data(data_file)

    for rec in book.iterator(2):
        print(rec)
