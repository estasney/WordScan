from rake_nltk import Rake


class KeywordExtractionMixin(object):

    def __init__(self):
        self.kw_finder = Rake()

    def extract_kw(self, text, scores=True):
        self.kw_finder.extract_keywords_from_text(text)
        if scores:
            return self.kw_finder.get_ranked_phrases_with_scores()
        else:
            return self.kw_finder.get_ranked_phrases()