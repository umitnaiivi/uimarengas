from flask import Flask, render_template, request
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from urllib import request as rq
from bs4 import BeautifulSoup
import re

# Get links of recent news

url = "https://yle.fi/uutiset/osasto/news/"
html = rq.urlopen(url).read().decode('utf8')
soup = BeautifulSoup(html, 'html.parser')
linkit = [link.get("href") for link in
          soup.find_all("a", attrs={"href": re.compile("^https://yle.fi/uutiset/osasto/news")})]


# Get text of recent news

artikkelit = []
puhtaat_linkit = []
for linkki in linkit[5:-4]: # sliced off some non-news links such as an address to contact yle etc.
    html = rq.urlopen(linkki).read().decode("utf8")
    soup = BeautifulSoup(html, "html.parser")
    teksti = soup.article.find_all("p")     #teksti = list of paragraphs
    kappaleet = []
    for kappale in teksti:
        kappaleet.append(kappale.get_text())
    kappaleet = " ".join(kappaleet)
    artikkelit.append(kappaleet)
    puhtaat_linkit.append(linkki)

links_and_articles = list(zip(puhtaat_linkit, artikkelit))

app = Flask(__name__)

d = {"and": "&", "AND": "&",
     "or": "|", "OR": "|",
     "not": "1 -", "NOT": "1 -",
     "(": "(", ")": ")"}  # operator replacements


def rewrite_query(query):  # rewrite every token in the query
    return " ".join(rewrite_token(t) for t in query.split())

def rewrite_token(t):
    return d.get(t, 'sparse_td_matrix[t2i["{:s}"]].todense()'.format(t))  # Make retrieved rows dense


# Indeksoidaan sanaesiintymät
print("initializing indexing")

documents = artikkelit
cv = CountVectorizer(lowercase=True, binary=True, token_pattern='(?u)\\b\\w+\\b', ngram_range=(1,2))
print("indexing in progress")
sparse_matrix = cv.fit_transform(documents)
sparse_td_matrix = sparse_matrix.T.tocsr()
t2i = cv.vocabulary_
gv = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2", ngram_range=(1,2))
g_matrix = gv.fit_transform(documents).T.tocsr()
print("indexing completed. variable documents is now a list of articles as strings.")


@app.route("/")
def home():

    #get query from URL variable
    syote = request.args.get('query')

    matches = []

    if syote is not None:

        # this is the tdf if search we used earlier

        query_vec = gv.transform([syote]).tocsc()

        # Cosine similarity
        hits = np.dot(query_vec, g_matrix)

        # Rank hits
        ranked_scores_and_doc_ids = \
            sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]),
                   reverse=True)

        # Output result
        for i, (score, doc_idx) in enumerate(ranked_scores_and_doc_ids):
            doc = documents[doc_idx]
            matches.append({'score': score, 'name': doc[:10]})

    return render_template("yle-haku.html", matches=matches)

if __name__ == "__main__":
    app.run(debug=True)
