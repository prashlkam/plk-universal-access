import re
from collections import Counter, defaultdict

WORD_RE = re.compile(r"[a-zA-Z']+")

class PredictionModel:
    def __init__(self):
        self.unigrams = Counter()
        self.bigrams = defaultdict(Counter)
        self.vocab = set()
        self.total_unigrams = 0

    def train_from_text(self, text):
        text = text.lower()
        tokens = WORD_RE.findall(text)
        prev = None
        for t in tokens:
            self.unigrams[t] += 1
            self.total_unigrams += 1
            self.vocab.add(t)
            if prev is not None:
                self.bigrams[prev][t] += 1
            prev = t

    def train_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            self.train_from_text(f.read())

    def _prefix_candidates(self, prefix, max_candidates=200):
        prefix = prefix.lower()
        results = [w for w in self.vocab if w.startswith(prefix)]
        results.sort(key=lambda w: -self.unigrams[w])
        return results[:max_candidates]

    def predict(self, prefix, prev_word=None, k=6, lambda_context=0.6):
        prefix = prefix.lower()
        if prefix == "": return []
        candidates = self._prefix_candidates(prefix)
        scored = []
        for w in candidates:
            uni_score = self.unigrams[w] / (self.total_unigrams + 1)
            bi_score = 0.0
            if prev_word and prev_word.lower() in self.bigrams:
                bi_count = self.bigrams[prev_word.lower()].get(w, 0)
                total_bi = sum(self.bigrams[prev_word.lower()].values()) + 1
                bi_score = bi_count / total_bi
            score = (1 - lambda_context) * uni_score + lambda_context * bi_score
            scored.append((score, w))
        scored.sort(reverse=True)
        return [w for _, w in scored[:k]]
