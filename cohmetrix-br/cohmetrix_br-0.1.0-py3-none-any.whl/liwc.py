import string
from nltk.tokenize import word_tokenize


# -----------------------------READ LIWC---------------------------------------------------#
# method for read the liwc after create the liwc.csv file
def reading_liwc():
    base = open('liwc.csv', 'r', encoding='utf-8', errors='ignore').read().split('\n')
    dataLiwc = []

    for lineBase in base:
        wordsBase = lineBase.split(',')
        if wordsBase:
            dataLiwc.append(wordsBase)

    return dataLiwc


# --------------------------------------------------------------------------------#

def search(lista, valor):
    return [lista.index(x) for x in lista if valor in x]


# -----------------------------FEATURES LIWC---------------------------------------------------#
def liwc_features(text):

    # reading liwc
    wn = open('../resources/LIWC2007_Portugues_win.dic.txt', 'r', encoding='utf-8', errors='ignore').read().split('\n')
    wordSetLiwc = []
    for line in wn:
        words = line.split('\t')
        if words:
            wordSetLiwc.append(words)
    # indexes of liwc
    indices = open('../resources/indices.txt', 'r', encoding='utf-8', errors='ignore').read().split('\n')

    # dataset tokenization
    wordsDataSet = []

    wordsLine = []
    for word in word_tokenize(str(text)):  # o texto tá na 2º coluna do csv, por isso pego vector[1]
        if word not in string.punctuation + "\..." and word != '``' and word != '"':
            wordsLine.append(word)
    wordsDataSet.append(wordsLine)

    # initializing liwc with zero
    liwc = []

    for j in range(1):
        liwc.append([0] * len(indices))

    # performing couting
    # print("writing liwc ")

    for k in range(len(wordsDataSet)):
        for word in wordsDataSet[k]:
            position = search(wordSetLiwc, word)
            if position:
                tam = len(wordSetLiwc[position[0]])
                for i in range(tam):
                    if wordSetLiwc[position[0]][i] in indices:
                        positionIndices = search(indices, wordSetLiwc[position[0]][i])
                        liwc[k][positionIndices[0]] = liwc[k][positionIndices[0]] + 1

    # saving the liwc file
    output = []

    for i in range(len(liwc)):
        for j in range(len(liwc[i])):
            output.append(liwc[i][j])
    return output
# --------------------------------------------------------------------------------#

# text = "G1 é um portal de notícias brasileiro mantido pelo Grupo Globo e sob orientação da Central Globo de
# Jornalismo. Foi lançado em 18 de setembro de 2006, ano que a Rede Globo fez 41 anos."

# print(liwcFeatures(text))
