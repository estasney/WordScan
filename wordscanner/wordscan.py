from collections import Counter
from operator import itemgetter

import easygui

from components.avature import AvatureMixin
from components.cisco_jobs import CiscoJobsMixin
from components.keywords import KeywordExtractionMixin, SkillExtractionMixin
from components.preprocessing import WordCleanerMixin
from components.ui import UserInterface
from components.wikiscraper import WikipediaMixin


class WordSearch(object):

    def __init__(self, multiple, stem, lemma, phrases, text=None):
        self.multiple = multiple
        self.stem = stem
        self.lemma = lemma
        self.phrases = phrases
        if not text:
            self.text = self.prompt_text()
        else:
            self.text = text

    def prompt_text(self):
        if not self.multiple:
            return easygui.codebox("Enter Text")
        all_text, getting_text = [], True
        while getting_text:
            text = easygui.codebox("Enter Text or Click Cancel")
            if text:
                all_text.append(text)
            else:
                break
        return all_text

    @staticmethod
    def show_results(results):
        if isinstance(results, list):
            easygui.codebox(text="\n".join(results))
        else:
            easygui.codebox(text=results)


class KeywordSearch(WordSearch, KeywordExtractionMixin):

    def __init__(self, multiple):
        WordSearch.__init__(self, multiple, stem=False, lemma=False, phrases=False)  # Not used with Rake
        KeywordExtractionMixin.__init__(self)

    def _get_keywords(self, scores=True):
        if self.multiple:
            all_text = " ".join(self.text)
        else:
            all_text = self.text
        kw = self.extract_kw(all_text, scores)
        if scores:
            kw = ["{:.1f} : {}".format(score, kw) for score, kw in kw]
        self.show_results(kw)

    def run(self):
        return self._get_keywords()


class SkillSearch(WordSearch, WordCleanerMixin, SkillExtractionMixin):

    def __init__(self, multiple):
        WordSearch.__init__(self, multiple, stem=False, lemma=False, phrases=False)
        WordCleanerMixin.__init__(self, self.stem, self.lemma, self.phrases)
        SkillExtractionMixin.__init__(self)

    def _get_skills(self):
        if self.multiple:
            all_text = [self.clean(doc) for doc in self.text]
            all_text = [words for doc in all_text for words in doc]
        else:
            all_text = self.clean(self.text)

        skills = [token for token in all_text if token in self.skills_set]
        skill_counter = Counter(skills)
        skill_data = []
        for word, count in skill_counter.most_common():
            occurence_count = self.skills_counts.get(word, 0)
            skill_data.append((word, count, occurence_count))
        skill_data = sorted(skill_data, key=itemgetter(2), reverse=True)
        counts = ["{} : {}: {}".format(word, count, occurence_count) for word, count, occurence_count in skill_data]
        self.show_results(counts)

    def run(self):
        return self._get_skills()


class WordCounts(WordSearch, WordCleanerMixin):

    def __init__(self, multiple, stem, lemma, phrases):
        WordSearch.__init__(self, multiple, stem, lemma, phrases)
        WordCleanerMixin.__init__(self, self.stem, self.lemma, self.phrases)

    def _get_counts(self, topn=100):
        if self.multiple:
            all_text = [self.clean(doc) for doc in self.text]
            all_text = [words for doc in all_text for words in doc]
        else:
            all_text = self.clean(self.text)

        word_counter = Counter(all_text)
        counts = word_counter.most_common(n=topn)
        counts = ["{} : {}".format(word, count) for word, count in counts]
        self.show_results(counts)

    def run(self):
        return self._get_counts()


class WikiWordCounts(WordSearch, WordCleanerMixin, WikipediaMixin):

    def __init__(self, stem, lemma, phrases):
        self.url = self.prompt_text()
        WikipediaMixin.__init__(self, self.url)
        WordSearch.__init__(self, multiple=False, text=self.text, stem=stem, lemma=lemma, phrases=phrases)
        WordCleanerMixin.__init__(self, self.stem, self.lemma, self.phrases)

    def prompt_text(self):
        return easygui.enterbox(msg="Enter the wikipedia URL")

    def _get_counts(self, topn=100):
        if self.multiple:
            all_text = [self.clean(doc) for doc in self.text]
            all_text = [words for doc in all_text for words in doc]
        else:
            all_text = self.clean(self.text)

        word_counter = Counter(all_text)
        counts = word_counter.most_common(n=topn)
        counts = ["{} : {}".format(word, count) for word, count in counts]
        self.show_results(counts)

    def run(self):
        return self._get_counts()


class AvatureWordCounts(WordSearch, WordCleanerMixin, AvatureMixin):

    def __init__(self, stem, lemma, phrases):
        self.zip_path = self.prompt_text()
        AvatureMixin.__init__(self, self.zip_path)
        WordSearch.__init__(self, multiple=True, text=self.text, stem=stem, lemma=lemma, phrases=phrases)
        WordCleanerMixin.__init__(self, self.stem, self.lemma, self.phrases)

    def prompt_text(self):
        return easygui.fileopenbox(msg="Select the zip file to extract")

    def _get_counts(self, topn=100):
        all_docs = [self.clean(doc) for doc in self.text]
        all_text = [words for doc in all_docs for words in doc]

        # Get occurrence counts
        all_words = set(all_text)
        word_counter = Counter(all_text)
        counts = word_counter.most_common(n=topn)

        word_occur = {word: 0 for word in all_words}
        for word in all_words:
            for doc in all_docs:
                if word in doc:
                    word_occur[word] = word_occur.get(word, 0) + 1

        word_freq = {word: count/len(all_docs) for word, count in word_occur.items()}

        str_counts = ["{} : {} : {:.2%}".format(word, count, word_freq.get(word, 0)) for word, count in counts]

        how_sort = easygui.choicebox(msg="How should we sort? By frequency or count?", choices=['Frequency', 'Count'])
        if how_sort == 'Count':
            self.show_results(str_counts)
        else:
            sorted_counts = sorted(
                [(word, count, word_freq.get(word, 0)) for word, count in counts], key=itemgetter(2), reverse=True)
            str_counts = ["{} : {} : {:.2%}".format(word, count, word_f) for word, count, word_f in sorted_counts]
            self.show_results(str_counts)

    def run(self):
        return self._get_counts()


class CiscoJobsWordCounts(WordSearch, WordCleanerMixin, CiscoJobsMixin):

    def __init__(self, stem, lemma, phrases):
        self.req_id = self.prompt_text()
        try:
            CiscoJobsMixin.__init__(self, self.req_id)
        except:
            easygui.msgbox("That Job was not found, please try another")
        WordSearch.__init__(self, multiple=False, text=self.text, stem=stem, lemma=lemma, phrases=phrases)
        WordCleanerMixin.__init__(self, self.stem, self.lemma, self.phrases)

    def prompt_text(self):
        return easygui.enterbox(msg="Enter the Req ID")

    def _get_counts(self, topn=100):
        all_text = self.clean(self.text)
        word_counter = Counter(all_text)
        counts = word_counter.most_common(n=topn)
        counts = ["{} : {}".format(word, count) for word, count in counts]
        self.show_results(counts)

    def run(self):
        return self._get_counts()


class CiscoJobsKeywords(WordSearch, KeywordExtractionMixin, CiscoJobsMixin):

    def __init__(self, *args, **kwargs):
        self.req_id = self.prompt_text()
        try:
            CiscoJobsMixin.__init__(self, self.req_id)
        except:
            easygui.msgbox("That Job was not found, please try another")
        WordSearch.__init__(self, multiple=False, text=self.text, stem=False, lemma=False, phrases=False)
        KeywordExtractionMixin.__init__(self)

    def prompt_text(self):
        return easygui.enterbox(msg="Enter the Req ID")

    def _get_keywords(self, scores=True):
        kw = self.extract_kw(self.text, scores)
        if scores:
            kw = ["{:.1f} : {}".format(score, kw) for score, kw in kw]
        self.show_results(kw)

    def run(self):
        return self._get_keywords()


mode_map = {'Keywords': [KeywordSearch, False],
            'Keywords - Multiple': [KeywordSearch, True],
            'Keywords - Cisco Jobs': CiscoJobsKeywords,
            'Skill Scan': [SkillSearch, False],
            'Skill Scan - Multiple': [SkillSearch, True],
            'Word Counts': [WordCounts, False],
            'Word Counts - Multiple': [WordCounts, True],
            'Word Counts - Avature Quick View': AvatureWordCounts,
            'Word Counts - Cisco Jobs': CiscoJobsWordCounts,
            'Word Counts - Wikipedia': WikiWordCounts}

secondary_options = [k for k in list(mode_map.keys()) if k.startswith('Word Counts')]

running = True
ui = UserInterface(mode_objects_map=mode_map, secondary_options=secondary_options)
while running:
    result = ui.prompt()
    if not result:
        running = False
        break
    result.run()
    if not easygui.ccbox("More?"):
        running = False
        break
