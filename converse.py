import curses

from shell import Shell
from command import Command
from menu import Menu
import constants

if __name__ == "__main__":
    converse = Shell()

    menu = Menu('main')
    menu.title = "Converse. It's a thing"

    com = Command('new <topic>', 'Create a new topic')
    def _run(tokens):
        converse.put("new topic %s" % tokens[1])
        return constants.CHOICE_LOAD
    com.set_run_function(_run)
    com.new_menu = 'edit'
    menu.commands.append(com)

    com = Command('load <topic>', 'Load a previous topic')
    def _run(tokens):
        converse.put("Loading topic %s" % tokens[1])
        return constants.CHOICE_NEW
    com.set_run_function(_run)
    com.new_menu = 'edit'
    menu.commands.append(com)

    com = Command('list', 'Show available topics')
    def _run(tokens):
        converse.put("Listing")
        return constants.CHOICE_LIST
    com.set_run_function(_run)
    menu.commands.append(com)

    quit_com = Command('quit', 'Quit the shell')
    def _run(tokens):
        return constants.CHOICE_QUIT
    quit_com.set_run_function(_run)
    menu.commands.append(quit_com)

    converse.menus.append(menu)
    menu = Menu('edit')
    menu.title = "Editing menu"

    com = Command('test', 'test that this works')
    def _run(tokens):
        converse.put("I worked!")
        return constants.CHOICE_LIST
    com.set_run_function(_run)
    menu.commands.append(com)

    menu.commands.append(quit_com)

    converse.menus.append(menu)

    converse.main_loop()

    curses.endwin()
