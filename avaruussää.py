from urllib import request
from bs4 import BeautifulSoup

url = "https://ilmatieteenlaitos.fi/revontulet-ja-avaruussaa"
html = request.urlopen(url).read().decode('utf8')

soup = BeautifulSoup(html, 'html.parser')

print("Kerron sinulle tämän päivän avaruussään:\n")

# tulostetaan ensimmäinen otsikko, joka kertoo avaruussäästä:
otsikot = [o.text for o in soup.find_all('h1')]
print(otsikot[1])

# tulostetaan teksti, joka koskee avaruussäätä:
tekstit = [t.text for t in soup.find_all('p')]
for t in tekstit[:2]:
    print(t)

# haetaan taulokosta revontulten todennäköisyys ja tulostetaan ne:
taulukko = [t.text for t in soup.find_all('td')]
aika = [line for line in taulukko[1:4]]
saa = [line for line in taulukko[5:]]
rivit = [line for line in zip(aika, saa)]

print(taulukko[4])
for rivi in rivit:
    print(rivi[0] + ': ' + rivi[1])

# ohjelmasta saa elegantimman näköisen käyttämällä esim regexiä rivin alussa olevien tyhjien poistamiseen