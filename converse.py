import sys

import candela.constants as constants
from candela.shell import Shell
from candela.command import Command, BackCommand, QuitCommand, RunScriptCommand
from candela.command import ClearCommand
from candela.menu import Menu
from editor import Editor
from convoplayer import ConversationPlayer


class Converse(Shell):
    def __init__(self, scriptfile):
        Shell.__init__(self, scriptfile)

        self.name = "Converse"

        self.header = """
   ____                                                    
  / ___|___  _ ____   _____ _ __ ___  ___                  
 | |   / _ \| '_ \ \ / / _ \ '__/ __|/ _ \\                 
 | |__| (_) | | | \ V /  __/ |  \__ \  __/                 
  \____\___/|_| |_|\_/ \___|_|  |___/\___|                 
                                           by Emmett Butler"""

        self.editor = Editor(self)
        self.convoplayer = ConversationPlayer(self)
        self.setup_menus()

        self.sticker("Autosave On")

        self.should_show_hint = True

        # TODO - response editing
        # TODO - "play" command that allows interactive tree traversal
        # TODO - sticker list of existing sentences in the edit menu

    def setup_menus(self):
        # completions
        def _complete_chartype(frag):
            return self.editor.list_all_chartypes()
        def _complete_mood(frag):
            return self.editor.list_all_moods()
        def _complete_topic(frag):
            return list(set(self.editor.get_available_topics() + self.editor.list_new_topics()))

        new_com = Command('new topic', 'Create a new topic')
        def _run(*args, **kwargs):
            topic = " ".join(args[0:])
            if topic in self.editor.get_available_topics():
                self.put("Topic %s already exists." % topic)
                self.editor.load_file(topic)
                self.sticker("Topic: '%s'" % self.editor.cwt)
            else:
                self.editor.cwt = topic
                self.put("New topic %s" % self.editor.cwt)
                self.sticker("Topic: '%s'" % self.editor.cwt)
            return constants.CHOICE_VALID
        new_com.run = _run
        new_com.new_menu = 'edit'

        load_com = Command('load topic', 'Load a previous topic')
        def _run(*args, **kwargs):
            topic = " ".join(args[0:])
            success = self.editor.load_file(topic)
            if success:
                self.sticker("Topic: '%s'" % self.editor.cwt)
                return constants.CHOICE_VALID
            return constants.FAILURE
        load_com.run = _run
        load_com.new_menu = 'edit'
        def _complete_topic(frag):
            return self.editor.get_available_topics()
        load_com.tabcomplete_hooks['topic'] = _complete_topic

        list_com = Command('list', 'Show available topics')
        def _run(*args, **kwargs):
            self.editor.list_topic_files()
            return constants.CHOICE_VALID
        list_com.run = _run

        sen_com = Command('sentence tags text', 'Create a new player sentence')
        def _run(*args, **kwargs):
            sentence = " ".join(args[1:])
            tag = args[0]
            self.editor.create_sentence(tag, sentence)
            return constants.CHOICE_VALID
        sen_com.run = _run
        def _complete(frag):
            tags = []
            for _id,tag,sentence in self.editor.sentences:
                for t in tag.split(','):
                    tags.append(t)
            return list(set(tags))
        sen_com.tabcomplete_hooks['tags'] = _complete

        res_com = Command('response sID chartype mood next_topic text', 'Create a new NPC response')
        def _run(*args, **kwargs):
            text = " ".join(args[4:])
            sen_id = int(args[0])
            _type = args[1]
            mood = args[2]
            _next = args[3]
            self.editor.create_response(sen_id, _type, mood, _next, text)
            return constants.CHOICE_VALID
        res_com.run = _run
        res_com.alias('res')
        res_com.tabcomplete_hooks['chartype'] = _complete_chartype
        res_com.tabcomplete_hooks['mood'] = _complete_mood
        res_com.tabcomplete_hooks['next_topic'] = _complete_topic

        list_topic_com = Command('list', 'Show current player sentences')
        def _run(*args, **kwargs):
            self.editor.list_topic()
            return constants.CHOICE_VALID
        list_topic_com.run = _run
        list_topic_com.alias('ls')

        del_res_com = Command('delete_r sen_id type res_id', 'Delete an NPC response')
        def _run(*args, **kwargs):
            sen_id = int(args[0])
            _type = args[1]
            res_id = int(args[2])
            self.editor.delete_response(sen_id, _type, res_id)
            return constants.CHOICE_VALID
        del_res_com.run = _run
        del_res_com.alias('delr')
        del_res_com.tabcomplete_hooks['type'] = _complete_chartype
        del_res_com.tabcomplete_hooks['mood'] = _complete_mood

        del_sen_com = Command('delete_s sen_id', 'Delete sentence by ID')
        def _run(*args, **kwargs):
            sen_id = int(args[0])
            self.editor.delete_sentence(sen_id)
            return constants.CHOICE_VALID
        del_sen_com.run = _run
        del_sen_com.alias('dels')

        edit_sen_com = Command('edit_s sen_id tags text', 'Edit an existing sentence')
        def _run(*args, **kwargs):
            sen_id = int(args[0])
            sentence = " ".join(args[2:])
            tag = args[1]
            self.editor.edit_sentence(sen_id, tag, sentence)
            return constants.CHOICE_VALID
        edit_sen_com.run = _run
        def _complete(frag):
            tags = []
            for _id,tag,sentence in self.editor.sentences:
                for t in tag.split(','):
                    tags.append(t)
            return list(set(tags))
        edit_sen_com.tabcomplete_hooks['tags'] = _complete

        write_com = Command('save', 'Save to a file')
        def _run(*args, **kwargs):
            self.editor.write_out(from_command=True)
            return constants.CHOICE_VALID
        write_com.run = _run

        cd_com = Command('cd path', 'Change current directory')
        def _run(*args, **kwargs):
            path = ""
            for part in args:
                path += part
            path = path.replace('\\', ' ')
            self.editor.path = path
            return constants.CHOICE_VALID
        cd_com.run = _run

        pwd_com = Command('pwd', 'Print current directory')
        def _run(*args, **kwargs):
            self.put(self.editor.path)
            return constants.CHOICE_VALID
        pwd_com.run = _run

        convoplay_com = Command('play chartype mood [-e entry_point]', 'Run a conversation')
        def _run(*args, **kwargs):
            entry = kwargs.get('e', 'greetings')
            char = args[0]
            mood = args[1]
            self.convoplayer.run(char, mood, entry=entry)
            return entry.lower()
        convoplay_com.run = _run

        # builtins
        back_com = BackCommand('main')
        def _run(*args, **kwargs):
            self.remove_sticker("Topic: '%s'" % self.editor.cwt)
            self.editor.unload_file(self.editor.cwt)
            return back_com.default_run(*args, **kwargs)
        back_com.run = _run
        quit_com = QuitCommand(self.name)
        quit_com.alias('q')
        run_com = RunScriptCommand(self)
        clear_com = ClearCommand(self)

        defaults = [quit_com, run_com, clear_com]

        main_menu = Menu('main')
        main_menu.title = "Main menu"
        main_menu.commands = [new_com, load_com, list_com, cd_com, pwd_com,
                              convoplay_com] + defaults

        edit_menu = Menu('edit')
        edit_menu.title = "Editing menu"
        edit_menu.commands = [sen_com, edit_sen_com, del_sen_com, res_com, del_res_com,
                              list_topic_com, back_com, convoplay_com, write_com] + defaults

        self.menus = [main_menu, edit_menu]
        self.menu = 'main'  # TODO - hide this somehow?


if __name__ == "__main__":
    arg = None
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    Converse(arg).main_loop().end()
