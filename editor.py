import os
import time
import shutil
from collections import defaultdict

from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement


class Editor():
    def __init__(self, shell):
        self.shell = shell
        self.default_state()

    def default_state(self):
        self.cwt = ''  # current working topic
        self.sentences = []
        self.responses = defaultdict(dict)
        self.created_topics = []
        self._id_counter = 0
        self._res_id_counter = 0
        self.path = "."

    def list_topic_files(self):
        files = self.get_available_topics()
        self.shell.put("Available topics:")
        for f in files:
            self.shell.put("  " + f)

    def get_available_topics(self):
        files = [f[:-4] for f in os.listdir(self.path) if \
                 os.path.isfile(os.path.join(self.path,f)) and f.endswith('.xml')]
        return list(set(files + self.created_topics))

    def list_all_chartypes(self):
        ret = []
        for res in self.responses.keys():
            ret += self.responses[res].keys()
        return list(set(ret))

    def list_topic(self):
        def cap(s, l, wrap=()):
            s =  s if len(s)<=l else s[0:l-3]+'...'
            if wrap:
                s = "%s%s%s" % (wrap[0], s, wrap[1])
            if len(s) < l:
                s += " "*(l-len(s))
            return s
        thresh = 40
        _sorted = sorted(self.sentences, key=lambda x: x[0])
        for _id,tag,sentence in _sorted:
            capped = cap(sentence, thresh)
            captag = cap(tag, thresh-8)
            self.shell.put("%d: %s (%s)" % (_id,capped,tag))
            for _type in self.responses[_id]:
                self.shell.put("  %s" % _type)
                for _rid,mood,_next,text in self.responses[_id][_type]:
                    capped = cap(text, thresh-4)
                    capmood = "%s" % cap(mood, thresh-8, wrap=("(", ")"))
                    self.shell.put("    %d: %s %s -> %s" % (_rid, capped, capmood, _next))

    def create_response(self, sen_id, _type, mood, _next, text):
        tup = (self._res_id_counter,mood,_next,text)
        if _type not in self.responses[sen_id].keys():
            self.responses[sen_id][_type] = []

        for res in self.responses[sen_id][_type]:
            if mood == res[1]:
                self.shell.put("Duplicate mood: %s" % mood)
                return

        self.responses[sen_id][_type].append(tup)
        self._res_id_counter += 1
        if _next not in self.created_topics:
            self.created_topics.append(_next)
        self.write_out()
        self.shell.put("NPC Response created: %s\nwith chartype: %s\nand mood: %s\nand topic: %s" % (text, _type, mood, _next))
        # TODO - prompt for topic creation

    def list_all_moods(self):
        ret = []
        for res in self.responses.keys():
            for _type in self.responses[res].keys():
                for _rid,mood,_next,text in self.responses[res][_type]:
                    ret.append(mood)
        return list(set(ret))

    def list_new_topics(self):
        ret = []
        for res in self.responses.keys():
            for _type in self.responses[res].keys():
                for _rid,mood,_next,text in self.responses[res][_type]:
                    ret.append(_next)
        return list(set(ret))

    def delete_response(self, sen_id, _type, res_id):
        if _type in self.responses[sen_id].keys():
            for res in self.responses[sen_id][_type]:
                if res[0] == res_id:
                    to_remove = res
                    break
            if not to_remove:
                self.shell.put("No matching response found.")
                return
            self.responses[sen_id][_type] = [a for a
                in self.responses[sen_id][_type] if a != to_remove]
            if len(self.responses[sen_id][_type]) == 0:
                self.responses[sen_id].pop(_type)
            self.write_out()
            self.shell.put("Deleted %s response to sentence %d" % (_type, sen_id))
        else:
            self.shell.put("No matching response found.")

    def create_sentence(self, tag, sentence):
        for sen in self.sentences:
            if sen[2] == sentence:
                self.shell.put("Duplicate sentence")
                return

        tup = (self._id_counter,tag,sentence)
        self.sentences.append(tup)
        self._id_counter += 1
        self.write_out()
        self.shell.put("Sentence created: %s\nwith tag: %s" % (sentence, tag))

    def edit_sentence(self, sen_id, tags, text):
        for sen in self.sentences:
            if sen[0] == sen_id:
                editing = sen
        if not editing:
            self.shell.put("Sentence ID %d not found" % sen_id)
            return
        self.sentences.pop(self.sentences.index(editing))
        self.sentences.append((sen_id, tags, text))
        self.write_out()
        self.shell.put("Success editing sentence %d" % sen_id)

    def delete_sentence(self, sen_id):
        for sen in self.sentences:
            if sen[0] == sen_id:
                to_remove = sen
                break

        self.sentences = [a for a in self.sentences if a != to_remove]
        self.responses.pop(sen_id)
        self.write_out()
        self.shell.put("Removed sentence '%s' and all responses" % to_remove[2])

    def load_file(self, topic):
        filename = "%s/%s.xml" % (self.path, topic)
        self.shell.sticker("Loading %s" % filename)

        def reset_sticker():
            time.sleep(.1)
            self.shell.remove_sticker("Loading %s" % filename)

        try:
            tree = ET.parse(filename)
            self._parse_tree(tree.getroot())
        except Exception as e:
            self.shell.put("Failed to load %s - %s" % (filename, e))
            self.shell.defer(reset_sticker)
            return False
        else:
            self.shell.put("Success loading %s" % filename)
            self.shell.defer(reset_sticker)
            return True

    def unload_file(self, topic):
        self.write_out()
        self.default_state()
        self.shell.put("Unloaded %s" % topic)

    def write_out(self, from_command=False):
        self.shell.sticker("Autosave On", new_output="Saving...")
        tree = self._build_tree()

        filename = "%s/%s.xml" % (self.path, self.cwt)

        def _file_exists(filename):
            try:
                with open(filename): pass
            except IOError:
                return False
            return True

        if _file_exists(filename):
            shutil.copyfile(filename, '%s.swp' % filename)
        else:
            f = open('%s.swp' % (filename), "w+")
            f.write(ET.tostring(tree))
            f.close()

        try:
            f = open(filename, "w+")
            f.write(ET.tostring(tree))
            f.close()
        except:
            if from_command:
                self.shell.put("Failed to write file")
            # restore from swap
            shutil.copyfile('%s.swp' % filename, filename)
        else:
            if from_command:
                self.shell.put("Success writing file %s" % filename)
            # remove swap on successful save
            os.remove('%s.swp' % filename)

        def reset_sticker():
            time.sleep(.1)
            self.shell.sticker("Saving...", new_output="Autosave On")
        self.shell.defer(reset_sticker)

    def _build_tree(self):
        root = Element('topic')
        root.set('name', self.cwt)
        for _id,tag,sentence in self.sentences:
            sen_element = SubElement(root, "sentence")
            sen_element.set('tag', tag)
            sen_element.set('sid', str(_id))
            text_element = SubElement(sen_element, "text")
            text_element.text = sentence
            if _id in self.responses.keys():
                res_element = SubElement(sen_element, "responses")
                for chartype in self.responses[_id]:
                    char_element = SubElement(res_element, "character")
                    char_element.set('type', chartype)
                    for _rid, mood,_next,response in self.responses[_id][chartype]:
                        mood_element = SubElement(char_element, 'mood')
                        mood_element.set('type', mood)
                        mood_element.set('next', _next)
                        mood_element.text = response
        return root

    def _parse_tree(self, root):
        self.sentences = []
        self.responses = defaultdict(dict)
        self.cwt = root.attrib['name']
        _id = self._id_counter
        for sentence in root:
            text = sentence.find('text').text
            try:
                _id = int(sentence.attrib['sid'])
            except:
                self._id_counter += 1
                _id = self._id_counter
            tup = (_id, sentence.attrib['tag'], text)
            self.sentences.append(tup)
            self.responses[_id] = {}
            responses = sentence.find('responses')
            if responses:
                for chartype in responses:
                    _type = chartype.attrib['type']
                    self.responses[_id][_type] = []
                    for mood in chartype:
                        tup = (self._res_id_counter, mood.attrib['type'],mood.attrib['next'],mood.text)
                        self.responses[_id][_type].append(tup)
                        if mood.attrib['next'] not in self.created_topics:
                            self.created_topics.append(mood.attrib['next'])
                        self._res_id_counter += 1
        self._id_counter = _id + 1
