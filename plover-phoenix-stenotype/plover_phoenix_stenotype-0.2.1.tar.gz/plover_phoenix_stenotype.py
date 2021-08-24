from plover.system.english_stenotype import *

ORTHOGRAPHY_RULES = [
    # dropping silent e before endings
    (r'^(.+[bcdfghjklmnpqrstuvz])e \^ (able|age|ed|est|ing|ings|ion|ory|ous)$', r'\1\2'),

    # dropping e after double vowels
    (r'^(.+[ie])e \^ (e.+)$', r'\1\2'),

    # consonant + y pluralization
    (r'^(.+[bcdfghjklmnpqrstvwxz])y \^ s$', r'\1ies'),

    # consonant doubling
    (r'^(.*(?:[bcdfghjklmnprstvwxyz]|qu)[aeiou])([bcdfgklmnprtvz]) \^ ((ee|[eo]i)(?:[bcdfghjklmnpqrstvwxyz].?)?)$', r'\1\2\2\3'),
    (r'^(.*(?:[bcdfghjklmnprstvwxyz]|qu)[aeiou])([bcdfgklmnprtvz]) \^ (([aeiouy]|[ai]e)(?:[bcdfghjklmnpqrstvwxyz].?))$', r'\1\2\2\3'),
    (r'^(.*(?:[bcdfghjklmnprstvwxyz]|qu)[aeiou])([bcdfgklmnprtvz]) \^ ([ei]?ous)$', r'\1\2\2\3'),
    (r'^(.*(?:[bcdfghjklmnprstvwxyz]|qu)[aeiou])([bcdfgklmnprtvz]) \^ ([ai]ble)$', r'\1\2\2\3'),
    (r'^(.*(?:[bcdfghjklmnprstvwxyz]|qu)[aeiou])([bcdfgklmnprtvz]) \^ ([ae]nce)$', r'\1\2\2\3'),
    (r'^(.*(?:[bcdfghjklmnprstvwxyz]|qu)[aeiou])([bcdfgklmnprtvz]) \^ (e[rn]ing)$', r'\1\2\2\3'),
    (r'^(.*(?:[bcdfghjklmnprstvwxyz]|qu)[aeiou])([bcdfgklmnprtvz]) \^ (ation)$', r'\1\2\2\3'),
    (r'^(.*(?:[bcdfghjklmnprstvwxyz]|qu)[aeiou])([bcdfgklmnprtvz]) \^ (iness)$', r'\1\2\2\3'),
    (r'^(.*(?:[bcdfghjklmnprstvwxyz]|qu)[aeiou])([bcdfgklmnprtvz]) \^ (ably)$', r'\1\2\2\3'),
    (r'^(.*(?:[bcdfghjklmnprstvwxyz]|qu)[aeiou])([bcdfgklmnprtvz]) \^ (ened)$', r'\1\2\2\3'),
    (r'^(.*(?:[bcdfghjklmnprstvwxyz]|qu)[aeiou])([bcdfgklmnprtvz]) \^ (ings)$', r'\1\2\2\3'),
]

ORTHOGRAPHY_RULES_ALIASES = {
    'able': 'ible',
    'ability': 'ibility',
}

SUFFIX_KEYS = ()
ORTHOGRAPHY_WORDLIST = 'american_english_words.txt'
DICTIONARIES_ROOT = 'asset:plover:assets'
DEFAULT_DICTIONARIES = ()