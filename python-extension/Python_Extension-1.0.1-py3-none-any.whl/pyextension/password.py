def replace1(word, dic):
    text = []
    retext = []
    result = ''
    # Value
    for x in range(0, len(word)):
        text.append(word[x])
    # Turn to List
    for x in range(0, len(text)):
        for y in range(0, len(dic)):
            z = y + key
            if z > len(dic) - 1:
                z = z - len(dic) + 1
            if text[x] == dic[z]:
                retext.append(dic[z])
                break
    # Create Password
    for x in retext:
        result += x
    # Turn to String
    return result

def replace2(word, dic):
    text = []
    retext = []
    result = ''
    # Value
    word = word[::-1]
    # Turn Upside Down
    for x in range(0, len(word)):
        text.append(word[x])
    # Turn to List
    for x in range(0, len(text)):
        for y in dic:
            if text[x] == y:
                retext.append(dic[y])
                break
    # Create Password
    for x in retext:
        result += x
    # Turn to String
    return result

def replace3(word, dic, key):
    text = []
    retext = []
    result = ''
    # Value
    word = word[::-1]
    # Turn Upside Down
    for x in range(0, len(word)):
        text.append(word[x])
    # Turn to List
    for x in range(0, len(text)):
        for y in range(0, len(dic)):
            z = y + key
            if z > len(dic) - 1:
                z = z - len(dic) + 1
            if text[x] == dic[z]:
                retext.append(dic[z])
                break
    # Create Password
    for x in retext:
        result += x
    # Turn to String
    return result

def replace4(word, dic, key, word_key):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    list_of_numbers = []
    key_index = 0
    str_text = ''
    # ( Create Password ( 1 ) )
    text = []
    retext = []
    result = ''
    # Value
    word = word[::-1]
    # Turn Upside Down
    for x in word_key:
        key_number = alphabet.find(x)
        list_of_numbers.append(key_number)
    for x in word:
        num = alphabet.find(x)
        if num == -1:
            str_text = str_text + ''
        else:
            new_num = num + list_of_numbers[key_index]
            new_num %= 26
            str_text
            str_text += alphabet[new_num]
        if key_index < len(list_of_numbers) - 1:
            key_index += 1
        else:
            key_index = 0
    # Create Password ( 1 )
    for x in range(0, len(word)):
        text.append(word[x])
    # Turn to List
    for x in range(0, len(text)):
        for y in range(0, len(dic)):
            z = y + key
            while z > len(dic) - 1:
                z = z - len(dic) + 1
            if text[x] == dic[z]:
                retext.append(dic[z])
                break
    # Create Password ( 2 )
    for x in retext:
        result += x
    # Turn to String
    return result
