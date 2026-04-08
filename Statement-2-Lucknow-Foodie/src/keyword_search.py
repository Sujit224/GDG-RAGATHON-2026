from sklearn.feature_extraction.text import TfidfVectorizer

def build_tfidf(corpus):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    return vectorizer, tfidf_matrix