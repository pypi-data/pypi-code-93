"""
Author: Shawan Mandal
    
MIT License, see LICENSE for more details.
Copyright (c) 2021 Shawan Mandal

"""

import sys, json
try:
    from utils import handleRequests, getSoupObj, ParseUsage, ParseSynonymsAndAntonyms
except:
    from .utils import handleRequests, getSoupObj, ParseUsage,  ParseSynonymsAndAntonyms

class PythonVersionError(Exception):
    pass

class Finder(object):
    """
    Finder
    Usage:
        >>> Meanings = Finder()
        >>> print(Meanings.findMeanings('apple'))
        >>> print(Meanings.findUsage('apple', 8))
        >>> print(Meanings.findSynonyms('apple', 8))
        >>> print(meanings.findAntonyms('apple', 12))
    """
    def __init__(self):
        self.searching = "Please wait while I'm searching for "
        self.isPython3 = True
        if (sys.version_info.major) < 3:
            self.isPython3 = False
        else:
            pass

    def __IfnotFound(self, query):
        '''
        1.  Returns any possible matches incase if the queried word is not found
        2.  Returns a resolution incase if nothing is found
        '''
        resolution = {"message": f"Couldn't find any results for {query.upper()}, try searching the web..."}

        res = handleRequests(query)
        soup = getSoupObj(res)

        try:
            suggestedContent = soup.find(attrs={'class': 'spell-suggestions-subtitle css-ycbn4w e19m0k9k5'})
            suggestedWord = suggestedContent.find('a')
            return {"message": f"Couldn't find results for {query}, Did you mean {suggestedWord.text}?"}
        except:
            return resolution
    
    def findMeanings(self, query):
        '''
        Searches for a word and returns response in a python Dictionary Obj,
        Alternatively searches for any possible matches incase the queried word is not found
        '''
        if (self.isPython3):
            pass
        else:
            raise PythonVersionError("Python version 3 or newer is required")

        print(self.searching + "meanings...")
        res = handleRequests(query)
        soup = getSoupObj(res)
        dataItems = {
            "word": query.title(),
            "meanings": []
        }

        contents = soup.findAll('section', attrs={'class': 'e1hk9ate4'})
        for each in contents:
            defFound = True
            json_contents = {}
            partOfSpeech = each.find(attrs={'class': 'e1hk9ate3'})
            for pos in partOfSpeech.find_all("span", {'class':'luna-inflected-form'}):
                    pos.replaceWith('')
            for pos1 in partOfSpeech.find_all("span", {'class':'inflected-form'}):
                    pos1.replaceWith('')
            for pos2 in partOfSpeech.find_all("span", {'class':'luna-pronset'}):
                    pos2.replaceWith('')
            partOfSpeech = partOfSpeech.get_text().title().strip()
            if partOfSpeech[-1] == ",":
                partOfSpeech = partOfSpeech[0:][:-1]
            json_contents = {
                "partOfSpeech": partOfSpeech,
                "definitions": []
            }
            definitions = each.findAll('div', attrs={'class': 'e1hk9ate0'})
            def_list = ""
            for definition in definitions:
                def_content = definition.find(attrs={'class': 'e1q3nk1v2'})
            
                if def_content:
                    for tag in def_content.find_all("span", {'class':'luna-example'}):
                        tag.replaceWith('')
                    def_content = def_content.get_text().replace('(', '').replace(')', '').replace(':', '').strip()
                    def_content = def_content[0].upper() + def_content[1:]
                else:
                    def_content = ''
            
                try:
                    example = definition.find(attrs={'class': 'luna-example'}).text
                except:
                    example = ""

                def_list += def_content
                def_list = def_list.strip()
            if def_list == "":
                defFound = False
            else:
                json_content = {
                    "definition": def_list,
                    "example": example
                }
            if defFound:
                json_contents['definitions'].append(json_content)
                dataItems['meanings'].append(json_contents)
            else:
                pass
        if dataItems['meanings']:
            return json.dumps(dataItems, indent=2, ensure_ascii=False)
        else:
            suggestions = self.__IfnotFound(query)
            return suggestions
        #return word, dataItems

    def findUsage(self, query, maxItems=5):
        """
        getUsage
        -----
        Returns a Python Dictionary of usage examples \n
        Args: Query -> (string), Maximum items -> (int) By default its value is 5

        Returns: \n
        {
            "word": [ ]
        }
        """
        if (self.isPython3):
            pass
        else:
            raise PythonVersionError("Python version 3 or newer is required")

        print(self.searching + "usage examples...")

        res = ParseUsage(query)
        soup = getSoupObj(res)
        usageExamples = {}
        examples = []
        try:
            usageClass = soup.find(attrs={'class': 'examples'})
            for junk in usageClass.find_all("div", {'class':'moreInfo active'}):
                            junk.replaceWith('')
            
            exg = usageClass.find(attrs={'class': 'exg'})
            ul = exg.find('ul').find_all('li')
            count = 0
            for each in ul:
                if count < maxItems:
                    text = each.text[1:][:-1]
                    examples.append(text[0].upper() + text[1:].strip())
                count += 1
        except:
            suggestions = self.__IfnotFound(query)
            examples.append(suggestions)
        usageExamples = {
            f"{query}": examples
        }

        return json.dumps(usageExamples, indent=2, ensure_ascii=False)
    
    def findSynonyms(self, query, maxItems=5):
        """
        findSynonyms
        ------------
        Returns a Python Dictionary of Synonyms \n
        Args: Query -> (string), Maximum items -> (int) By default its value is 5

        Returns: \n
        {
            "word": [ ]
        }
        """

        if (self.isPython3):
            pass
        else:
            raise PythonVersionError("Python version 3 or newer is required")

        print(self.searching + "Synonyms...")

        res = ParseSynonymsAndAntonyms(query)
        soup = getSoupObj(res)
        Syns = []
        Synonyms = {}

        try:
            count = 0
            SynonymsClass = soup.find(attrs={'class': 'e1ccqdb60'}).find_all('li')
            for each in SynonymsClass:
                if count < maxItems:
                    Syns.append(each.text[0].upper() + each.text[1:].strip())
                count += 1
        except:
            suggestions = self.__IfnotFound(query)
            Syns.append(suggestions)

        Synonyms = {
            f"{query}": Syns
        }

        return json.dumps(Synonyms, indent=2, ensure_ascii=False)
        
    def findAntonyms(self, query, maxItems=5):
        """
        findAntonyms
        ------------
        Returns a Python Dictionary of Antonyms \n
        Args: Query -> (string), Maximum items -> (int) By default its value is 5

        Returns: \n
        {
            "word": [ ]
        }
        """

        if (self.isPython3):
            pass
        else:
            raise PythonVersionError("Python version 3 or newer is required")

        print(self.searching + "Antonyms...")

        res = ParseSynonymsAndAntonyms(query)
        soup = getSoupObj(res)
        Antyns = []
        Antonyms = {}
        count = 0

        try:
            AntonymsClass = soup.find(attrs={'id': 'antonyms'})
            Antonym = AntonymsClass.find(attrs={'class': 'css-ixatld e15rdun50'}).find('ul').find_all('li')
            for each in Antonym:
                if count < maxItems:
                    Antyns.append(each.text[0].upper() + each.text[1:].strip())
                count += 1
        except:
            suggestions = self.__IfnotFound(query)
            Antyns.append(suggestions)

        Antonyms = {
            f"{query}": Antyns
        }

        return json.dumps(Antonyms, indent=2, ensure_ascii=False)