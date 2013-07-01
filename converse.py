import curses

from shell import Shell
from command import Command
import constants

if __name__ == "__main__":
    converse = Shell()

    converse.commands = {'main': [], 'edit': []}

    com = Command('new <topic>')
    def _run(tokens):
        converse.put("new topic %s" % tokens[1])
        return constants.CHOICE_LOAD
    com.set_run_function(_run)
    com.new_menu = 'edit'
    converse.commands['main'].append(com)

    com = Command('load <topic>')
    def _run(tokens):
        converse.put("Loading topic %s" % tokens[1])
        return constants.CHOICE_NEW
    com.set_run_function(_run)
    com.new_menu = 'edit'
    converse.commands['main'].append(com)

    com = Command('list')
    def _run(tokens):
        converse.put("Listing")
        return constants.CHOICE_LIST
    com.set_run_function(_run)
    converse.commands['main'].append(com)

    com = Command('quit')
    def _run(tokens):
        return constants.CHOICE_QUIT
    com.set_run_function(_run)
    converse.commands['main'].append(com)

    com = Command('test')
    def _run(tokens):
        converse.put("I worked!")
        return constants.CHOICE_LIST
    com.set_run_function(_run)
    converse.commands['edit'].append(com)

    converse.main_loop()

    curses.endwin()
