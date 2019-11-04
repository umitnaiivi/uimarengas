from urllib import request
from bs4 import BeautifulSoup

url = "https://ilmatieteenlaitos.fi/revontulet-ja-avaruussaa"
html = request.urlopen(url).read().decode('utf8')

soup = BeautifulSoup(html, 'html.parser')

print("Kerron sinulle tämän päiväisen avaruussään:\n")

# find_all -metodi luo listan asioista, joiden tag on p
# käydään läpi for-loopilla:
for p in soup.find_all('p'):
    print(p.get_text())


# Ongelma: miten filtteröidä hakukomentoa paremmin? Esimerkiks tää printtaa
# kaikki 'p' tägätyt tekstit, vaikka vaan osa tosta saattaa on olennaista