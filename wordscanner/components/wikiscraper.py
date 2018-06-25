import requests
from bs4 import BeautifulSoup as bs


def get_wiki_text(url):
    page = requests.get(url)
    soup = bs(page.content, 'html.parser')
    elements = soup.find("div", class_="mw-parser-output").contents
    texts = [e.get_text() for e in elements if e.name == 'p' or e.name == 'ul']
    return texts


class WikipediaMixin(object):

    def __init__(self, url):
        self.text = " ".join(get_wiki_text(url))
