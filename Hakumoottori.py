# test

from sklearn.feature_extraction.text import CountVectorizer

documents = ["I heheheh This is a silly example",
             "A better example",
             "Nothing to see here",
             "This is a great and long example"]


cv = CountVectorizer(lowercase=True, binary=True)
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
    if not hits_list:
        print("No matching documents!")
    else:
        for i, doc_idx in enumerate(hits_list):
            print("Matching doc #{:d}: {:s}".format(i, documents[doc_idx]))

def query():
    print("This is a search engine for words in a document")
    print("Here are some examples for you:")
    print("NOT word1 or word2")
    print("( NOT word1 OR word2 ) AND word3")
    print("Press q to quit and print result")

    while True:
        syote = input("What do you want to search from documents?")
        if syote == "q" or syote == 'Q':
            print("Thank you, see you soon!")
            break
        else:
            try:
                get_documents(syote)
            except KeyError:
                print("Check your query!")
            except SyntaxError:
                print("Check your query!")

query()
