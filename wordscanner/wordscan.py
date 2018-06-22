from collections import Counter
from operator import itemgetter

import easygui

from components.avature import AvatureMixin
from components.cisco_jobs import CiscoJobsMixin
from components.keywords import KeywordExtractionMixin
from components.preprocessing import WordCleanerMixin
from components.ui import UserInterface
from components.wikiscraper import WikipediaMixin


class WordSearch(object):

    def __init__(self, multiple, stem, lemma, text=None):
        self.multiple = multiple
        self.stem = stem
        self.lemma = lemma
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
        WordSearch.__init__(self, multiple, stem=False, lemma=False)  # Not used with Rake
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


class WordCounts(WordSearch, WordCleanerMixin):

    def __init__(self, multiple, stem, lemma):
        WordSearch.__init__(self, multiple, stem, lemma)
        WordCleanerMixin.__init__(self, self.stem, self.lemma)

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

    def __init__(self, stem, lemma):
        self.url = self.prompt_text()
        WikipediaMixin.__init__(self, self.url)
        WordSearch.__init__(self, multiple=False, text=self.text, stem=stem, lemma=lemma)
        WordCleanerMixin.__init__(self, self.stem, self.lemma)

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

    def __init__(self, stem, lemma):
        self.zip_path = self.prompt_text()
        AvatureMixin.__init__(self, self.zip_path)
        WordSearch.__init__(self, multiple=True, text=self.text, stem=stem, lemma=lemma)
        WordCleanerMixin.__init__(self, self.stem, self.lemma)

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

    def __init__(self, stem, lemma):
        self.req_id = self.prompt_text()
        try:
            CiscoJobsMixin.__init__(self, self.req_id)
        except:
            easygui.msgbox("That Job was not found, please try another")
        WordSearch.__init__(self, multiple=False, text=self.text, stem=stem, lemma=lemma)
        WordCleanerMixin.__init__(self, self.stem, self.lemma)

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
        WordSearch.__init__(self, multiple=False, text=self.text, stem=False, lemma=False)
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