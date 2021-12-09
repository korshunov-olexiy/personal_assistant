from collections import UserDict


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


class CommandHandler(UserDict):
    action_commands = ["help", "hello", "add", "change", "phone", "show all"]
    exit_commands = ["good bye", "close", "exit"]
    cmd_type = TypeOfCommand()
    type_of_commands = {cmd_type.EXIT: exit_commands, cmd_type.ACTION: action_commands}
    def __init__(self) -> None:
        self.data = None
        self.dont_exit = None

    def get_input_msg(self, input_msg: str) -> str:
        """"""

    def __len__(self) -> int:
        return 1 if self.dont_exit else 0


if __name__ == "__main__":
    cmd = CommandHandler()
    if cmd:
        print("run again")
    else:
        print("exit")
