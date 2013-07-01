import curses
import sys

import constants


class Shell():
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.raw()
        self.stdscr.keypad(1)

        self.backbuffer = []
        self.height,self.width = self.stdscr.getmaxyx()

        self.menus = []

        self.stickers = []

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
        if not pos:
            pos = (3, self.width - 20)
        sticker = (output, pos)
        self.stickers.append(sticker)

    def print_stickers(self):
        for text,pos in self.stickers:
            _x,_y = pos
            self.stdscr.addstr(_x, _y, text)

    def update_screen(self):
        self.stdscr.clear()
        self.stdscr.refresh()

        self.print_backbuffer()
        self.print_stickers()


    def put(self, output, command=False, pos=None):
        self.update_screen()

        if not output:
            return

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
            if keyin >= 32 and keyin <= 126:
                buff += chr(keyin)
            elif keyin == curses.KEY_DL:  # TODO - broken keycode
                buff = buff[:-1]
            elif keyin in [curses.KEY_DOWN, curses.KEY_UP]:
                hist_commands = list(set([(s,c) for s,c in self.backbuffer if c]))
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
        self.put(buff, command=True)
        self.stdscr.refresh()
        return buff

    def print_menu_header(self, menu):
        self.put("\n\n" + self.get_menu(menu).title + "\n" + "-"*20)
        self.put("options:\n%s" % self.get_menu(menu).options())

    def main_loop(self):
        menu = 'main'

        self.print_menu_header(menu)

        ret_choice = None
        while ret_choice != constants.CHOICE_QUIT:
            ret_choice = constants.CHOICE_INVALID
            choice = self._input("> ")
            tokens = choice.split()
            if len(tokens) == 0:
                self.put("Invalid command")
                continue
            for command in self.get_menu(menu).commands:
                if tokens[0] == command.name:
                    if not command.validate(tokens):
                        self.put("Missing parameter")
                    else:
                        ret_choice = command.run(tokens)
                        if command.new_menu:
                            menu = command.new_menu
                            self.print_menu_header(menu)
            if ret_choice == constants.CHOICE_INVALID:
                self.put("Invalid command")

    def get_menu(self, name):
        return [a for a in self.menus if a.name == name][0]
