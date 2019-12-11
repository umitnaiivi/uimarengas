from urllib import request
from bs4 import BeautifulSoup

url = "https://yle.fi/uutiset/3-11112373"
html = request.urlopen(url).read().decode('utf8')

soup = BeautifulSoup(html, 'html.parser')

print("Tämän hetken uusimmat uutisaiheet ovat:\n")
otsikot = soup.find_all('p')[1:6]
uusimmat = []
for otsikko in otsikot:
    uusimmat.append(otsikko.get_text())

aika = soup.find_all('time')[0:5]
ajat = []
for a in aika:
    ajat.append(a.get_text())

uusi = zip(ajat, uusimmat)
for i in uusi:
    print(i[0] + ': '+ i[1])



