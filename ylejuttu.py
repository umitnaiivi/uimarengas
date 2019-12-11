from urllib import request
from bs4 import BeautifulSoup

url = "https://yle.fi/uutiset/3-11112373"
html = request.urlopen(url).read().decode('utf8')

soup = BeautifulSoup(html, 'html.parser')

print("Tämän hetken uusimmat uutisaiheet ovat:\n")
teksti = soup.find_all('p')
kappaleet = []
for kappale in teksti:
    uusimmat.append(kappale.get_text())

print(kappaleet)