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

