import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    PHRASER_PATH = os.path.join(basedir, 'models{}phraser.model'.format(os.path.sep))