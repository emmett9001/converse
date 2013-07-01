import curses

from shell import Shell
from command import Command
from menu import Menu
import constants

if __name__ == "__main__":
    converse = Shell()

    main_menu = Menu('main')
    main_menu.title = "Converse. It's a thing"

    new_com = Command('new <topic>', 'Create a new topic')
    def _run(tokens):
        converse.put("new topic %s" % tokens[1])
        return constants.CHOICE_LOAD
    new_com.set_run_function(_run)
    new_com.new_menu = 'edit'

    load_com = Command('load <topic>', 'Load a previous topic')
    def _run(tokens):
        converse.put("Loading topic %s" % tokens[1])
        return constants.CHOICE_NEW
    load_com.set_run_function(_run)
    load_com.new_menu = 'edit'

    list_com = Command('list', 'Show available topics')
    def _run(tokens):
        converse.put("Listing")
        return constants.CHOICE_LIST
    list_com.set_run_function(_run)

    quit_com = Command('quit', 'Quit the shell')
    def _run(tokens):
        return constants.CHOICE_QUIT
    quit_com.set_run_function(_run)

    edit_menu = Menu('edit')
    edit_menu.title = "Editing menu"

    test_com = Command('test', 'test that this works')
    def _run(tokens):
        converse.put("I worked!")
        return constants.CHOICE_LIST
    test_com.set_run_function(_run)

    main_menu.commands = [new_com, load_com, list_com, quit_com]
    edit_menu.commands = [test_com, quit_com]
    converse.menus = [main_menu, edit_menu]

    converse.main_loop()

    curses.endwin()
