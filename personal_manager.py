import pickle
import re
from collections import UserDict
from datetime import datetime
from difflib import get_close_matches
from pathlib import Path
from typing import List, Optional

from pick import pick

"""Decorator for command type constants."""
def constant(func):
    def fset(self, value): raise TypeError
    def fget(self): return func()
    return property(fget, fset)


"""Classes for choosing constants "EXIT" (used for exit_commands), "ACTION" (used for action_commands)"""
class TypeOfCommand(object):
    @constant
    def EXIT(): return "EXIT"
    @constant
    def ACTION(): return "ACTION"


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
            self._value = ''


class Record:
    """Record class responsible for the logic of adding/removing/editing fields
    Only one name but many phone numbers"""

    def __init__(self, name: str, phone: List[str] = None, birthday: Optional[str] = None) -> None:
        self.phone = []
        for one_phone in phone:
            try:
                self.phone.append(Phone(one_phone))
            except InvalidPhoneNumber:
                print(f"The phone number {one_phone} is invalid")
        self.name = Name(name)
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
            result += f", phones: {[one_phone.value for one_phone in self.phone]}"
        if self.birthday.value:
            result += f", birthday: {self.birthday.value}"
            result += f", to birthday: {self.days_to_birthday()}"
        return result


class AddressBook(UserDict):
    """Add new instance of Record class in AddressBook"""

    def add_record(self, name: str, phones: List[str] = None, birthday: Optional[str] = None) -> None:
        new_record = Record(name, phones, birthday)
        self.data[new_record.name.value] = new_record

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


class CommandHandler(UserDict):

    def __init__(self) -> None:
        self.data = {}

    def get_input_msg(self, input_msg: str) -> int:
        for key, commands in list_of_commands.items():
            for cmd in commands:
                spaces = len(cmd.split())
                msg = re.sub(r" +", " ", input_msg).split(" ", maxsplit=spaces)
                raw_cmd, raw_msg = ' '.join(msg[:spaces]), ' '.join(msg[spaces:])
                # дописать: если прямое соответствие, то get_close_matches делать не надо
                match = ''.join(get_close_matches(raw_cmd, [cmd]))
                if key == cmd_type.EXIT and match:
                    return None
                elif key == cmd_type.ACTION and match:
                    self.data.update({match: raw_msg})
        if not self.data:
            print("Sorry, I could not recognize the entered command!")
            return 1
        else:
            if len(self.data) > 1:
                option, _ = pick(self.data.values(), TITLE, indicator="=>")
            else:
                option = self.data.values()[0]
            commands_func[option](raw_msg)


TITLE = "We have chosen several options from the command you provided.\nPlease choose the one that you need."
action_commands = ["help", "hello", "add ", "change", "phone", "show all"]
exit_commands = ["good bye", "close", "exit"]
cmd_type = TypeOfCommand()
list_of_commands = {cmd_type.EXIT: exit_commands, cmd_type.ACTION: action_commands}
#functions_list = [cmd_help, cmd_hello, cmd_add, cmd_change, cmd_phone, cmd_show_all]
#functions_list = ['cmd_help', 'cmd_hello', 'cmd_add', 'cmd_change', 'cmd_phone', 'cmd_show_all']
#commands_func = {cmd: func for cmd, func in zip(commands_list, functions_list)}


if __name__ == "__main__":
    current_script_path = Path(__file__).absolute()
    file_bin_name = f"{current_script_path.stem}.bin"
    book = AddressBook()
    data_file = current_script_path.parent.joinpath(file_bin_name)
    """get data file from current directory"""
    book.load_data(data_file)
    cmd = CommandHandler()
    input_msg = input("Hello, please enter the command: ").lower().strip()
    while cmd.get_input_msg(input_msg):
        """run again"""
        input_msg = input("Please enter the command: ").lower().strip()

    book.save_data(data_file)
    print("Have a nice day... Good bye!")
