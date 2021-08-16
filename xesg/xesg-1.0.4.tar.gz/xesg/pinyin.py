def pinyin1(word):
    import pypinyin
    if len(str(word))==1:
        return pypinyin.pinyin(word)[0][0]
    else:
        return None
def pinyin2(word):
    import pypinyin
    py=[]
    for i in word:
        py.append(pypinyin.pinyin(i)[0][0])
    return py
def pinyin3(word):
    import pypinyin
    py=[]
    for i in word:
        py.append(pypinyin.pinyin(i)[0][0])
    return " ".join(py)
