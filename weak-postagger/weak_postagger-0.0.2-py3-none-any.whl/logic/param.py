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
