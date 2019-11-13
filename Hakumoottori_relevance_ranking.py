import re

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


# Luetaan tekstitiedosto kovalevyltä:

def read_file():
    try:
        file_name = input("Where is your file?\n")
        with open(file_name, encoding="utf8") as f:
            documents = f.read().replace('\n', " ")
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

documents = read_file()
cv = CountVectorizer(lowercase=True, binary=True, token_pattern='(?u)\\b\\w+\\b')
sparse_matrix = cv.fit_transform(documents)
sparse_td_matrix = sparse_matrix.T.tocsr()
t2i = cv.vocabulary_

gv = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
g_matrix = gv.fit_transform(documents).T.tocsr()


def search_gutenberg(query_string):
    # Vectorize query string
    query_vec = gv.transform([query_string]).tocsc()

    # Cosine similarity
    hits = np.dot(query_vec, g_matrix)

    # Rank hits
    ranked_scores_and_doc_ids = \
        sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]),
               reverse=True)

    # Output result
    print("Your query '{:s}' matches the following documents:".format(query_string))
    for i, (score, doc_idx) in enumerate(ranked_scores_and_doc_ids):
        print("Doc #{:d} (score: {:.4f}): {:s}".format(i, score, documents[doc_idx]))
    print()

d = {"and": "&", "AND": "&",
     "or": "|", "OR": "|",
     "not": "1 -", "NOT": "1 -",
     "(": "(", ")": ")"}  # operator replacements


def rewrite_query(query):  # rewrite every token in the query
    return " ".join(rewrite_token(t) for t in query.split())

def rewrite_token(t):
    return d.get(t, 'sparse_td_matrix[t2i["{:s}"]].todense()'.format(t))  # Make retrieved rows dense

def get_documents(syote):
    hits_matrix = eval(rewrite_query(syote))
    hits_list = list(hits_matrix.nonzero()[1])
    if not hits_list: # if there are no documents found for the search word, i.e. the hits_list is empty:
        print("No matching documents!")
    else:
        for i, doc_idx in enumerate(hits_list[:10]):
            print("Matching doc #{:d}: {:s}".format(i+1, re.match(r'(?:[^.:;]+[.:;]){1}', documents[doc_idx]).group())) # gets the first sentence

# käyttöliittymä, joka kysyy syötteen:
def query():
    print("Welcome!")
    print("This is Hakumoottori, a search engine for words in a document")
    print("Here are some examples for you:")
    print("NOT word1 or word2")
    print("( NOT word1 OR word2 ) AND word3")
    print("Press q to quit")
    print("Press r to return to main menu")

    while True:
        syote = input("What do you want to search from documents?\n")
        if syote == "q" or syote == 'Q':
            print("Thank you for using our Hakumoottori, see you soon!")
            break
        if syote == "r" or syote == "R":
            main()
        else:
            try:
                get_documents(syote)
            except KeyError:
                print("Check your query!")
            except SyntaxError:
                print("Check your query!")


def main():
    while True:
        syote = input("Do you want to use a boolean or tfidf engine?\n"
                      "(1): Boolean\n"
                      "(2): TF-IDF\n"
                      "(Q): quit\n")
        if syote == "q" or syote == "Q":
            print("bye")
            break
        if syote == "1":
            print("initializing boolean engine...")
            query()

        elif syote == "2":
            try:
                print("initializing tfidf engine...")
                search_gutenberg("helsinki")
            except KeyError:
                print("Check your query!")
            except SyntaxError:
                print("Check your query!")


main()
