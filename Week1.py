from urllib import request
from nltk import word_tokenize

from bs4 import BeautifulSoup

url = "https://yle.fi/uutiset/3-11042880"
html = request.urlopen(url).read().decode('utf8')

raw = BeautifulSoup(html, 'html.parser').get_text()
tokens = word_tokenize(raw)
print(tokens)