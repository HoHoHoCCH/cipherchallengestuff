import gzip
import json

def load_score(path="quadgrams.gz"):
    with gzip.open(path, "rt", encoding="utf8") as fh:
        data = json.load(fh)

    logp = data["logp"]
    floor = min(logp.values()) - 1

    def score(text: str) -> float:
        t = "".join(ch for ch in text.upper())
        if len(t) < 4:
            return float("-inf")
        s = 0
        get = logp.get
        for i in range(len(t) - 3):
            s += get(t[i:i+4], floor)
        return s

    def score_per_gram(text: str) -> float:
        raw = score(text)
        n = max(1, len("".join(ch for ch in text.upper())) - 3)
        return raw / n

    score.normalized = score_per_gram
    return score