from flask import Flask, render_template, request
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from urllib import request as rq
from bs4 import BeautifulSoup
import re
import nltk
import random
import math
from nltk.stem.snowball import SnowballStemmer
from nltk.cluster import KMeansClusterer, euclidean_distance, cosine_distance


def remove_duplicate_links(x):
    return list(dict.fromkeys(x))


def doc_counter():
    return str(len(artikkelit))


stemmer = SnowballStemmer("finnish")
url = "https://yle.fi/uutiset/18-34953"
html = rq.urlopen(url).read().decode('utf8')
soup = BeautifulSoup(html, 'html.parser')

testilinkki = soup.find_all(class_="yle__article__listItem__link", attrs={"href": re.compile("uutiset")})
testilinkki2 = remove_duplicate_links([link.get("href") for link in testilinkki])
# vajaat_linkit = remove_duplicate_links([link.get("href") for link in
#          soup.find_all("a", attrs={"href": re.compile("uutiset")})])
kokonaiset_linkit = [("https://yle.fi" + linkki) for linkki in testilinkki2]
regex = re.compile(r'd?-d?')
putsatut_linkit = list(filter(regex.search, kokonaiset_linkit))


# Get the text of recent news

artikkelit = []
puhtaat_linkit = []
for linkki in putsatut_linkit:
    html = rq.urlopen(linkki).read().decode("utf8")
    soup = BeautifulSoup(html, "html.parser")
    teksti = soup.article.find_all("p")     # teksti = list of paragraphs
    kappaleet = []
    for kappale in teksti:
        kappaleet.append(kappale.get_text())
    kappaleet = " ".join(kappaleet)
    artikkelit.append(kappaleet)
    puhtaat_linkit.append(linkki)


links_and_articles = list(zip(puhtaat_linkit, artikkelit))


# make a vocabulary from the words in the articles, tokenize and stem
# first turn list of articles into a string

vocabulary_0 = " ".join(artikkelit)
vocabulary_tokenized = nltk.word_tokenize(vocabulary_0)
vocabulary_stemmed = [stemmer.stem(word) for word in vocabulary_tokenized]

# tokenize and stem all the words in the articles themselves

artikkelit_tokenized = [nltk.word_tokenize(article) for article in artikkelit]
artikkelit_stemmed = [[stemmer.stem(word.lower()) for word in article] for article in artikkelit_tokenized]


# beginning of vector stuff

def add_vector(a, b):
    for i, x in enumerate(b):
        a[i] += x

def normalize(a):
    total = math.sqrt(sum(x ** 2 for x in a))
    return [x / total for x in a]


d = 10     # size of the index and context vectors
m = 1       # number of non-zero components in index vectors

###
# document vektoreiden rakentaminen on kysymysmerkki koska miten vitus niit nimiä iteroidaan
# tos artikkelit_stemmed_tuple ssa on siis ideana document vektorit sisältävän dictionaryn avaimet
###    document_vectors[artikkelit_stemmed_tuple[2]]

index_vector = {word: [0] * d for word in vocabulary_stemmed}
artikkelit_stemmed_tuple = tuple(tuple(x) for x in artikkelit_stemmed)
document_vectors = {item: [0.0] * d for item in artikkelit_stemmed_tuple}

# random indexing for the index and document vectors

for word in vocabulary_stemmed:
    random_positions = list(range(0, d))
    random.shuffle(random_positions)
    for i in random_positions[:m]:
        index_vector[word][i] = 1

for fileid in document_vectors:
    random_positions = list(range(0, d))
    random.shuffle(random_positions)
    for i in random_positions[:m]:
        document_vectors[fileid][i] = 1


# document vector making

for i in range(len(artikkelit_stemmed_tuple)):
    for word in artikkelit_stemmed_tuple[i]:
        add_vector(document_vectors[artikkelit_stemmed_tuple[i]], index_vector[word])


# clustering


n_clusters = 4  # number of clusters
vectors = [np.array(normalize(document_vectors[w])) for w in artikkelit_stemmed_tuple]
clusterer = KMeansClusterer(n_clusters, cosine_distance, avoid_empty_clusters=True, repeats=10)
clusters = clusterer.cluster(vectors, assign_clusters=True, trace=False)
cluster_docs = [set() for i in range(0, n_clusters)]
for i in range(0, len(clusters)):
    cluster_docs[clusters[i]].add(docs[i])
for i in range(0, n_clusters):
    print("Cluster #{:d}: {:s}".format(i, ", ".join(cluster_docs[i])))


# FLASK APP ALKAA



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

documents = artikkelit
cv = CountVectorizer(lowercase=True, binary=True, token_pattern='(?u)\\b\\w+\\b', ngram_range=(1,2))
sparse_matrix = cv.fit_transform(documents)
sparse_td_matrix = sparse_matrix.T.tocsr()
t2i = cv.vocabulary_
gv = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2", ngram_range=(1,2))
g_matrix = gv.fit_transform(documents).T.tocsr()



@app.route("/")
def home():

    syote = request.args.get('query')
    matches = []
    doc_counter()

    if syote is not None:

        syote = rewrite_query(syote)

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
            matches.append({'score': score, 'name': doc[:300]})

    return render_template("yle-haku.html", matches=matches, doc_counter=doc_counter())


if __name__ == "__main__":
    app.run(debug=True)
