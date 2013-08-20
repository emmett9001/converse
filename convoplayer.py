from editor import Editor
from candela.menu import Menu
from candela.command import Command, BackCommand, QuitCommand, ClearCommand
from candela import constants


class ConversationPlayer():
    def __init__(self, shell):
        self.shell = shell
        self.editor = Editor(shell)
        self.defaults = self.setup_defaults()

    def run(self, chartype, mood, entry):
        sentences_menu = self._next_step(chartype, mood, entry)
        self.shell.menus.append(sentences_menu)

    def _next_step(self, chartype, mood, entry):
        success = self.editor.load_file(entry)

        sentences_menu = Menu(entry.lower())
        sentences_menu.title = entry

        for i,sen in zip(range(len(self.editor.sentences)), self.editor.sentences):
            _id,tags,text = sen
            com = Command(str(i), text)
            def _run(text=text, _id=_id):
                self.shell.put("Player: '%s'" % text)
                responses = self.editor.responses[_id].get(chartype, [])
                found = False
                next_topic = 'main'
                for _rid,_mood,_next,_text in responses:
                    for indv_mood in _mood.split(','):
                        if indv_mood == mood:
                            self.shell.put("%s: '%s'" % (chartype, _text))
                            next_topic = _next
                            found = True
                if not found:
                    self.shell.put("Error, no responses found for %s %s\nReturning to main menu" % (mood, chartype))
                else:
                    menu = self._next_step(chartype, mood, next_topic)
                    self.shell.menus.append(menu)
                return next_topic
            com.run = _run
            sentences_menu.commands.append(com)

        sentences_menu.commands += self.defaults

        return sentences_menu

    def setup_defaults(self):
        quit_com = QuitCommand('converse')
        quit_com.alias('q')

        clear_com = ClearCommand(self.shell)

        back_com = BackCommand('main')

        return [back_com, clear_com, quit_com]
