import curses

from shell import Shell
from command import Command, BackCommand, QuitCommand
from menu import Menu
import constants

class Converse(Shell):
    def __init__(self):
        Shell.__init__(self)

        self.name = "Converse"

        self.header = """
   ____                                   
  / ___|___  _ ____   _____ _ __ ___  ___ 
 | |   / _ \| '_ \ \ / / _ \ '__/ __|/ _ \\
 | |__| (_) | | | \ V /  __/ |  \__ \  __/
  \____\___/|_| |_|\_/ \___|_|  |___/\___|
                                           by Emmett Butler"""

        self.cwt = ''

        self.setup_menus()

    def setup_menus(self):
        new_com = Command('new <topic>', 'Create a new topic')
        def _run(tokens):
            self.put("new topic %s" % tokens[1])
            self.cwt = tokens[1]
            self.sticker("Topic: %s" % self.cwt)
            return constants.CHOICE_LOAD
        new_com.set_run_function(_run)
        new_com.new_menu = 'edit'

        load_com = Command('load <topic>', 'Load a previous topic')
        def _run(tokens):
            self.put("Loading topic %s" % tokens[1])
            self.cwt = tokens[1]
            self.sticker("Topic: %s" % self.cwt)
            return constants.CHOICE_NEW
        load_com.set_run_function(_run)
        load_com.new_menu = 'edit'

        list_com = Command('list', 'Show available topics')
        def _run(tokens):
            self.put("Listing")
            return constants.CHOICE_LIST
        list_com.set_run_function(_run)

        sen_com = Command('sentence <tags> <text>', 'Create a new player sentence')
        def _run(tokens):
            self.put("Sentence created: %s\nwith tag: %s" % (tokens[2], tokens[1]))
            return constants.CHOICE_SENTENCE
        sen_com.set_run_function(_run)

        res_com = Command('response <sID> <chartype> <mood> <next_topic> text', 'Create a new NPC response')
        def _run(tokens):
            self.put("NPC Response created: %s\nwith chartype: %s\nand mood: %s\nand topic: %s" % (tokens[5], tokens[2], tokens[3], tokens[4]))
            return constants.CHOICE_RESPONSE
        res_com.set_run_function(_run)

        back_com = BackCommand('main')
        def _run(tokens):
            self.remove_sticker("Topic: %s" % self.cwt)
            return back_com.default_run(tokens)
        back_com.set_run_function(_run)

        quit_com = QuitCommand(self.name)

        main_menu = Menu('main')
        main_menu.title = "Main menu"
        main_menu.commands = [new_com, load_com, list_com, quit_com]

        edit_menu = Menu('edit')
        edit_menu.title = "Editing menu"
        edit_menu.commands = [sen_com, res_com, back_com, quit_com]

        self.menus = [main_menu, edit_menu]

if __name__ == "__main__":
    converse = Converse()
    converse.main_loop()
    curses.endwin()
