from PyDictAPI import Finder, Translate

F = Finder()
T = Translate()

print(T.languages_help(pretty=True))
print(T.languages_help())
print(T.translateItems("help", "hi"))

print(F.findMeanings("help"))
print(F.findSynonyms("help"))
print(F.findAntonyms("help"))
print(F.findUsage("help"))