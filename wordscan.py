import easygui
import nltk
from nltk.tokenize.nist import NISTTokenizer
from nltk.corpus import wordnet
from rake_nltk import Rake
from components.preprocessing import FILTERS, preprocess_string
from collections import Counter
from components.wikiscraper import get_wiki_text
from components.avature import extract_quickview, _fetch_req
from operator import itemgetter


class WordCleanerMixin(object):

    def __init__(self, text):
        self.raw_text = text
        self.tokenizer = NISTTokenizer()
        self.lemmatizer = nltk.WordNetLemmatizer()
        self.wordnet_corpus = wordnet

    def clean_text(self, text=None):
        if not text:
            return preprocess_string(self.raw_text, FILTERS)
        else:
            return preprocess_string(text, FILTERS)

    def tokenize_text(self):
        return self.tokenizer.tokenize(self.raw_text)

    def pos_tag_text(self):
        return nltk.pos_tag(self.tokenize_text())

    def stem_tokens(self):
        pos_tagged_tokens = self.pos_tag_text()
        return [self.lemmatizer.lemmatize(token, self.get_wordnet_pos(tag)) if self.get_wordnet_pos(tag)
                else self.lemmatizer.lemmatize(token) for token, tag in pos_tagged_tokens]

    def get_wordnet_pos(self, treebank_tag):
        if treebank_tag.startswith('J'):
            return self.wordnet_corpus.ADJ
        elif treebank_tag.startswith('V'):
            return self.wordnet_corpus.VERB
        elif treebank_tag.startswith('N'):
            return self.wordnet_corpus.NOUN
        elif treebank_tag.startswith('R'):
            return self.wordnet_corpus.ADV
        else:
            return False


class KeywordExtractionMixin(object):

    def __init__(self):
        self.kw_finder = Rake()

    def extract_kw(self, text, scores=True):
        self.kw_finder.extract_keywords_from_text(text)
        if scores:
            return self.kw_finder.get_ranked_phrases_with_scores()
        else:
            return self.kw_finder.get_ranked_phrases()


class WikipediaMixin(object):

    def __init__(self, url):
        self.text = " ".join(get_wiki_text(url))


class AvatureMixin(object):

    def __init__(self, zip_path):
        self.text = self._df_to_text(zip_path)

    @staticmethod
    def _df_to_text(zip_path):
        df = extract_quickview(zip_path)
        return df['Resume'].values.tolist()


class CiscoJobsMixin(object):

    def __init__(self, req_id):
        self.text = self.fetch_req(req_id)

    @staticmethod
    def fetch_req(req_id):
        job_text = _fetch_req(req_id)
        return job_text


class WordSearch(object):

    def __init__(self, multiple, text=None):
        self.multiple = multiple
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
        WordSearch.__init__(self, multiple)
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

    def __init__(self, multiple):
        WordSearch.__init__(self, multiple)
        WordCleanerMixin.__init__(self, self.text)

    def _get_counts(self, topn=100):
        if self.multiple:
            all_text = [self.clean_text(doc) for doc in self.text]
            all_text = [words for doc in all_text for words in doc]
        else:
            all_text = self.clean_text(self.text)

        word_counter = Counter(all_text)
        counts = word_counter.most_common(n=topn)
        counts = ["{} : {}".format(word, count) for word, count in counts]
        self.show_results(counts)

    def run(self):
        return self._get_counts()


class WikiWordCounts(WordSearch, WordCleanerMixin, WikipediaMixin):

    def __init__(self):
        self.url = self.prompt_text()
        WikipediaMixin.__init__(self, self.url)
        WordSearch.__init__(self, multiple=False, text=self.text)
        WordCleanerMixin.__init__(self, self.text)

    def prompt_text(self):
        return easygui.enterbox(msg="Enter the wikipedia URL")

    def _get_counts(self, topn=100):
        if self.multiple:
            all_text = [self.clean_text(doc) for doc in self.text]
            all_text = [words for doc in all_text for words in doc]
        else:
            all_text = self.clean_text(self.text)

        word_counter = Counter(all_text)
        counts = word_counter.most_common(n=topn)
        counts = ["{} : {}".format(word, count) for word, count in counts]
        self.show_results(counts)

    def run(self):
        return self._get_counts()


class AvatureWordCounts(WordSearch, WordCleanerMixin, AvatureMixin):

    def __init__(self):
        self.zip_path = self.prompt_text()
        AvatureMixin.__init__(self, self.zip_path)
        WordSearch.__init__(self, multiple=True, text=self.text)
        WordCleanerMixin.__init__(self, self.text)

    def prompt_text(self):
        return easygui.fileopenbox(msg="Select the zip file to extract")

    def _get_counts(self, topn=100):
        all_docs = [self.clean_text(doc) for doc in self.text]
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

    def __init__(self):
        self.req_id = self.prompt_text()
        CiscoJobsMixin.__init__(self, self.req_id)
        WordSearch.__init__(self, multiple=False, text=self.text)
        WordCleanerMixin.__init__(self, self.text)

    def prompt_text(self):
        return easygui.enterbox(msg="Enter the Req ID")

    def _get_counts(self, topn=100):
        all_text = self.clean_text(self.text)
        word_counter = Counter(all_text)
        counts = word_counter.most_common(n=topn)
        counts = ["{} : {}".format(word, count) for word, count in counts]
        self.show_results(counts)

    def run(self):
        return self._get_counts()


class CiscoJobsKeywords(WordSearch, KeywordExtractionMixin, CiscoJobsMixin):

    def __init__(self):
        self.req_id = self.prompt_text()
        CiscoJobsMixin.__init__(self, self.req_id)
        WordSearch.__init__(self, multiple=False, text=self.text)
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


def prompt():
    mode = easygui.choicebox("Pick a mode", choices=["Extract Keywords", "Extract Keywords - Multiple", "Word Counts",
                                                     "Word Counts - Multiple", "Word Counts - Wikipedia",
                                                     "Extract Avature", "Extract Keywords - Cisco Jobs",
                                                     "Word Counts - Cisco Jobs"])

    if mode == 'Extract Keywords':
        return KeywordSearch(multiple=False)
    elif mode == 'Extract Keywords - Multiple':
        return KeywordSearch(multiple=True)
    elif mode == "Word Counts":
        return WordCounts(multiple=False)
    elif mode == 'Word Counts - Multiple':
        return WordCounts(multiple=True)
    elif mode == "Word Counts - Wikipedia":
        return WikiWordCounts()
    elif mode == "Extract Avature":
        return AvatureWordCounts()
    elif mode == "Extract Keywords - Cisco Jobs":
        return CiscoJobsKeywords()
    elif mode == "Word Counts - Cisco Jobs":
        return CiscoJobsWordCounts()


running = True
while running:
    result = prompt()
    if not result:
        running = False
        break
    result.run()
    if not easygui.ccbox("More?"):
        running = False
        break

