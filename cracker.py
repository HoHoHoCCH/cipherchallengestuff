# Okay, imports up top. Pulling in everything we'll need.
import itertools
import string
import re
from collections import Counter

from colorama import Fore, Style, init

from scorer import load_score
from NEWvignere import vignere


ALPH = string.ascii_lowercase
ETAOIN = "etaoinshrdlcumwfgypbvkjxqz"

def caesar_crack(ciphertext, scorer):
    best_guess = (-1e9, None, None)
    for shift in range(26):
        attempt = []
        for ch in ciphertext:
            if ch.isalpha():
                base = ord('A')
                shifted = (ord(ch.upper()) - base - shift) % 26
                attempt.append(chr(base + shifted))
            else:
                attempt.append(ch)
        decoded = ''.join(attempt)
        score = scorer(decoded)
        if score > best_guess[0]:
            best_guess = (score, shift, decoded)
    return best_guess


def crack_permutations(ciphertext, scorer, min_k=2, max_k=6, top_n=5):
    clean = ''.join(c for c in ciphertext.upper() if c.isalpha())
    if len(clean) < 4:
        return []

    results = []
    for k in range(min_k, max_k + 1):
        pad = (-len(clean)) % k
        padded = clean + ('X' * pad)
        chunks = [padded[i:i + k] for i in range(0, len(padded), k)]

        for perm in itertools.permutations(range(k)):
            reassembled = []
            for chunk in chunks:
                P = [''] * k
                for idx, ch in enumerate(chunk):
                    P[perm[idx]] = ch
                reassembled.append(''.join(P))
            candidate = ''.join(reassembled)
            if pad:
                candidate = candidate[:-pad]

            score = scorer(candidate)
            it = iter(candidate)
            display = ''.join(next(it) if ch.isalpha() else ch for ch in ciphertext)
            results.append((score, k, perm, display))


    results.sort(reverse=True, key=lambda x: x[0])
    seen, final = set(), []
    for score, k, perm, disp in results:
        key = ''.join(c for c in disp.upper() if c.isalpha())
        if key in seen:
            continue
        seen.add(key)
        final.append((score, k, perm, disp))
        if len(final) >= top_n:
            break
    return final


def multiLineInput():
    all_lines = []
    print("type p n enter to finish input")
    while True:
        line = input()
        if line.strip().lower() == 'p':
            break
        all_lines.append(line)
    return "\n".join(all_lines)


def initial_key(ciphertext):

    only_letters = [ch.lower() for ch in ciphertext if ch.isalpha()]
    freq = Counter(only_letters)
    ranked = ''.join(c for c, _ in freq.most_common())


    for ch in ALPH:
        if ch not in ranked:
            ranked += ch

    guess_map = {c: ETAOIN[i] for i, c in enumerate(ranked)}
    return guess_map


def decrypt(text, c2p):
    result = []
    for ch in text:
        if ch.isalpha():
            lo = ch.lower()
            mapped = c2p.get(lo, lo)
            result.append(mapped.upper() if ch.isupper() else mapped)
        else:
            result.append(ch)
    return ''.join(result)


def improve_key(ciphertext, key_map, scorer, max_passes=5):
    pairs = list(itertools.combinations(ALPH, 2))
    current_plain = decrypt(ciphertext, key_map)
    best_score = scorer.normalized(current_plain)

    for _ in range(max_passes):
        updated = False
        for a, b in pairs:
            if a not in key_map or b not in key_map:
                continue
            pa, pb = key_map[a], key_map[b]
            if pa == pb:
                continue

            key_map[a], key_map[b] = pb, pa
            candidate = decrypt(ciphertext, key_map)
            candidate_score = scorer.normalized(candidate)

            if candidate_score > best_score:
                best_score = candidate_score
                current_plain = candidate
                updated = True
            else:
                key_map[a], key_map[b] = pa, pb
        if not updated:
            break
    return key_map, current_plain, best_score


def crack_monoalpha(ciphertext, scorer):
    rough_key = initial_key(ciphertext)
    improved_key, decrypted, _ = improve_key(ciphertext, rough_key, scorer)
    key_string = ''.join(improved_key.get(c, c) for c in ALPH)
    return decrypted, key_string



if __name__ == "__main__":
    init(autoreset=True)

    scorer = load_score()

    print(Fore.CYAN + "ADD CIPHERTEXT:")
    cipher = multiLineInput().strip()

    print(Fore.YELLOW + "\n-----Caesar Cipher-----" + Style.RESET_ALL)
    score, shift, plain = caesar_crack(cipher, scorer)
    print(f"{Fore.GREEN}shift:{Style.RESET_ALL} {shift}")
    print(f"{Fore.GREEN}score:{Style.RESET_ALL} {score:.2f}")
    print(f"{Fore.GREEN}decrypted:{Style.RESET_ALL}\n{plain}\n")

    print(Fore.YELLOW + "-----Permutation Cipher-----" + Style.RESET_ALL)
    permutation_results = crack_permutations(cipher, scorer, min_k=6, max_k=6, top_n=1)
    if not permutation_results:
        print(Fore.RED + "no permutation candidates found\n")
    else:
        score, klen, perm, pt = permutation_results[0]
        print(f"{Fore.GREEN}score:{Style.RESET_ALL} {score:.2f}")
        print(f"{Fore.GREEN}key len:{Style.RESET_ALL} {klen}")
        print(f"{Fore.GREEN}key:{Style.RESET_ALL} {tuple(x+1 for x in perm)}")
        print(f"{Fore.GREEN}decrypted:{Style.RESET_ALL}\n{pt}\n")

    print(Fore.YELLOW + "-----Monoalphabetic Cipher-----" + Style.RESET_ALL)
    plain_text, key_map = crack_monoalpha(cipher, scorer)
    print(f"{Fore.GREEN}decrypted:{Style.RESET_ALL}\n{plain_text}\n")
    print(f"{Fore.GREEN}key alphabet:{Style.RESET_ALL}\n{key_map}\n")

    print(Fore.YELLOW + "-----Vigenere Cipher-----" + Style.RESET_ALL)
    klen, key, text = vignere(cipher, 2, 12)
    print(f"{Fore.GREEN}key length:{Style.RESET_ALL} {klen}")
    print(f"{Fore.GREEN}key:{Style.RESET_ALL} {key}")
    print(f"{Fore.GREEN}decrypted:{Style.RESET_ALL} {text}")

    print(Fore.CYAN + "attempts finished" + Style.RESET_ALL)