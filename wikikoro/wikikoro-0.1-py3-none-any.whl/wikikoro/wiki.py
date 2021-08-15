import wikipedia
import warnings
warnings.filterwarnings(action= 'ignore')

def find(txt):
    '''Give any strng value.It will return the Wikipedia Search Result'''
    while True:
        try:
            result = wikipedia.summary(txt, sentences=10)

            r = result.split('.')
            for i in r:
                print(i)
            break
        except:
            print("Not Found in Wikipedia")
            break