
"""
----------------------
Python Dictionary API 
----------------------

PyDictAPI is library written in Python, that can be used to fetch meanings and translation.

Currently supports only English-English dictionary searches

Basic usage:

   >>> from PyDictAPI import Finder
   >>> Meanings = Finder()
   >>> print(Meanings.findMeanings('apple'))

Output:

`{
    'word': 'apple', 
    'meanings': [
        {
            'partOfSpeech': 'noun', 
            'definitions': [
                {
                    'definition': 'the usually round, red or yellow, edible fruit of a small tree, Malus sylvestris, of the rose family.', 
                    'example': ''
                }
            ]
        }, 
        {
            'partOfSpeech': 'noun', 
            'definitions': [
                {
                    'definition': 'a rosaceous tree, Malus sieversii, native to Central Asia but widely cultivated in temperate regions in many varieties, having pink or white fragrant flowers and firm rounded edible fruits', 
                    'example': ''
                }
            ]
        }
    ]
}`
---------------------------------------    
Finding Examples, Synonyms and Antonyms
---------------------------------------

   >>> print(Meanings.findUsage('help', 2)) #Finding Examples
   
    # Here 2 defines the maximum number of examples to be included in the response, 
    # by default it is set to 5

   >>> print(Meanings.findSynonyms('help', 4)) #Finding Synonyms
   >>> print(Meanings.findAntonyms('help', 4)) #Finding Antonyms

----------------
Translating text
----------------

### Example:
>>> # Import the module first
>>> from PyDictAPI import Translate
>>> t = Translate() #   Creates an instance of Translate class
>>> 
>>> # You can get all supported language list through languages_help()
>>> languages = t.languages_help(pretty=True)
>>> # Pretty=true returns the list of supported languages in a well structured manner. By default Pretty is set to False
>>> 
>>> # Tranlate English into Hindi
>>> print(t.translateItems("Hello, How are you?", "hi"))

`{'query': 'Hello, How are you?', 'language_detected': 'Hindi', 'translation': 'नमस्कार किसे हो आप?'}`

Full documentation is at <https://github.com/imshawan/PyDictAPI>.

copyright: (c) 2021 by Shawan Mandal.

license: MIT License, see LICENSE for more details.
"""
__author__ = "Shawan Mandal"
__email__ = "imshawan.dev049@gmail.com"
__version__ = "1.5.1"

try:
    from .scrape import *
    from .translator import *
except:
    from scrape import *
    from translator import *


