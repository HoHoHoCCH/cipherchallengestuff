def ceaser(message, key):
    alf = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    liMessage = list(message.lower())
    decMessage = []
    if key >= 0:
        key = key * -1
    else:
        key = (26 + key) * -1
    for i in range(len(liMessage)):
        if liMessage[i] != " ":
            decMessage.append(alf[alf.index(liMessage[i])+key])
        else:
            decMessage.append(" ")
    return "".join(decMessage)

def mono(message, key):
    alf = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    message = list(message.lower())
    key = list(key)
    decMessage = []
    for i in range(len(message)):
        if message[i] != " ":
            decMessage.append(key[alf.index(message[i])])
        else:
            decMessage.append(" ")
    return "".join(decMessage)

def transposition_block(message, key):
    text = ''.join(c for c in message.upper() if c.isalpha())
    k = len(key)
    ciphertext = []

    for start in range(0, len(text), k):
        block = text[start:start + k]
        m = len(block)
        ct_block = [''] * m
        for i, v in enumerate(key):
            if i < m and v <= m:
                ct_block[v - 1] = block[i]
        ciphertext.append(''.join(ct_block))

    return ''.join(ciphertext)

def playfair_decrypt(ciphertext, key):
    key = "".join(ch for ch in key.upper() if ch.isalpha()).replace("J", "I")
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    seen = set()
    square = [c for c in key + alphabet if not (c in seen or seen.add(c))]

    def pos(ch):
        i = square.index(ch)
        return divmod(i, 5)

    text = "".join(ch for ch in ciphertext.upper() if ch.isalpha())
    raw = []

    for i in range(0, len(text), 2):
        a, b = text[i], text[i + 1]
        ra, ca = pos(a)
        rb, cb = pos(b)

        if ra == rb:
            raw.append(square[ra * 5 + (ca - 1) % 5])
            raw.append(square[rb * 5 + (cb - 1) % 5])
        elif ca == cb:
            raw.append(square[((ra - 1) % 5) * 5 + ca])
            raw.append(square[((rb - 1) % 5) * 5 + cb])
        else:
            raw.append(square[ra * 5 + cb])
            raw.append(square[rb * 5 + ca])

    clean = []
    for i, ch in enumerate(raw):
        if i > 0 and i < len(raw) - 1:
            if raw[i] in {"X", "O"} and raw[i - 1] == raw[i + 1]:
                continue
        clean.append(ch)
    if clean and clean[-1] in {"X", "O"}:
        clean.pop()

    return "".join(clean)


def polybius_decrypt(message, keyword):
    keyword = "".join(ch for ch in keyword.upper() if ch.isalpha()).replace("J", "I")
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    seen = set()
    table = [c for c in keyword + alphabet if not (c in seen or seen.add(c))]

    message = "".join(ch for ch in message if ch.isdigit())
    plaintext = []

    for i in range(0, len(message), 2):
        row = int(message[i]) - 1
        col = int(message[i + 1]) - 1
        plaintext.append(table[row * 5 + col])

    return "".join(plaintext)


def playfair(ciphertext, key):
    return playfair_decrypt(ciphertext, key)


def polybius(message, keyword):

    return polybius_decrypt(message, keyword)


def columnar_manual(ciphertext, key_digits):
    text = ''.join(c for c in ciphertext.upper() if c.isalpha())
    if not key_digits:
        return ''
    k = len(key_digits)


    try:
        perm = [int(x) - 1 for x in key_digits]
    except Exception:
        return ''
    if sorted(perm) != list(range(k)):
        return ''

    n = len(text)
    if k <= 0 or n == 0:
        return ''

    q, r = divmod(n, k)


    chunk_lens = [(q + 1) if col < r else q for col in perm]


    idx = 0
    chunks = []
    for L in chunk_lens:
        chunks.append(list(text[idx: idx + L]))
        idx += L


    columns = [None] * k
    for pos, col in enumerate(perm):
        columns[col] = chunks[pos]


    out = []
    max_h = q + 1
    for row in range(max_h):
        for c in range(k):
            col = columns[c]
            if row < len(col):
                out.append(col[row])

    return ''.join(out)


def railfence_manual(ciphertext, rails, offset=0):
    text = ''.join(c for c in ciphertext.upper() if c.isalpha())
    n = len(text)
    if rails is None or rails < 2 or n == 0:
        return text

    pattern = []
    r, d = 0, 1
    for _ in range(n):
        pattern.append(r)
        r += d
        if r == 0 or r == rails - 1:
            d *= -1


    period = max(1, 2 * (rails - 1))
    off = int(offset or 0) % period
    if off:
        rotated = pattern[off:] + pattern[:off]
    else:
        rotated = pattern


    counts = [rotated.count(i) for i in range(rails)]
    rails_data = []
    idx = 0
    for c in counts:
        rails_data.append(list(text[idx: idx + c]))
        idx += c


    out = []
    for rail_idx in rotated:
        out.append(rails_data[rail_idx].pop(0))

    return ''.join(out)


def vigenere_manual(text, key):

    if not key:
        return text
    key_shifts = [ord(c.upper()) - ord('A') for c in key if c.isalpha()]
    if not key_shifts:
        return text

    out = []
    j = 0
    L = len(key_shifts)
    for ch in text:
        if ch.isalpha():
            k = key_shifts[j % L]
            if ch.isupper():
                base = ord('A')
                out.append(chr((ord(ch) - base - k) % 26 + base))
            else:
                base = ord('a')
                out.append(chr((ord(ch) - base - k) % 26 + base))
            j += 1
        else:
            out.append(ch)
    return ''.join(out)

def hill2_manual(text, key_digits):
    if not key_digits or len(key_digits) != 4:
        return ''
    try:
        a, b, c, d = [int(x) % 26 for x in key_digits]
    except Exception:
        return ''

    det = (a * d - b * c) % 26
    inv_det = None
    if det % 2 == 1 and det % 13 != 0:
        for x in range(1, 26):
            if (det * x) % 26 == 1:
                inv_det = x
                break
    if inv_det is None:
        return 'invalid key'

    ia = (inv_det * d) % 26
    ib = (inv_det * (-b)) % 26
    ic = (inv_det * (-c)) % 26
    id_ = (inv_det * a) % 26

    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return text
    upper = ''.join(ch.upper() for ch in letters)
    if len(upper) % 2 == 1:
        upper += 'X'

    nums = [ord(ch) - 65 for ch in upper]
    out_chars = []
    for i in range(0, len(nums), 2):
        x, y = nums[i], nums[i + 1]
        p0 = (ia * x + ib * y) % 26
        p1 = (ic * x + id_ * y) % 26
        out_chars.append(chr(65 + p0))
        out_chars.append(chr(65 + p1))


    plain_letters = ''.join(out_chars)[:len(letters)]


    it = iter(plain_letters)
    out = []
    for ch in text:
        if ch.isalpha():
            p = next(it)
            out.append(p.lower() if ch.islower() else p)
        else:
            out.append(ch)
    return ''.join(out)
