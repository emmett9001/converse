import curses
import sys

import constants


class Shell():
    # current working topic
    _cwt = ""

    def __init__(self):
        self.stdscr = curses.initscr()
        curses.raw()
        self.stdscr.keypad(1)

        self.backbuffer = []
        self.height,self.width = self.stdscr.getmaxyx()


    def resolve(self, user_in):
        if user_in == constants.COMMAND_QUIT:
            return constants.CHOICE_QUIT

    def put(self, output, command=False):
        self.stdscr.clear()
        self.stdscr.refresh()
        rev = list(self.backbuffer)
        rev.reverse()
        i = 0
        for string, iscommand in rev:
            ypos = self.height-2-i
            if ypos > 0:
                printstring = string
                if iscommand:
                    printstring = "> %s" % string
                self.stdscr.addstr(ypos,0,printstring)
            i += 1
        self.stdscr.addstr(self.height-1, 0, output)
        backbuf_string = output
        to_append = (backbuf_string, command)
        if output != "> ":
            self.backbuffer.append(to_append)

    def shell_input(self, prompt):
        self.put(prompt)
        keyin = ''
        buff = ''
        hist_counter = 1
        while keyin != 10:
            keyin = self.stdscr.getch()
            if keyin >= 32 and keyin <= 126:
                buff += chr(keyin)
            elif keyin == curses.KEY_DL:  # TODO - broken keycode
                buff = buff[:-1]
            elif keyin in [curses.KEY_DOWN, curses.KEY_UP]:
                hist_commands = [(s,c) for s,c in self.backbuffer if c]
                buff = hist_commands[-hist_counter][0]
                self.stdscr.addstr(self.height-1, 0, "> %s" % buff)
                if keyin == curses.KEY_UP:
                    if hist_counter < len(hist_commands) - 1:
                        hist_counter += 1
                else:
                    if hist_counter > 0:
                        hist_counter -= 1
            elif keyin == curses.KEY_F1:
                curses.endwin()
                sys.exit()
        self.put(buff, True)
        self.stdscr.refresh()
        return buff

    def main_loop(self):
        self.put("Converse! It's a thing")
        self.put("options:")
        self.put("  load [topicname]")
        self.put("  new [topicname]")
        self.put("  list")

        menu = 'main'

        ret_choice = None
        while ret_choice != constants.CHOICE_QUIT:
            ret_choice = constants.CHOICE_INVALID
            choice = self.shell_input("> ")
            tokens = choice.split()
            if len(tokens) == 0:
                self.put("Invalid command")
                continue
            for command in self.commands[menu]:
                if tokens[0] == command.name:
                    if not command.validate(tokens):
                        self.put("Missing parameter")
                    else:
                        ret_choice = command.run(tokens)
                        menu = command.new_menu if command.new_menu else menu
            if ret_choice == constants.CHOICE_INVALID:
                self.put("Invalid command")

