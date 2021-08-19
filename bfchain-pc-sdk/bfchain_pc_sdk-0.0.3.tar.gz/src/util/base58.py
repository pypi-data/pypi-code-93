ALPHABET = bytearray("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
BASE_58 = len(ALPHABET)
BASE_256 = 256
INDEXES = [-1] * 128
for i in range(len(ALPHABET)):
    INDEXES[ALPHABET[i]] = i


def encode(input_bytes):
    if len(input_bytes) == 0:
        return ""
    input_bytes = input_bytes[0:len(input_bytes)]
    zeroCount = 0
    while zeroCount < len(input_bytes) and input_bytes[zeroCount] == 0:
        zeroCount = zeroCount + 1
    temp = [0] * (len(input_bytes) * 2)
    j = len(temp)
    startAt = zeroCount
    while startAt < len(input_bytes):
        mod = divmod58(input_bytes, startAt)
        if input_bytes[startAt] == 0:
            startAt = startAt + 1
        j = j - 1
        temp[j] = ALPHABET[mod]
    while j < len(temp) and temp[j] == ALPHABET[0]:
        j = j + 1
    while zeroCount >= 0:
        zeroCount = zeroCount - 1
        j = j - 1
        temp[j] = ALPHABET[0]
    output = temp[j + 1:len(temp)]
    return bytearray(output)


def divmod58(number, startAt):
    remainder = 0
    for i in range(startAt, len(number)):
        digit256 = number[i] & 0xFF
        temp = remainder * BASE_256 + digit256
        number[i] = temp / BASE_58
        remainder = temp % BASE_58
    return remainder
