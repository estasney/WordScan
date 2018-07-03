from rake_nltk import Rake
import pickle
from app_config import Config


class KeywordExtractionMixin(object):

    def __init__(self):
        self.kw_finder = Rake()

    def extract_kw(self, text, scores=True):
        self.kw_finder.extract_keywords_from_text(text)
        if scores:
            return self.kw_finder.get_ranked_phrases_with_scores()
        else:
            return self.kw_finder.get_ranked_phrases()


class SkillExtractionMixin(object):

    def __init__(self, skills_fp=Config.SKILLS_PATH):
        self._load_skills(skills_fp)

    def _load_skills(self, skills_fp):
        with open(skills_fp, 'rb') as pickle_file:
            skills_counts = pickle.load(pickle_file)
            self.skills_counts = skills_counts
            self.skills_set = set(list(skills_counts.keys()))
