import re

from sklearn.feature_extraction.text import CountVectorizer

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

    while True:
        syote = input("What do you want to search from documents?\n")
        if syote == "q" or syote == 'Q':
            print("Thank you for using our Hakumoottori, see you soon!")
            break
        else:
            try:
                get_documents(syote)
            except KeyError:
                print("Check your query!")
            except SyntaxError:
                print("Check your query!")

query()
