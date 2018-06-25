import easygui


class UserInterface(object):

    def __init__(self, mode_objects_map, secondary_options):
        self.mode_objects_map = mode_objects_map
        self.secondary_options = secondary_options

    def prompt(self):
        choices = list(self.mode_objects_map.keys())
        mode = easygui.choicebox("Pick a mode", choices=choices)
        return self._map_mode(mode)

    def _map_mode(self, mode):
        if mode in self.secondary_options:
            secondary_selected = easygui.multchoicebox(title="Select Cleaning", msg="Select Preprocessing to Perform",
                                                       choices=['Stem', 'Lemmatize', 'Phrase Detection'])
            stem = True if 'Stem' in secondary_selected else False
            lemma = True if 'Lemmatize' in secondary_selected else False
            phrases = True if 'Phrase Detection' in secondary_selected else False
            obj = self.mode_objects_map[mode]
            if isinstance(obj, list):
                multiple = obj[1]
                obj = obj[0]
                return obj(stem=stem, lemma=lemma, phrases=phrases, multiple=multiple)
            else:
                return obj(stem=stem, lemma=lemma, phrases=phrases)
        else:
            return self.mode_objects_map[mode]()
