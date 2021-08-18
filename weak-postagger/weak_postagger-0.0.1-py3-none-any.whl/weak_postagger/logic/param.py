CLASS_TO_POS_TAG = {'verbos': 'VERB',
                    'adjetivos': 'ADJ',
                    'adverbios': 'ADV',
                    'artigos': 'ART',
                    'conjuncoes': 'CONJ',
                    'interjeicoes': 'INT',
                    'substantivos': 'SUBS',
                    'pronomes': 'PRON',
                    'numeros': 'NUM',
                    'preposicoes': 'PREP',
                    'participios': 'PART'}

PUNCTUATION = ['.', ',', ';', ':', '/', '!', '?']
SYMBOLS = ['"', '@', '#', '$', '%', '¨', '&', '*', '(', ')', '_', '-', '+', '=', '§', '{', '[', ']', '}']

SUBSTANTIVE_PLACEHOLDERS = ['EMAIL', 'MONEY', 'URL', 'MEASURE', 'CODE', '']
NUMERIC_PLACEHOLDERS = ['DATE', 'TIME', 'DDD', 'PHONE', 'CPF', 'CNPJ', 'NUMBER']
OOV_TOKEN = ['ABSTAIN']

FILE_NAME_DIVIDERS = ['.', '_']

SET_WORDS = {
    'que': ['CONJ'],
    'se': ['CONJ'],
    'mesmo': ['ADV'],
    'ainda': ['ADV'],
    'centenário': ['SUBS'],
    'pares': ['SUBS'],
    'vocês': ['PRON'],
}

PREPOSITION_ARTICLES = ['no', 'na', 'do', 'das', 'nas']

OBLIQUE_PERSONAL_PRONOUN = ['eu', 'tu', 'ele', 'ela', 'nos',
                            'vos', 'eles', 'elas', 'você',
                            'vocês', 'me', 'te']

VERB_EXCEPTIONS = ['ganho', 'gasto', 'pago', 'dito', 'escrito',
                   'feito', 'visto', 'posto', 'aberto', 'coberto']

ADDRESS = ['rua', 'av', 'bloco', 'apt', 'r', 'avenida']
