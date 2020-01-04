from urllib import request
from bs4 import BeautifulSoup
import re

# Get links of recent news

def remove_duplicate_links(x):
    return list(dict.fromkeys(x))

url = "https://yle.fi/uutiset/osasto/news/"
html = request.urlopen(url).read().decode('utf8')
soup = BeautifulSoup(html, 'html.parser')
linkit = remove_duplicate_links([link.get("href") for link in soup.find_all("a", attrs={"href": re.compile("^https://yle.fi/uutiset/osasto/news")})])





# Get text of recent news

for linkki in linkit[4:]:
    url = linkit[7]
    html = request.urlopen(url).read().decode("utf8")
    soup = BeautifulSoup(html, "html.parser")

    print("artikkelin teksti:\n")
    teksti = soup.find_all("p")

kappaleet = []
for kappale in teksti:
    kappaleet.append(kappale.get_text())

kappaleet = " ".join(kappaleet)

print(kappaleet)
print(len(kappaleet))

#yhestä tollasesta "itemistä" ( esim str_linkit[2] ) saa
# <h1> - otsikon
# src=... - kuvan urlin
# <a href=... - artikkelin urlin
# muutin noi sisällöt stringeiks et niit ois helpompi tsiigaa,
# mut toi tietojen irrottaminen on salee helpompaa beautifulsoupin
# avulla - eli "linkit" muuttujan kautta
# link =  following    <a href="     and before      ">

print(type(linkit))