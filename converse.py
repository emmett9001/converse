from collections import defaultdict
import sys
from shutil import copyfile
import os
from os import listdir
from os.path import isfile, join
import time

from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement

from candela.shell import Shell
from candela.command import Command, BackCommand, QuitCommand, RunScriptCommand
from candela.menu import Menu
import candela.constants as constants


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

        self.setup_menus()
        self.default_state()

        self.sticker("Autosave On")

    def default_state(self):
        self.cwt = ''  # current working topic
        self.sentences = []
        self.responses = defaultdict(dict)
        self._id_counter = 0

    def setup_menus(self):
        new_com = Command('new topic', 'Create a new topic')
        def _run(*args, **kwargs):
            topic = " ".join(args[0:])
            if topic in self.get_available_topics():
                self.put("Topic %s already exists." % topic)
                self.load_file(topic)
                self.sticker("Topic: '%s'" % self.cwt)
            else:
                self.cwt = topic
                self.put("New topic %s" % self.cwt)
                self.sticker("Topic: '%s'" % self.cwt)
            return constants.CHOICE_VALID
        new_com.run = _run
        new_com.new_menu = 'edit'

        load_com = Command('load topic', 'Load a previous topic')
        def _run(*args, **kwargs):
            topic = " ".join(args[0:])
            success = self.load_file(topic)
            if success:
                self.sticker("Topic: '%s'" % self.cwt)
                return constants.CHOICE_VALID
            return constants.FAILURE
        load_com.run = _run
        load_com.new_menu = 'edit'

        list_com = Command('list', 'Show available topics')
        def _run(*args, **kwargs):
            self.list_topic_files()
            return constants.CHOICE_VALID
        list_com.run = _run

        sen_com = Command('sentence tags text', 'Create a new player sentence')
        def _run(*args, **kwargs):
            sentence = " ".join(args[1:])
            tag = args[0]
            self.create_sentence(tag, sentence)
            return constants.CHOICE_VALID
        sen_com.run = _run

        res_com = Command('response sID chartype mood next_topic text', 'Create a new NPC response')
        def _run(*args, **kwargs):
            text = " ".join(args[4:])
            sen_id = int(args[0])
            _type = args[1]
            mood = args[2]
            _next = args[3]
            self.create_response(sen_id, _type, mood, _next, text)
            return constants.CHOICE_VALID
        res_com.run = _run

        list_topic_com = Command('list', 'Show current player sentences')
        def _run(*args, **kwargs):
            self.list_topic()
            return constants.CHOICE_VALID
        list_topic_com.run = _run
        list_topic_com.alias('ls')

        del_res_com = Command('delete_r sen_id type mood', 'Delete an NPC response')
        def _run(*args, **kwargs):
            sen_id = int(args[0])
            _type = args[1]
            mood = args[2]
            self.delete_response(sen_id, _type, mood)
            return constants.CHOICE_VALID
        del_res_com.run = _run

        del_sen_com = Command('delete_s sen_id', 'Delete sentence by ID')
        def _run(*args, **kwargs):
            sen_id = int(args[0])
            self.delete_sentence(sen_id)
            return constants.CHOICE_VALID
        del_sen_com.run = _run

        write_com = Command('save', 'Save to a file')
        def _run(*args, **kwargs):
            self.write_out(from_command=True)
            return constants.CHOICE_VALID
        write_com.run = _run

        # builtins
        back_com = BackCommand('main')
        def _run(*args, **kwargs):
            self.remove_sticker("Topic: '%s'" % self.cwt)
            self.unload_file(self.cwt)
            return back_com.default_run(*args, **kwargs)
        back_com.run = _run
        quit_com = QuitCommand(self.name)
        quit_com.alias('q')
        run_com = RunScriptCommand(self)

        defaults = [quit_com, run_com]

        main_menu = Menu('main')
        main_menu.title = "Main menu"
        main_menu.commands = [new_com, load_com, list_com] + defaults

        edit_menu = Menu('edit')
        edit_menu.title = "Editing menu"
        edit_menu.commands = [sen_com, del_sen_com, res_com, del_res_com,
                              list_topic_com, back_com, write_com] + defaults

        # TODO - sticker list of existing sentences in the edit menu

        self.menus = [main_menu, edit_menu]
        self.menu = 'main'  # TODO - hide this somehow?

    def list_topic_files(self):
        files = self.get_available_topics()
        self.put("Available topics:")
        for f in files:
            self.put("  " + f)

    def get_available_topics(self):
        files = [f[:-4] for f in listdir('.') if \
                 isfile(join('.',f)) and f.endswith('.xml')]
        return files

    def list_topic(self):
        for _id,tag,sentence in self.sentences:
            self.put("%d: %s (%s)" % (_id,sentence,tag))
            for _type in self.responses[_id]:
                self.put("  %s" % _type)
                for mood,_next,text in self.responses[_id][_type]:
                    self.put("    %s (%s) -> %s" % (text, mood, _next))

    def create_response(self, sen_id, _type, mood, _next, text):
        tup = (mood,_next,text)
        if _type not in self.responses[sen_id].keys():
            self.responses[sen_id][_type] = []

        for res in self.responses[sen_id][_type]:
            if mood == res[0]:
                self.put("Duplicate mood: %s" % mood)
                return

        self.responses[sen_id][_type].append(tup)
        self.write_out()
        self.put("NPC Response created: %s\nwith chartype: %s\nand mood: %s\nand topic: %s" % (text, _type, mood, _next))

    def delete_response(self, sen_id, _type, mood):
        if _type in self.responses[sen_id].keys():
            for res in self.responses[sen_id][_type]:
                if res[0] == mood:
                    to_remove = res
                    break
            self.responses[sen_id][_type] = [a for a
                in self.responses[sen_id][_type] if a != to_remove]
            if len(self.responses[sen_id][_type]) == 0:
                self.responses[sen_id].pop(_type)
            self.write_out()
            self.put("Deleted %s %s response to %d" % (_type, mood, sen_id))
        else:
            self.put("No matching response found.")

    def create_sentence(self, tag, sentence):
        for sen in self.sentences:
            if sen[2] == sentence:
                self.put("Duplicate sentence")
                return

        tup = (self._id_counter,tag,sentence)
        self.sentences.append(tup)
        self._id_counter += 1
        self.write_out()
        self.put("Sentence created: %s\nwith tag: %s" % (sentence, tag))

    def delete_sentence(self, sen_id):
        for sen in self.sentences:
            if sen[0] == sen_id:
                to_remove = sen
                break

        self.sentences = [a for a in self.sentences if a != to_remove]
        self.responses.pop(sen_id)
        self.write_out()
        self.put("Removed sentence '%s' and all responses" % to_remove[2])

    def load_file(self, topic):
        filename = "%s.xml" % topic
        self.sticker("Loading %s" % filename)

        def reset_sticker():
            time.sleep(.1)
            self.remove_sticker("Loading %s" % filename)

        try:
            tree = ET.parse(filename)
            self._parse_tree(tree.getroot())
        except Exception as e:
            self.put("Failed to load %s - %s" % (filename, e))
            self.timeout(reset_sticker)
            return False
        else:
            self.put("Success loading %s" % filename)
            self.timeout(reset_sticker)
            return True

    def unload_file(self, topic):
        self.write_out()
        self.default_state()
        self.put("Unloaded %s" % topic)

    def write_out(self, from_command=False):
        self.sticker("Autosave On", new_output="Saving...")
        tree = self._build_tree()

        if self._file_exists('%s.xml' % self.cwt):
            shutil.copyfile('%s.xml' % self.cwt, '%s.xml.swp' % self.cwt)
        else:
            f = open('%s.xml.swp' % self.cwt, "w+")
            f.write(ET.tostring(tree))
            f.close()

        try:
            f = open('%s.xml' % self.cwt, "w+")
            f.write(ET.tostring(tree))
            f.close()
        except:
            if from_command:
                self.put("Failed to write file")
            # restore from swap
            shutil.copyfile('%s.xml.swp' % self.cwt, '%s.xml' % self.cwt)
        else:
            if from_command:
                self.put("Success writing file %s.xml" % self.cwt)
            # remove swap on successful save
            os.remove('%s.xml.swp' % self.cwt)

        def reset_sticker():
            time.sleep(.1)
            self.sticker("Saving...", new_output="Autosave On")
        self.timeout(reset_sticker)

    def _file_exists(self, filename):
        try:
            with open('filename'): pass
        except IOError:
            return False
        return True

    def _build_tree(self):
        root = Element('topic')
        root.set('name', self.cwt)
        for _id,tag,sentence in self.sentences:
            sen_element = SubElement(root, "sentence")
            sen_element.set('tag', tag)
            text_element = SubElement(sen_element, "text")
            text_element.text = sentence
            if _id in self.responses.keys():
                res_element = SubElement(sen_element, "responses")
                for chartype in self.responses[_id]:
                    char_element = SubElement(res_element, "character")
                    char_element.set('type', chartype)
                    for mood,_next,response in self.responses[_id][chartype]:
                        mood_element = SubElement(char_element, 'mood')
                        mood_element.set('type', mood)
                        mood_element.set('next', _next)
                        mood_element.text = response
        return root

    def _parse_tree(self, root):
        self.cwt = root.attrib['name']
        for sentence in root:
            text = sentence.find('text').text
            tup = (self._id_counter, sentence.attrib['tag'], text)
            self.sentences.append(tup)
            self.responses[self._id_counter] = {}
            responses = sentence.find('responses')
            if responses:
                for chartype in responses:
                    _type = chartype.attrib['type']
                    self.responses[self._id_counter][_type] = []
                    for mood in chartype:
                        tup = (mood.attrib['type'],mood.attrib['next'],mood.text)
                        self.responses[self._id_counter][_type].append(tup)
            self._id_counter += 1


if __name__ == "__main__":
    arg = None
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    Converse(arg).main_loop().end()
