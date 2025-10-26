from collections import Counter
FREQS = {
    'A': 8.2, 
    'B': 1.5, 
    'C': 2.8, 
    'D': 4.3, 
    'E': 12.7,
    'F': 2.2, 
    'G': 2.0, 
    'H': 6.1, 
    'I': 7.0, 
    'J': 0.15,
    'K': 0.8, 
    'L': 4.0, 
    'M': 2.4, 
    'N': 6.7, 
    'O': 7.5,
    'P': 1.9, 
    'Q': 0.1, 
    'R': 6.0, 
    'S': 6.3, 
    'T': 9.1,
    'U': 2.8, 
    'V': 1.0, 
    'W': 2.4, 
    'X': 0.15, 
    'Y': 2.0, 
    'Z': 0.07
}
def IOC(text):
    filtered = [ch.upper() for ch in text if 'A' <= ch.upper() <= 'Z']
    N = len(filtered)
    if N < 2:
        return 0
    
    freqs = Counter(filtered)
    numerator = sum(f * (f - 1) for f in freqs.values())
    denominator = N * (N - 1)
    return numerator / denominator

def getSquared(text):
    text = [c for c in text.upper() if 'A' <= c <= 'Z']
    N = len(text)
    if N == 0:
        return float('inf')

    observed = Counter(text)
    chi = 0
    for letter in FREQS:
        observed_count = observed.get(letter, 0)
        expected = FREQS[letter] * N / 100
        chi += (observed_count - expected) ** 2 / expected

    return chi


def calcShift(group):
    shiftBest = 0
    scoreBest = float('inf')
    for shift in range(26):
        shifted = ''.join(chr((ord(c) - 65 - shift) % 26 + 65) for c in group)
        score = getSquared(shifted)

        if score < scoreBest:
            scoreBest = score
            shiftBest = shift

    return shiftBest

def vignere(text, minL=2, maxL=10):
    letters = [ch.upper() for ch in text if 'A' <= ch.upper() <= 'Z']
    best_ic, key_length = 0, 0


    for k in range(minL, maxL + 1):
        groups = ['' for _ in range(k)]
        for i, ch in enumerate(letters):
            groups[i % k] += ch

        IC_VALUE = [IOC(g) for g in groups if len(g) > 1]
        avg_ic = sum(IC_VALUE) / len(IC_VALUE)
        if avg_ic > best_ic:
            best_ic, key_length = avg_ic, k


    groups = ['' for _ in range(key_length)]
    for i, ch in enumerate(letters):
        groups[i % key_length] += ch

    key = ''.join(chr(calcShift(g) + 65) for g in groups)


    decrypted_text = []
    j = 0

    for char in text:
        if char.isupper():
            k = key[j % len(key)]
            Dchar = chr((ord(char) - ord(k) + 26) % 26 + ord('A'))
            decrypted_text.append(Dchar)
            j += 1
        elif char.islower():
            k = key[j % len(key)].lower()
            Dchar = chr((ord(char) - ord(k) + 26) % 26 + ord('a'))
            decrypted_text.append(Dchar)
            j += 1
        else:
            decrypted_text.append(char)

    return key_length, key, ''.join(decrypted_text)

