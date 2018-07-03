import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    PHRASER_PATH = os.path.join(basedir, 'models{}phraser.model'.format(os.path.sep))
    TFIDF_PATH = os.path.join(basedir, 'models{}tfidf_lem_bigrams.model'.format(os.path.sep))
    SKILLS_PATH = os.path.join(basedir, 'models{}skills.pkl'.format(os.path.sep))
