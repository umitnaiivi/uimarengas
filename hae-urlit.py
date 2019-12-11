from urllib import request
from bs4 import BeautifulSoup
import re

url = "https://yle.fi/uutiset/osasto/news/"
html = request.urlopen(url).read().decode('utf8')

soup = BeautifulSoup(html, 'html.parser')
linkit2 = []
print("linkit ovat:\n")
linkit = soup.find_all("a", href=re.compile('^https://yle.fi/uutiset/osasto/news/.+'))

str_linkit = [str(item) for item in linkit]


#tulostus että näät, mikä file structure
print(str_linkit[4])
