import gzip
import json
import math
from typing import Dict


def _load_quadgrams(path: str) -> Dict[str, float]:
    with gzip.open(path, "rt", encoding="utf8") as fh:
        data = json.load(fh)
    return data["logp"]


def _load_bigrams(path: str) -> Dict[str, float]:
    with open(path, "r", encoding="utf8") as fh:
        pairs = json.load(fh)
    total = sum(c for _, c in pairs)

    return {bg.upper(): math.log10(c / total) for bg, c in pairs}


def load_score(qpath: str = "quadgrams.gz", bpath: str = "bigrams.json"):
    logp4 = _load_quadgrams(qpath)
    floor4 = min(logp4.values()) - 1


    try:
        logp2 = _load_bigrams(bpath)
        have_bi = True
        floor2 = min(logp2.values()) - 1
    except Exception:
        logp2, floor2, have_bi = {}, 0.0, False


    mono_freq = {
        'A': 0.08167, 'B': 0.01492, 'C': 0.02782, 'D': 0.04253, 'E': 0.12702,
        'F': 0.02228, 'G': 0.02015, 'H': 0.06094, 'I': 0.06966, 'J': 0.00153,
        'K': 0.00772, 'L': 0.04025, 'M': 0.02406, 'N': 0.06749, 'O': 0.07507,
        'P': 0.01929, 'Q': 0.00095, 'R': 0.05987, 'S': 0.06327, 'T': 0.09056,
        'U': 0.02758, 'V': 0.00978, 'W': 0.02360, 'X': 0.00150, 'Y': 0.01974,
        'Z': 0.00074,
    }
    logp1 = {k: math.log10(v) for k, v in mono_freq.items()}
    floor1 = min(logp1.values()) - 1

    def score(text: str) -> float:
        t = "".join(ch for ch in text.upper() if ch.isalpha())
        n = len(t)
        if n < 2:
            return float("-inf")

        s1 = 0.0
        get1 = logp1.get
        for ch in t:
            s1 += get1(ch, floor1)


        s2 = 0.0
        if have_bi and n >= 2:
            get2 = logp2.get
            for i in range(n - 1):
                s2 += get2(t[i : i + 2], floor2)


        s4 = float("-inf")
        if n >= 4:
            s4 = 0.0
            get4 = logp4.get
            for i in range(n - 3):
                s4 += get4(t[i : i + 4], floor4)


        if n < 4 or not math.isfinite(s4):

            if n < 30:
                w1 = 0.5
            elif n < 150:
                w1 = 0.5 - (n - 30) * (0.3 / 120)
            else:
                w1 = max(0.1, 0.2 - (n - 150) * (0.1 / 150))
            w2 = 1.0 - w1 if have_bi else 0.0
            return w1 * s1 + w2 * s2


        w1 = max(0.0, 0.3 - (n - 4) * (0.3 / 396))


        if n <= 300:
            w4 = 0.05 + (n - 4) * ((0.4 - 0.05) / (300 - 4)) 
        elif n <= 800:
            w4 = 0.4 + (n - 300) * ((0.75 - 0.4) / 500)
        elif n <= 1500:
            w4 = 0.75 + (n - 800) * ((0.9 - 0.75) / 700)
        else:
            w4 = 0.9
        w4 = max(0.0, min(0.95, w4))


        w2 = max(0.0, 1.0 - w1 - w4) if have_bi else 0.0
        return w1 * s1 + w2 * s2 + w4 * s4

    def score_per_gram(text: str) -> float:
        t = "".join(ch for ch in text.upper() if ch.isalpha())
        n = len(t)
        if n < 2:
            return float("-inf")


        s1 = 0.0
        get1 = logp1.get
        for ch in t:
            s1 += get1(ch, floor1)
        per1 = s1 / max(1, n)


        s2 = 0.0
        if have_bi and n >= 2:
            get2 = logp2.get
            for i in range(n - 1):
                s2 += get2(t[i : i + 2], floor2)
        per2 = s2 / max(1, n - 1)


        s4 = float("-inf")
        per4 = float("-inf")
        if n >= 4:
            s4 = 0.0
            get4 = logp4.get
            for i in range(n - 3):
                s4 += get4(t[i : i + 4], floor4)
            per4 = s4 / max(1, n - 3)

        if n < 4 or not math.isfinite(s4):
            if n < 30:
                w1 = 0.5
            elif n < 150:
                w1 = 0.5 - (n - 30) * (0.3 / 120)
            else:
                w1 = max(0.1, 0.2 - (n - 150) * (0.1 / 150))
            w2 = 1.0 - w1 if have_bi else 0.0
            return w1 * per1 + w2 * per2

        w1 = max(0.0, 0.3 - (n - 4) * (0.3 / 396))
        if n <= 300:
            w4 = 0.05 + (n - 4) * ((0.4 - 0.05) / (300 - 4))
        elif n <= 800:
            w4 = 0.4 + (n - 300) * ((0.75 - 0.4) / 500)
        elif n <= 1500:
            w4 = 0.75 + (n - 800) * ((0.9 - 0.75) / 700)
        else:
            w4 = 0.9
        w4 = max(0.0, min(0.95, w4))
        w2 = max(0.0, 1.0 - w1 - w4) if have_bi else 0.0
        return w1 * per1 + w2 * per2 + w4 * per4

    score.normalized = score_per_gram
    return score
