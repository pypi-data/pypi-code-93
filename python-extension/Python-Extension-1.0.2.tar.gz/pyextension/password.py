def replace1(original, dic):
    alphabet = '''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890~`!@#$%^&*()[]{}_-+=|:;"'<>,./? '''
    alphabet_dic = {}
    alphabet_num = 0
    text = []
    retext = []
    result = ''
    # Value
    try:
        for x in alphabet:
            if original.find(x) != -1:
                alphabet_dic[x] = dic[alphabet_num]
                alphabet_num += 1
    except IndexError:
        raise ValueError('The number of argument original\'s letters must as long as dic')
    # Match
    for x in range(0, len(original)):
        text.append(original[x])
    # Turn to List
    for x in text:
        for y in alphabet_dic:
            z = alphabet_dic[y]
            if x == y:
                retext.append(z)
                break
    # Create Password
    for x in retext:
        result += x
    # Turn to String
    result = result[::-1]
    # Turn Upside Down
    return result

def replace2(original, dic, key):
    alphabet = '''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890~`!@#$%^&*()[]{}_-+=|:;"'<>,./? '''
    alphabet_dic = {}
    alphabet_num = 0
    text = []
    retext = []
    result = ''
    # Value
    try:
        for x in alphabet:
            if original.find(x) != -1:
                y = (alphabet_num + key) % len(original)
                alphabet_dic[x] = dic[y]
                alphabet_num += 1
    except IndexError:
        raise ValueError('The number of argument original\'s letters must as long as dic')
    # Match
    for x in range(0, len(original)):
        text.append(original[x])
    # Turn to List
    for x in text:
        for y in alphabet_dic:
            z = alphabet_dic[y]
            if x == y:
                retext.append(z)
                break
    # Create Password
    for x in retext:
        result += x
    # Turn to String
    result = result[::-1]
    # Turn Upside Down
    return result

def replace3(original, dic, word_key):
    alphabet = '''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890~`!@#$%^&*()[]{}_-+=|:;"'<>,./? '''
    alphabet_dic = {}
    alphabet_num = 0
    alphabet_list = []
    key_index = 0
    key = []
    text = []
    retext = []
    result = ''
    # Value
    for x in word_key:
        key_number = alphabet.find(x)
        key.append(key_number)
    # Key
    try:
        for x in alphabet:
            if original.find(x) != -1:
                y = (alphabet_num + key[key_index]) % len(original)
                alphabet_dic[x] = dic[y]
                alphabet_num += 1
                key_index += 1
                key_index %= len(key) - 1
    except IndexError:
        raise ValueError('The number of argument original\'s letters must as long as dic')
    # Match
    for x in original:
        text.append(x)
    # Turn to List
    for x in text:
        for y in alphabet_dic:
            z = alphabet_dic[y]
            if x == y:
                retext.append(z)
                break
    # Create Password ( 2 )
    for x in retext:
        result += x
    # Turn to String
    result = result[::-1]
    # Turn Upside Down
    return result
