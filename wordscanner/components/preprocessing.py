import re
import nltk
nltk.data.path.append(r"wordscanner/nltk_data_folder")
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords as sw
from nltk import wordpunct_tokenize
from nltk import WordNetLemmatizer
from nltk import sent_tokenize
from nltk import pos_tag
from nltk.stem.porter import PorterStemmer
import string
from gensim.models.phrases import Phraser
from app_config import Config


STOPWORDS = frozenset([
    'all', 'six', 'just', 'less', 'being', 'indeed', 'over', 'move', 'anyway', 'four', 'not', 'own', 'through',
    'using', 'fify', 'where', 'mill', 'only', 'find', 'before', 'one', 'whose', 'system', 'how', 'somewhere',
    'much', 'thick', 'show', 'had', 'enough', 'should', 'to', 'must', 'whom', 'seeming', 'yourselves', 'under',
    'ours', 'two', 'has', 'might', 'thereafter', 'latterly', 'do', 'them', 'his', 'around', 'than', 'get', 'very',
    'de', 'none', 'cannot', 'every', 'un', 'they', 'front', 'during', 'thus', 'now', 'him', 'nor', 'name', 'regarding',
    'several', 'hereafter', 'did', 'always', 'who', 'didn', 'whither', 'this', 'someone', 'either', 'each', 'become',
    'thereupon', 'sometime', 'side', 'towards', 'therein', 'twelve', 'because', 'often', 'ten', 'our', 'doing', 'km',
    'eg', 'some', 'back', 'used', 'up', 'go', 'namely', 'computer', 'are', 'further', 'beyond', 'ourselves', 'yet',
    'out', 'even', 'will', 'what', 'still', 'for', 'bottom', 'mine', 'since', 'please', 'forty', 'per', 'its',
    'everything', 'behind', 'does', 'various', 'above', 'between', 'it', 'neither', 'seemed', 'ever', 'across', 'she',
    'somehow', 'be', 'we', 'full', 'never', 'sixty', 'however', 'here', 'otherwise', 'were', 'whereupon', 'nowhere',
    'although', 'found', 'alone', 're', 'along', 'quite', 'fifteen', 'by', 'both', 'about', 'last', 'would',
    'anything', 'via', 'many', 'could', 'thence', 'put', 'against', 'keep', 'etc', 'amount', 'became', 'ltd', 'hence',
    'onto', 'or', 'con', 'among', 'already', 'co', 'afterwards', 'formerly', 'within', 'seems', 'into', 'others',
    'while', 'whatever', 'except', 'down', 'hers', 'everyone', 'done', 'least', 'another', 'whoever', 'moreover',
    'couldnt', 'throughout', 'anyhow', 'yourself', 'three', 'from', 'her', 'few', 'together', 'top', 'there', 'due',
    'been', 'next', 'anyone', 'eleven', 'cry', 'call', 'therefore', 'interest', 'then', 'thru', 'themselves',
    'hundred', 'really', 'sincere', 'empty', 'more', 'himself', 'elsewhere', 'mostly', 'on', 'fire', 'am', 'becoming',
    'hereby', 'amongst', 'else', 'part', 'everywhere', 'too', 'kg', 'herself', 'former', 'those', 'he', 'me', 'myself',
    'made', 'twenty', 'these', 'was', 'bill', 'cant', 'us', 'until', 'besides', 'nevertheless', 'below', 'anywhere',
    'nine', 'can', 'whether', 'of', 'your', 'toward', 'my', 'say', 'something', 'and', 'whereafter', 'whenever',
    'give', 'almost', 'wherever', 'is', 'describe', 'beforehand', 'herein', 'doesn', 'an', 'as', 'itself', 'at',
    'have', 'in', 'seem', 'whence', 'ie', 'any', 'fill', 'again', 'hasnt', 'inc', 'thereby', 'thin', 'no', 'perhaps',
    'latter', 'meanwhile', 'when', 'detail', 'same', 'wherein', 'beside', 'also', 'that', 'other', 'take', 'which',
    'becomes', 'you', 'if', 'nobody', 'unless', 'whereas', 'see', 'though', 'may', 'after', 'upon', 'most', 'hereupon',
    'eight', 'but', 'serious', 'nothing', 'such', 'why', 'off', 'a', 'don', 'whereby', 'third', 'i', 'whole', 'noone',
    'sometimes', 'well', 'amoungst', 'yours', 'their', 'rather', 'without', 'so', 'five', 'the', 'first', 'with',
    'make', 'once', 'data', 'development', 'web', 'applications', 'developed', 'experience', 'summary', 'description'
] + sw.words('english'))

RE_PUNCT = re.compile(r'([%s])+' % re.escape(string.punctuation), re.UNICODE)
RE_TAGS = re.compile(r"<([^>]+)>", re.UNICODE)
RE_NUMERIC = re.compile(r"[0-9]+", re.UNICODE)
RE_NONALPHA = re.compile(r"\W", re.UNICODE)
RE_AL_NUM = re.compile(r"([a-z]+)([0-9]+)", flags=re.UNICODE)
RE_NUM_AL = re.compile(r"([0-9]+)([a-z]+)", flags=re.UNICODE)
RE_WHITESPACE = re.compile(r"(\s)+", re.UNICODE)

FILTERS = [lambda x: x.lower(),
           lambda x: RE_TAGS.sub("", x),
           lambda x: RE_PUNCT.sub(" ", x),
           lambda x: RE_WHITESPACE.sub(" ", x),
           lambda x: RE_NUMERIC.sub("", x),
           lambda x: " ".join([word for word in x.split() if word not in STOPWORDS]),
           lambda x: " ".join([word for word in x.split() if len(word)>=3])]


def preprocess_string(s, filters=FILTERS, lemma=False, stem=False, phrases=False):
    if lemma:
        s = _tokenize(s)
    for f in filters:
        s = f(s)
    if stem:
        stemmer = PorterStemmer()
        s = " ".join([stemmer.stem(word) for word in s.split()])
    if phrases is not False and phrases is not None:
        s = " ".join(phrases[s.split()])
    return s.split()


def preprocess_string_to_sentences(s, filters=FILTERS, lemma=False, stem=False, phrases=False):
    if lemma:
        sentences = _tokenize(s, as_sentences=True)
    else:
        sentences = sent_tokenize(s)

    def text_filter(sentence):
        for f in filters:
            sentence = f(sentence)
        return sentence

    def stem_text(text):
        stem_sent = " ".join([stemmer.stem(word) for word in text.split()])
        return stem_sent

    def phrase_text(text):
        phrased_sent = " ".join(phrases[text.split()])
        return phrased_sent

    sentences = map(text_filter, sentences)

    if stem:
        stemmer = PorterStemmer()
        sentences = map(stem_text, sentences)

    if phrases is not False and phrases is not None:
        sentences = map(phrase_text, sentences)

    return list(sentences)


def _tokenize(text, as_sentences=False):
    sentences = sent_tokenize(text)

    def tokenize_sentence(sent):
        return [_lemmatize(token, tag) for token, tag in pos_tag(wordpunct_tokenize(sent))]

    sentence_tokens = map(tokenize_sentence, sentences)

    if as_sentences:
        return [" ".join(sentence) for sentence in sentence_tokens]
    else:
        return " ".join([token for sentence in sentence_tokens for token in sentence])


def _lemmatize(token, tag):
    tag = {
        'N': wn.NOUN,
        'V': wn.VERB,
        'R': wn.ADV,
        'J': wn.ADJ
    }.get(tag[0], wn.NOUN)

    return WordNetLemmatizer().lemmatize(token, tag)


class WordCleanerMixin(object):

    def __init__(self, stem, lemma, phrases=False):
        self.lemma = lemma
        self.stem = stem
        self.phrases = self.load_phraser(phrases)

    @staticmethod
    def load_phraser(use_phrases):
        if use_phrases:
            return Phraser.load(Config.PHRASER_PATH)
        else:
            return False

    def clean(self, doc):
        return preprocess_string(doc, filters=FILTERS, lemma=self.lemma, stem=self.stem, phrases=self.phrases)


class SentenceCleanerMixin(object):
    def __init__(self, stem, lemma, phrases=False):
        self.lemma = lemma
        self.stem = stem
        self.phrases = phrases

    @staticmethod
    def load_phraser(use_phrases):
        if use_phrases:
            return Phraser.load(Config.PHRASER_PATH)
        else:
            return False

    def clean(self, doc):
        return preprocess_string_to_sentences(doc, filters=FILTERS, lemma=self.lemma, stem=self.stem, phrases=self.phrases)