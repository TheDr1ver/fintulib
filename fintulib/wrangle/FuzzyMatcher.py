import pandas as pd
import numpy as np
import dill as pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
from scipy.sparse import rand

try:
    import sparse_dot_topn.sparse_dot_topn as ct
except ModuleNotFoundError:
    print("This module requires the sparse_dot_topn library \
    accelerated sparse matrix multiplication,which can be found \
    at https://github.com/ing-bank/sparse_dot_topn.")
    import sys
    sys.exit(1)


def cossim_top(A, B, ntop, lower_bound=0):
    B = B.tocsr()

    M, _ = A.shape
    _, N = B.shape

    idx_dtype = np.int32

    nnz_max = M*ntop

    indptr = np.empty(M+1, dtype=idx_dtype)
    indices = np.empty(nnz_max, dtype=idx_dtype)
    data = np.empty(nnz_max, dtype=A.dtype)

    ct.sparse_dot_topn(
        M, N, np.asarray(A.indptr, dtype=idx_dtype),
        np.asarray(A.indices, dtype=idx_dtype),
        A.data,
        np.asarray(B.indptr, dtype=idx_dtype),
        np.asarray(B.indices, dtype=idx_dtype),
        B.data,
        ntop,
        lower_bound,
        indptr, indices, data)

    return csr_matrix((data, indices, indptr), shape=(M, N))


class FuzzyMatcher:
    """A fuzzy string matcher based on TF-IDF weighted cosine similarity of character n-grams.
    This class uses the accelerated sparse matrix multiplication library from \
    https://github.com/ing-bank/sparse_dot_topn and cython - please install before use."""

    def __init__(self, n_grams=3):
        """Create a new fuzzy matcher.

        :param n_grams: The number of characters to be used in n-grams.
        See https://en.wikipedia.org/wiki/N-gram for more details.
        """
        def ngrams_extractor(string):
            string = re.sub(r'[,-./]|\sBD', r'', string)
            ngrams = zip(*[string[i:] for i in range(n_grams)])
            return [''.join(ngram) for ngram in ngrams]

        self.vectorizer = TfidfVectorizer(analyzer=ngrams_extractor, norm="l2")
        self.n_grams_n = n_grams
        self.is_fitted = False
        self.corpus = None
        self.corpus_vect = None
        self.attributes = ["vectorizer", "n_grams_n",
                           "is_fitted", "corpus", "corpus_vect"]

    def save_state(self, filename):
        """Save the current state of this matcher (including vocabulary and corpus)
        to a file.

        :params filename: The path/name of the file to save to.
        """
        state = {}
        for a in self.attributes:
            state[a] = getattr(self, a)
        pickle.dump(state, open(filename, "wb"))

    def load_state(self, filename):
        """Read the state of this matcher (including vocabulary and corpus)
        from a previously saved file.

        :params filename: The path/name of the file to read from to.
        """
        state = pickle.load(open(filename, "rb"))
        for a in self.attributes:
            setattr(self, a, state[a])

    def fit(self, strings):
        """Fit a set of raw strings - this set is used to calculate inverse document frequency (IDF)
        of n-grams.

        :param strings: An iterable of raw strings on which the inverse document frequency of n-grams
                        for the matcher is calculated.
        """
        lc_strings = self._to_lowercase(strings)
        self.vectorizer.fit(lc_strings)
        self.is_fitted = True

    def add_corpus(self, corpus):
        """Vectorize a corpus of strings to match against. If `fit()` hasn't been called yet,
        the inverse document frequency is calculated from the corpus.

        :param corpus: An interable of strings that will be used as the corpus for `match_against_corpus()`.
        """
        lc_corpus = self._to_lowercase(corpus)
        if self.is_fitted == False:
            print("Fitting vectorizer to corpus...")
            corpus_vect = self.vectorizer.fit_transform(lc_corpus).transpose()
        else:
            corpus_vect = self.vectorizer.transform(lc_corpus).transpose()
        self.corpus = corpus
        self.corpus_vect = corpus_vect
        self.is_fitted = True

    def match_against_corpus(self, strings, top_n=5, threshold=0):
        """Match a set of strings against the corpus, returning the top n results above the threshold.

        :param strings: The strings to match against the corpus.
        :param top_n: The number of potential matches to return for each string.
        :param threshold: Minimum score - all potential matches below this score will be discarded.
        """
        if self.corpus_vect == None:
            raise Exception("Must add a corpus before matching against it.")

        lc_strings = self._to_lowercase(strings)
        strings_vect = self.vectorizer.transform(lc_strings)

        return self._match_feature_matrices(strings, self.corpus, strings_vect, self.corpus_vect, top_n, threshold)

    def match_sets(self, left_strings, right_strings, top_n=5, threshold=0):
        """Match the set `left_strings` against the set `right_strings`,
        returning for each string in `left_strings` the `top_n` matches in `right_strings`
        with score greater than `threshold`.

        :param left_strings: The strings to match against `right_strings`.
        :param right_strings: The strings that `left_strings` will be matched against.
        :param top_n: The number of potential matches to return for each string.
        :param threshold: Minimum score - all potential matches below this score will be discarded.
        """
        if self.is_fitted == False:
            raise Exception(
                "Must fit a dictionary for IDF-weights before matching. Use `.fit()`.")

        lc_left_strings = self._to_lowercase(left_strings)
        lc_right_strings = self._to_lowercase(right_strings)

        left_vect = self.vectorizer.transform(lc_left_strings)
        right_vect = self.vectorizer.transform(lc_right_strings).transpose()

        return self._match_feature_matrices(left_strings, right_strings, left_vect, right_vect, top_n, threshold)

    def score_pair(self, left_string, right_string):
        """Calculate the matching score for two strings.

        :param left_string: The string to match against `right_string`.
        :param right_string: The string to match against `left_string`.
        """
        if self.is_fitted == False:
            raise Exception(
                "Must fit a dictionary for IDF-weights before matching. Use `.fit()`.")

        lc_left_string = left_string.lower()
        lc_right_string = right_string.lower()

        left_vect = self.vectorizer.transform([lc_left_string])
        right_vect = self.vectorizer.transform([lc_right_string]).transpose()

        return np.multiply(left_vect, right_vect)[0,0]

    def _to_lowercase(self, strings):
        return [s.lower() for s in strings]

    def _match_feature_matrices(self, left_strings, right_strings, left_vect, right_vect, top_n, threshold):
        print("Calculating cosine similarities...this might take a while...")
        c = cossim_top(left_vect, right_vect, top_n, threshold)

        non_zeros = c.nonzero()

        sparserows = non_zeros[0]
        sparsecols = non_zeros[1]

        nr_matches = sparsecols.size

        lookup_indices = []
        lookups = []
        results = []

        lookup_index = sparserows[0]
        lookup = left_strings[sparserows[0]]
        entry = (c.data[0], sparsecols[0], right_strings[sparsecols[0]])
        result = [entry]

        for index in range(1, nr_matches):
            if sparserows[index] != sparserows[index-1]:
                # new lookup entry - save the previous result list
                # and create a new result list
                lookup_indices.append(lookup_index)
                lookups.append(lookup)
                results.append(result)
                lookup_index = sparserows[index]
                lookup = left_strings[sparserows[index]]
                result = []
            entry = (c.data[index], sparsecols[index],
                     right_strings[sparsecols[index]])
            result.append(entry)

        lookup_indices.append(lookup_index)
        lookups.append(lookup)
        results.append(result)

        return pd.DataFrame({
            'lookup': lookups,
            'results': results}, index=lookup_indices)
