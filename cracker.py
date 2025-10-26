import itertools
import string
import re
from collections import Counter
import heapq
import time
import os

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


def crack_columnar_transposition(ciphertext, scorer, min_k=2, max_k=6, top_n=3):

    clean = ''.join(c for c in ciphertext.upper() if c.isalpha())
    if len(clean) < 4:
        return []

    results = []
    for k in range(min_k, max_k + 1):
        n = len(clean)
        q, r = divmod(n, k) 


        for perm in itertools.permutations(range(k)):
            chunk_lens = [(q + 1) if col < r else q for col in perm]


            idx = 0
            chunks = []
            valid = True
            for L in chunk_lens:
                if idx + L > n:
                    valid = False
                    break
                chunks.append(list(clean[idx: idx + L]))
                idx += L
            if not valid or idx != n:
                continue


            columns = [None] * k
            for pos, col in enumerate(perm):
                columns[col] = chunks[pos]

            reconstructed = []
            max_h = q + 1 
            for row in range(max_h):
                for c in range(k):
                    col = columns[c]
                    if row < len(col):
                        reconstructed.append(col[row])

            candidate = ''.join(reconstructed)
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


def railfenceDecrypt(ciphertext: str, search_area: int = 100, start_key: int = 2):
    stext = ciphertext
    n = len(stext)
    if n == 0:
        return stext

    max_rails = min(start_key + search_area - 1, max(2, min(12, n // 2)))

    best = -1e19
    best_candidate = stext

    for rails in range(max(2, start_key), max_rails + 1):
        pattern = [0] * n
        r, d = 0, 1
        for i in range(n):
            pattern[i] = r
            r += d
            if r == 0 or r == rails - 1:
                d *= -1

        counts = [0] * rails
        for ridx in pattern:
            counts[ridx] += 1

        rails_str = [None] * rails
        idx = 0
        for ri in range(rails):
            c = counts[ri]
            rails_str[ri] = stext[idx: idx + c]
            idx += c

        ptr = [0] * rails
        out_chars = []
        for ridx in pattern:
            s = rails_str[ridx]
            out_chars.append(s[ptr[ridx]])
            ptr[ridx] += 1
        candidate = ''.join(out_chars)

        letters_only = ''.join(ch for ch in candidate.upper() if ch.isalpha())
        s = scorer(letters_only)
        if s > best:
            best = s
            best_candidate = candidate

    return best_candidate


def hill2x2(ciphertext: str, scorer, sample_letters: int = 60, refine_top: int = 3):
    letters = [ch.upper() for ch in ciphertext if ch.isalpha()]
    if len(letters) < 2:
        return ciphertext, None
    L = ''.join(letters)


    def to_pairs_num(s: str):
        n = len(s) - (len(s) % 2)
        nums = [ord(c) - 65 for c in s[:n]]
        return list(zip(nums[0::2], nums[1::2]))

    sample_len = min(len(L) - (len(L) % 2), max(2, sample_letters - (sample_letters % 2)))
    sample_pairs = to_pairs_num(L[:sample_len])
    full_pairs = to_pairs_num(L)


    inv26 = [0] * 26
    for a in range(26):

        if (a & 1) and (a % 13 != 0):
 
            for x in range(1, 26):
                if (a * x) % 26 == 1:
                    inv26[a] = x
                    break
        else:
            inv26[a] = 0

    top = []
    push, pop = heapq.heappush, heapq.heappop


    for a in range(26):
        for b in range(26):
            for c in range(26):
                for d in range(26):
                    det = (a * d - b * c) % 26
                    inv_det = inv26[det]
                    if inv_det == 0:
                        continue
                    ia = (inv_det * d) % 26
                    ib = (inv_det * (-b)) % 26
                    ic = (inv_det * (-c)) % 26
                    id_ = (inv_det * a) % 26


                    out = []
                    for x, y in sample_pairs:
                        out.append(chr(65 + ((ia * x + ib * y) % 26)))
                        out.append(chr(65 + ((ic * x + id_ * y) % 26)))
                    s = scorer(''.join(out))
                    if len(top) < refine_top:
                        push(top, (s, (ia, ib, ic, id_)))
                    elif s > top[0][0]:
                        pop(top)
                        push(top, (s, (ia, ib, ic, id_)))


    best_s, best_plain, best_key = -1e19, None, None
    for s0, (ia, ib, ic, id_) in sorted(top, reverse=True):
        out = []
        for x, y in full_pairs:
            out.append(chr(65 + ((ia * x + ib * y) % 26)))
            out.append(chr(65 + ((ic * x + id_ * y) % 26)))
        cand = ''.join(out)[:len(L)]
        sfull = scorer(cand)
        if sfull > best_s:
            best_s, best_plain, best_key = sfull, cand, (ia, ib, ic, id_)

    if best_plain is None:
        return ciphertext, None


    it = iter(best_plain)
    out = []
    for ch in ciphertext:
        if ch.isalpha():
            p = next(it)
            out.append(p.lower() if ch.islower() else p)
        else:
            out.append(ch)
    return ''.join(out), best_key

if __name__ == "__main__":
    init(autoreset=True)
    scorer = load_score()
    overall_start = time.perf_counter()
    times = {}
    print(Fore.CYAN + "ADD CIPHERTEXT:")
    cipher = multiLineInput().strip()


    run = {
        'CAESAR': os.environ.get('RUN_CAESAR', '1') == '1',
        'BLOCK': os.environ.get('RUN_BLOCK', '1') == '1',
        'COLUMNAR': os.environ.get('RUN_COLUMNAR', '1') == '1',
        'MONO': os.environ.get('RUN_MONO', '1') == '1',
        'VIG': os.environ.get('RUN_VIG', '1') == '1',
        'HILL': os.environ.get('RUN_HILL', '1') == '1',
        'RAIL': os.environ.get('RUN_RAIL', '1') == '1',
    }
    if run['CAESAR']:
        t0 = time.perf_counter()
        print(Fore.YELLOW + "\n-----Caesar Cipher-----" + Style.RESET_ALL)
        score, shift, plain = caesar_crack(cipher, scorer)
        print(f"{Fore.GREEN}shift:{Style.RESET_ALL} {shift}")
        print(f"{Fore.GREEN}score:{Style.RESET_ALL} {score:.2f}")
        print(f"{Fore.GREEN}decrypted:{Style.RESET_ALL}\n{plain}\n")
        times['caesar'] = time.perf_counter() - t0
        print(f"{Fore.CYAN}time:{Style.RESET_ALL} {times['caesar']:.2f}s\n")

    if run['BLOCK']:
        t0 = time.perf_counter()
        print(Fore.YELLOW + "-----Block Transposition-----" + Style.RESET_ALL)
        permutation_results = crack_permutations(cipher, scorer, min_k=6, max_k=6, top_n=1)
        if not permutation_results:
            print(Fore.RED + "no permutation candidates found\n")
        else:
            score, klen, perm, pt = permutation_results[0]
            print(f"{Fore.GREEN}score:{Style.RESET_ALL} {score:.2f}")
            print(f"{Fore.GREEN}key len:{Style.RESET_ALL} {klen}")
            print(f"{Fore.GREEN}key:{Style.RESET_ALL} {tuple(x+1 for x in perm)}")
            print(f"{Fore.GREEN}decrypted:{Style.RESET_ALL}\n{pt}\n")
        times['block transposition'] = time.perf_counter() - t0
        print(f"{Fore.CYAN}time:{Style.RESET_ALL} {times['block transposition']:.2f}s\n")

    if run['COLUMNAR']:
        t0 = time.perf_counter()
        print(Fore.YELLOW + "-----Columnar Transposition-----" + Style.RESET_ALL)
        col_results = crack_columnar_transposition(cipher, scorer, min_k=2, max_k=7, top_n=1)
        if not col_results:
            print(Fore.RED + "no columnar candidates found\n")
        else:
            score, klen, perm, pt = col_results[0]
            print(f"{Fore.GREEN}score:{Style.RESET_ALL} {score:.2f}")
            print(f"{Fore.GREEN}columns:{Style.RESET_ALL} {klen}")
            print(f"{Fore.GREEN}key:{Style.RESET_ALL} {tuple(x+1 for x in perm)}")
            print(f"{Fore.GREEN}decrypted:{Style.RESET_ALL}\n{pt}\n")
        times['column transposition'] = time.perf_counter() - t0
        print(f"{Fore.CYAN}time:{Style.RESET_ALL} {times['column transposition']:.2f}s\n")

    if run['MONO']:
        t0 = time.perf_counter()
        print(Fore.YELLOW + "-----Monoalphabetic Cipher-----" + Style.RESET_ALL)
        plain_text, key_map = crack_monoalpha(cipher, scorer)
        print(f"{Fore.GREEN}decrypted:{Style.RESET_ALL}\n{plain_text}\n")
        print(f"{Fore.GREEN}key alphabet:{Style.RESET_ALL}\n{key_map}\n")
        times['monoalphabetic'] = time.perf_counter() - t0
        print(f"{Fore.CYAN}time:{Style.RESET_ALL} {times['monoalphabetic']:.2f}s\n")

    if run['VIG']:
        t0 = time.perf_counter()
        print(Fore.YELLOW + "-----Vigenere Cipher-----" + Style.RESET_ALL)
        klen, key, text = vignere(cipher, 2, 12)
        print(f"{Fore.GREEN}key length:{Style.RESET_ALL} {klen}")
        print(f"{Fore.GREEN}key:{Style.RESET_ALL} {key}")
        print(f"{Fore.GREEN}decrypted:{Style.RESET_ALL} {text}")
        times['vigenere'] = time.perf_counter() - t0
        print(f"{Fore.CYAN}time:{Style.RESET_ALL} {times['vigenere']:.2f}s\n")

    if run['HILL']:
        t0 = time.perf_counter()
        print(Fore.YELLOW + "-----Hill 2x2 ONLY-----" + Style.RESET_ALL)
        hill_text, hill_key = hill2x2(cipher, scorer, sample_letters=80, refine_top=5)
        if hill_key is None:
            print(Fore.RED + "no hill candidates found\n")
        else:
            print(f"{Fore.GREEN}key:{Style.RESET_ALL} {hill_key}")
            print(f"{Fore.GREEN}decrypted:{Style.RESET_ALL}\n{hill_text}\n")
        times['2x2 hill'] = time.perf_counter() - t0
        print(f"{Fore.CYAN}time:{Style.RESET_ALL} {times['2x2 hill']:.2f}s\n")

    if run['RAIL']:
        t0 = time.perf_counter()
        print(Fore.YELLOW + "-----Railfence Cipher-----" + Style.RESET_ALL)
        rf = railfenceDecrypt(cipher)
        print(rf)
        times['railfence'] = time.perf_counter() - t0
        print(f"{Fore.CYAN}time:{Style.RESET_ALL} {times['railfence']:.2f}s\n")

    total = time.perf_counter() - overall_start
    print(Fore.CYAN + "attempts finished" + Style.RESET_ALL)
    print(Fore.YELLOW + "\n-----times-----" + Style.RESET_ALL)
    for name, secs in times.items():
        print(f"{Fore.GREEN}{name}:{Style.RESET_ALL} {secs:.2f}s")
    print(f"{Fore.GREEN}Total:{Style.RESET_ALL} {total:.2f}s")
