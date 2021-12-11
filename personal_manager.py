import pickle
import re
from collections import UserDict
from datetime import datetime, timedelta
from difflib import get_close_matches
from pathlib import Path
from typing import List, Optional, Dict, Tuple

from pick import pick

"""standard_input is used to simulate user input. Use in vscode."""
def standard_input():
    yield "add_"
    yield "Vasya"
    yield "165-34-54-221,123-34-567-01,456-12-345-67"
    yield "09.01.1990"
    yield "Lvivska st., Lviv, 32/56; Kyivska st., Kyiv, 56/42"
    yield "holidays_period"
    yield "30"
    yield "ex"


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

    def __init__(self, name: str, phone: List[str] = None, birthday: Optional[str] = None, address: Optional[str] = None) -> None:
        self.phone = []
        for one_phone in phone:
            try:
                self.phone.append(Phone(one_phone))
            except InvalidPhoneNumber:
                print(f"The phone number \"{one_phone}\" is invalid. It was not recorded.")
        self.name = Name(name)
        self.address = []
        for one_address in address:
            self.address.append(Address(one_address))
        if birthday:
            self.birthday = Birthday(birthday)

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
            result += f", phones: {','.join([one_phone.value for one_phone in self.phone])}"
        if self.address:
            result += f", address: {'; '.join([one_address.value for one_address in self.address])}"
        if self.birthday.value:
            result += f", birthday: {self.birthday.value}"
            result += f", to birthday: {self.days_to_birthday()}"
        return result


class AddressBook(UserDict):
    """Add new instance of Record class in AddressBook"""

    def __get_params(self, params: Dict[str,str]) -> List[str]:
        msg = "Please enter the "
        params_keys = list(params.keys())
        for index in range(len(params)):
            obj_name = params_keys[index]
            if obj_name == "phone":
                params[obj_name] = input(f"{msg}{obj_name}. Separator character for phone number is ',': ").split(",")
            elif obj_name == "address":
                params[obj_name] = input(f"{msg}{obj_name}. Separator character for address is ';': ").split(";")
            else:
                params[obj_name] = input(f"{msg}{obj_name}: ")
        return params.values()

    def add_record(self) -> None:
        new_record = Record(*self.__get_params({"name": "", "phone": "", "birthday": "", "address": ""}))
        self.data[new_record.name.value] = new_record

    def holidays_period(self) -> None:
        period = int(''.join(self.__get_params({"period": ""})))
        flag_found = False
        birthdays = {rec.birthday.value: name for name, rec in self.data.items()}
        dates = {date[:5]: date[5:] for date in birthdays}
        today = datetime.today()
        print(f"Search results for birthdays for a period of {period} days:")
        for one_day in range(period+1):
            today_period = (today + timedelta(days=one_day)).strftime("%d.%m")
            if today_period in dates:
                date = f"{today_period}{dates[today_period]}"
                print(f"{birthdays[date]} - {date}")
                flag_found = True
        if not flag_found:
            print("No contacts found with birthdays for the specified period.")

    def find_record(self, value: str) -> Optional[Record]:
        return self.data.get(value.capitalize())

    def delete_record(self, value: str) -> None:
        value = value.capitalize()
        if self.data.get(value):
            self.data.pop(value)

    def find_info(self, search_info):
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
def  cmd_add_tag():
    ''''''
def  cmd_sort_files():
    ''''''
def  cmd_find_contact():
    ''''''
def  cmd_edit_contact():
    ''''''
def  cmd_del_contact():
    ''''''
book = AddressBook()
TITLE = "We have chosen several options from the command you provided.\nPlease choose the one that you need."
action_commands = ["add_user", "holidays_period", "save_note ", "edit_note", "del_note", "sort_note", "find_note", "add_tag", "sort_files", "find_contact", "edit_contact", "del_contact"]
exit_commands = ["bye", "close", "exit"]
functions_list = [book.add_record, book.holidays_period, cmd_save_note, cmd_edit_note, cmd_del_note, cmd_sort_note, cmd_find_note, cmd_add_tag, cmd_sort_files, cmd_find_contact, cmd_edit_contact, cmd_del_contact]
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
