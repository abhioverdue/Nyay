import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

USE_TFIDF = True

_vectorizer = None
_fitted = False

LEGAL_CORPUS_SEED = [
    "section 138 negotiable instruments act cheque dishonour insufficient funds convicted acquitted",
    "section 420 ipc cheating fraud mens rea dishonest intention convicted acquitted",
    "section 304b ipc dowry death cruelty harassment presumption section 113b evidence act",
    "convicted acquitted accused complainant judgment court dismissed settled",
    "supreme court high court sessions court magistrate first class",
    "evidence act presumption rebuttal burden of proof beyond reasonable doubt",
    "notice statutory period demand payment 30 days dishonour",
    "bail imprisonment fine sentence rigorous simple",
    "maharashtra tamil nadu karnataka delhi rajasthan uttar pradesh india",
    "legal reasoning ratio decidendi obiter dicta precedent citation",
    "cheque bounce hand loan repayment security ex parte",
    "dowry harassment cruelty burns hanging poisoning",
    "mens rea intent fraud investment scheme builder insolvency",
    "cross examination witness deposition corroboration",
]

def _get_vectorizer(corpus=None):
    global _vectorizer, _fitted
    if _vectorizer is None:
        _vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=512, sublinear_tf=True, min_df=1)
    if not _fitted:
        seed = list(LEGAL_CORPUS_SEED) + (corpus or [])
        _vectorizer.fit(seed)
        _fitted = True
    return _vectorizer

def embed(texts):
    vec = _get_vectorizer(texts)
    matrix = vec.transform(texts).toarray().astype(np.float32)
    matrix = normalize(matrix, norm="l2")
    return matrix.tolist()

def embed_single(text):
    return embed([text])[0]
