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
