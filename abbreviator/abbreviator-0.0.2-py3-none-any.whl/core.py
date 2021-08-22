import pyphen

dic_nl = pyphen.Pyphen(lang='nl_NL')
dic_de = pyphen.Pyphen(lang='de_DE')
dic_en = pyphen.Pyphen(lang='en_GB')

pyphen_dict = {'nl' : dic_nl, 'de' : dic_de, 'en' : dic_en}

def shortener_v1( long_word, language='en'):
    """
        Basic shortener; 
            - Keeps the first syllable intact
            - For remaining syllable: only add 1st letter
    """
    global pyphen_dict

    dic = pyphen_dict[language]
    
    long_word = long_word.replace('-','')

    hyphened = dic.inserted(long_word)
    word_list = hyphened.split('-')
    
    short = word_list[0] + "".join([ w[0] for w in word_list[1:]])
    short = short.upper()
    
    return short


def shortener_v3( long_word, maximum_first_syllable=4, language='en'):
    """
        - First Syllable: Maximum length maximum_first_syllable
        - First Syllable: Takes last character of first_syllable
        - Remaining Syllable: Only use first character
        - Add last character from last syllable
    """
    global pyphen_dict

    dic = pyphen_dict[language]
    
    long_word = long_word.replace('-','')

    hyphened = dic.inserted(long_word)
    word_list = hyphened.split('-')
    
    first_syllable = word_list[0][:maximum_first_syllable - 1]
    
    if len(word_list[0]) >= maximum_first_syllable:
        first_syllable += word_list[0][-1]
    
    short = first_syllable + "".join([ w[0] for w in word_list[1:]])
    
    if word_list[1:]:
        short += word_list[-1][-1]
    
    short = short.upper()
    
    return short

def abbreviate_or_keep( word, language='en'):
    """
        helper function
    """
    if any(i.isdigit() for i in word):
        return word.upper()
    else:
        return shortener_v3(word, language=language)


def sentence_shortener( long_sentence, language='en'):
    """
        Example Input

        SuperDuperLaser MegaDestroyer p1200

        - If contains number, keep
        - if not, shorten
    """

    word_list = long_sentence.split(" ")

    shorted_word_list = [ abbreviate_or_keep(w, language=language) for w in word_list ]

    return " ".join(shorted_word_list)