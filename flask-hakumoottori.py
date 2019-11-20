from flask import Flask, render_template
import re
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

app = Flask(__name__)

@app.route("/")

def read_file():
    try:
        file_name = ("C:\desktop-12-11-2019/docs.txt")
        with open(file_name, encoding="utf8") as f:
            documents = f.read().replace('\n', " ")
            documents = documents.split(sep="</article>")
            print(documents[0])
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

def home():
    return render_template("flask-haku.html")

if __name__ == "__main__":
    app.run(debug=True)