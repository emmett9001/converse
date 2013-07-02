import curses
import sys

import constants


class Shell():
    def __init__(self):
        self.stdscr = curses.initscr()
        self.stdscr.keypad(1)

        self.backbuffer = []
        self.height,self.width = self.stdscr.getmaxyx()

        self.menus = []
        self.stickers = []

        self.header = ""
        self._header_bottom = 0
        self._header_right = 0

    def print_backbuffer(self):
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

    def sticker(self, output, pos=None):
        if len(self.stickers) > 0:
            sort = sorted(self.stickers, key=lambda x: x[1][0])
            ht = sort[0][1][0]+1
        else:
            ht = 3

        if not pos:
            pos = (ht, self.width - 20)
        sticker = (output, pos)
        self.stickers.append(sticker)

    def remove_sticker(self, text):
        self.stickers = [a for a in self.stickers if a[0] != text]

    def print_header(self):
        ht = 0
        for line in self.header.split("\n"):
            self.stdscr.addstr(ht, 0, line)
            if len(line) > self._header_right:
                self._header_right = len(line)
            ht += 1
        self._header_bottom = ht

    def print_stickers(self):
        for text,pos in self.stickers:
            _y,_x = pos
            if _x + len(text) > self.width:
                _x = self.width - len(text) - 1
            self.stdscr.addstr(_y, _x, text)

    def get_helpstring(self):
        helpstring = "\n\n" + self.get_menu().title + "\n" + "-"*20 + "\n" + self.get_menu().options()
        return helpstring

    def print_help(self):
        ht = 0
        for line in self.get_helpstring().split("\n"):
            self.stdscr.addstr(ht, self._header_right + 10, line + " "*15)
            ht += 1

    def update_screen(self):
        self.stdscr.clear()
        self.stdscr.refresh()

        self.print_backbuffer()
        self.print_header()
        self.print_help()
        self.print_stickers()

    def put(self, output, command=False, pos=None):
        self.update_screen()

        if not output:
            return

        output = str(output)

        _x,_y = (self.height-1, 0)
        if pos:
            _x,_y = pos

        for line in output.split('\n'):
            # put the line
            self.stdscr.addstr(_x, _y, line)

            # add it to backbuffer
            backbuf_string = line
            to_append = (backbuf_string, command)
            if line != "> ":
                self.backbuffer.append(to_append)

    def _input(self, prompt):
        self.put(prompt)
        keyin = ''
        buff = ''
        hist_counter = 1
        while keyin != 10:
            keyin = self.stdscr.getch()
            #self.stdscr.addstr(20, 70, str(keyin))
            if keyin in [127, 263]:  # backspaces
                buff = buff[:-1]
                self.stdscr.addstr(self.height-1, 0, " "*(self.width-3))
                self.stdscr.addstr(self.height-1, 0, "> %s" % buff)
            elif keyin in [curses.KEY_DOWN, curses.KEY_UP]:
                hist_commands = [(s,c) for s,c in self.backbuffer if c]
                hist_commands.reverse()
                buff = hist_commands[-hist_counter][0]
                self.stdscr.addstr(self.height-1, 0, " "*(self.width-3))
                self.stdscr.addstr(self.height-1, 0, "> %s" % buff)
                if keyin == curses.KEY_UP:
                    if hist_counter < len(hist_commands):
                        hist_counter += 1
                else:
                    if hist_counter > 0:
                        hist_counter -= 1
            elif keyin == curses.KEY_F1:
                curses.endwin()
                sys.exit()
            elif keyin >= 32 and keyin <= 126:
                buff += chr(keyin)
        self.put(buff, command=True)
        self.stdscr.refresh()
        return buff

    def print_menu_header(self):
        self.put(self.get_helpstring())

    def main_loop(self):
        self.menu = 'main'

        ret_choice = None
        while ret_choice != constants.CHOICE_QUIT:
            ret_choice = constants.CHOICE_INVALID
            choice = self._input("> ")
            tokens = choice.split()
            if len(tokens) == 0:
                self.put("\n")
                continue
            for command in self.get_menu().commands:
                if tokens[0] == command.name:
                    if not command.validate(tokens):
                        self.put("Missing parameter")
                    else:
                        ret_choice = command.run(tokens)
                        if command.new_menu:
                            self.menu = command.new_menu
            if ret_choice == constants.CHOICE_INVALID:
                self.put("Invalid command")

        return self

    def get_menu(self):
        return [a for a in self.menus if a.name == self.menu][0]

    def end(self):
        curses.endwin()
