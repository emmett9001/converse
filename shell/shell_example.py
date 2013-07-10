import getpass

from shell import Shell
from menu import Menu
from command import QuitCommand


class MyShell(Shell):
    def __init__(self):
        Shell.__init__(self)

        self.name = "My Shell"
        self.header = "My Cool Shell"

        self.sticker("Welcome, %s" % getpass.getuser())

        quit_com = QuitCommand(self.name)
        quit_com.alias('q')

        main_menu = Menu('main')
        main_menu.title = "Main menu"
        main_menu.commands = [quit_com]

        self.menus = [main_menu]
        self.menu = 'main'


if __name__ == "__main__":
    MyShell().main_loop().end()
