import re
from typing import Tuple, Union, List

from nltk.corpus import stopwords


class Fumes:
    """
    Instantiate a Fumes object.
    Text will be fumigated according to mention methods.
    """

    def __init__(self):
        self.stopwords = stopwords.words('english')
        self.text = None

    # Remove symbols
    def _sym(self, extract=False):
        regex = r"[^a-zA-Z0-9]"
        garbage = None
        if extract:
            garbage = re.findall(regex, self.text)
        return re.sub(r"[^a-zA-Z0-9]", " ", self.text), garbage

    # Remove Links
    def _url(self, extract=False):
        regex = r'(\w+:\/\/\S+)|^rt|http.+?'
        garbage = None
        if extract:
            garbage = re.findall(regex, self.text)
        return re.sub(regex, "", self.text), garbage

    # Remove Numbers
    def _num(self, extract=False):
        regex = r'\d+'
        garbage = None
        if extract:
            garbage = re.findall(regex, self.text)
        return re.sub(regex, "", self.text), garbage

    # Remove Emojis
    def _emo(self, extract=False):
        regex = "[" u"\U0001F600-\U0001F64F" u"\U0001F300-\U0001F5FF" u"\U0001F680-\U0001F6FF" \
                u"\U0001F1E0-\U0001F1FF" u"\U00002500-\U00002BEF" u"\U00002702-\U000027B0" \
                u"\U00002702-\U000027B0" u"\U000024C2-\U0001F251" u"\U0001f926-\U0001f937" \
                u"\U00010000-\U0010ffff" u"\u2640-\u2642" u"\u2600-\u2B55" u"\u200d" u"\u23cf" \
                u"\u23e9" u"\u231a" u"\ufe0f" u"\u3030""]+ "
        garbage = None
        if extract:
            garbage = re.findall(regex, self.text)
        emoj = re.compile(regex, re.UNICODE)
        return re.sub(emoj, '', self.text), garbage

    # Remove Stopwords
    def _stopwords(self, extract=False):
        garbage = None
        if extract:
            garbage = [word for word in self.text.split() if word in self.stopwords]
        return " ".join([word for word in self.text.split() if word not in self.stopwords]), garbage

    def clean(self, text: str, methods: List[str] = None, extract: bool = False) -> Union[str, Tuple[str, list]]:
        """
        Fumigate the text

        :param methods: Available methods ["sym" | "num" | "url" | "emo"].
        :type methods: list[string]

        :param text: The text to fumigate.
        :type text: string

        :param extract: Return fumigated values.
        :type extract: bool

        :return: (The result after fumigation, fumigated values).
        :rtype: Union[str, Tuple[str, list]]
        """

        try:
            self.text = text.lower()
            if methods is None:
                return self.purge(text)
            else:
                garbage_list = []
                for method in methods:
                    self.text, garbage = eval("self._" + method.lower() + f"({extract})")
                    garbage_list.append(garbage)
                self.text = re.sub(r"\s+", " ", self.text)
                if extract:
                    return self.text, garbage_list
                return self.text
        except Exception as e:
            raise Exception(e)

    def purge(self, text: str) -> str:
        """
        Fumigate the text using all methods

        :param text: The text to fumigate.
        :type text: string

        :return: The result after fumigation.
        :rtype: str
        """
        try:
            self.text = text.lower()
            # Remove Symbols, Links, Numbers, Emojis
            self.text = re.sub(r"(@[A-Za-z0-9]+)|(\d+)|([^0-9A-Za-z ])|(\w+:\/\/\S+)|^rt|http.+?", "", self.text)
            self.text = re.sub(r"\s+", " ", self.text)
            # remove StopWords
            self.text, _ = self._stopwords()
            return self.text
        except Exception as e:
            raise Exception(e)

