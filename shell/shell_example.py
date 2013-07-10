import getpass

from shell import Shell
from menu import Menu
from command import Command, QuitCommand
import constants


class MyShell(Shell):
    def __init__(self):
        Shell.__init__(self)

        self.name = "My Shell"
        self.header = "My Cool Shell"

        self.sticker("Welcome, %s" % getpass.getuser())

        hello_world_com = self.build_hello_command()
        quit_com = self.build_quit_command()

        main_menu = Menu('main')
        main_menu.title = "Main menu"
        main_menu.commands = [hello_world_com, quit_com]

        self.menus = [main_menu]
        self.menu = 'main'

    def build_hello_command(self):
        com = Command('sayhello', 'Print a friendly greeting')
        def _run(tokens):
            for token in tokens:
                self.put(token)
            self.put("Hello, world!")
            return constants.CHOICE_VALID
        com.run = _run
        return com

    def build_quit_command(self):
        quit_com = QuitCommand(self.name)
        quit_com.alias('q')
        return quit_com


if __name__ == "__main__":
    MyShell().main_loop().end()
