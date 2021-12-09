import re
from collections import UserDict
from difflib import get_close_matches

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

TITLE = "We have chosen several options from the command you provided.\nPlease choose the one that you need."
action_commands = ["help", "hello", "add", "change", "phone", "show all"]
exit_commands = ["good bye", "close", "exit"]
cmd_type = TypeOfCommand()
list_of_commands = {cmd_type.EXIT: exit_commands, cmd_type.ACTION: action_commands}
# functions_list = [cmd_help, cmd_hello, cmd_add, cmd_change, cmd_phone, cmd_show_all]
# commands_func = {cmd: func for cmd, func in zip(commands_list, functions_list)}

class CommandHandler(UserDict):

    def __init__(self) -> None:
        self.data = {}

    def get_input_msg(self, input_msg: str) -> int:
        for key, commands in list_of_commands.items():
            for cmd in commands:
                spaces = len(cmd.split())
                msg = re.sub(r" +", " ", input_msg).split(" ", maxsplit=spaces)
                raw_cmd, raw_msg = ' '.join(msg[:spaces]), ' '.join(msg[spaces:])
                match = ''.join(get_close_matches(raw_cmd, [cmd]))
                if key == cmd_type.EXIT and match:
                    return None
                elif key == cmd_type.ACTION and match:
                    self.data.update({match: raw_msg})
        if len(self.data) > 1:
            return self.data
        elif not self.data:
            print("Sorry, I could not recognize the entered command!")
            return 1
        else:
            # commands_func[cmd](input_str[len(cmd):].strip())

    # def __len__(self) -> int:
    #     return 1 if self.dont_exit else 0


if __name__ == "__main__":
    cmd = CommandHandler()
    input_msg = "hely"
    # input_msg = input("Hello, please enter the command: ").lower().strip()
    if cmd.get_input_msg(input_msg):
        print("run again")
        input_msg = ""
        #input_msg = input("Please enter the command: ").lower().strip()

print("Have a nice day... Good bye!")
