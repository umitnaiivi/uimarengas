from flask import Flask, render_template, request
import re
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

app = Flask(__name__)

d = {"and": "&", "AND": "&",
     "or": "|", "OR": "|",
     "not": "1 -", "NOT": "1 -",
     "(": "(", ")": ")"}  # operator replacements


def rewrite_query(query):  # rewrite every token in the query
    return " ".join(rewrite_token(t) for t in query.split())

def rewrite_token(t):
    return d.get(t, 'sparse_td_matrix[t2i["{:s}"]].todense()'.format(t))  # Make retrieved rows dense

def read_file():
    try:
        file_name = "enwiki-20181001-corpus.100-articles.txt"
        with open(file_name, encoding="utf8") as f:
            documents = f.read().replace('\n', " ")
            documents = documents.replace('\\\'', '\'')
            documents = documents.split(sep="</article>")
    except PermissionError:
        print("Incorrect path")
    except FileNotFoundError:
        print("Incorrect path")
    except KeyError:
        print("Incorrect path")
    except SyntaxError:
        print("Incorrect path")
    return documents

# Indeksoidaan sanaesiintymät
print("initializing indexing")

documents = read_file()
print("documents is now a list of strings.")
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
            doc = doc.split('>')
            doc[0] = doc[0].replace('<article name=', '')
            matches.append({'score': score, 'name': doc[0], 'document': doc[1]})

    return render_template("flask-haku.html", matches=matches)

if __name__ == "__main__":
    app.run(debug=True)
