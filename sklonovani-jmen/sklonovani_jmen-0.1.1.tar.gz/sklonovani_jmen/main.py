import requests

class Client:
    def __init__(self, klic="klic"):
        """Initializes the object for sending requests to the API of
        https://www.sklonovani-jmen.cz.

        Args:
            klic (str): Unique key for using the API. Defaults to "klic".
        """
        self.key = klic

    def _split_long_url(self, string_to_split):
        """Splitting strings longer than 7000
        characters (used to shorten "jmeno" argument in request method)

        Returns: list of strings
        """
        strings_list = []

        # Slices the string from the front after 7000 characters
        while len(string_to_split) > 7000:
            substring_length = string_to_split.find("|", 7000, 7500)
            
            if substring_length == -1:
                # "|" character was not found
                break
            
            strings_list.append(string_to_split[:substring_length])
            string_to_split = string_to_split[(substring_length+1):]
        strings_list.append(string_to_split)

        return strings_list

    def request(self, jmeno="Adelaida", pad=5, osloveni_zeny=None, osloveni_muze=None, \
        osloveni_firmy=None, pohlavi=0, tvar=1, format=None):
        """Sends a request to the API to inflect names or obtain information about gender.

        Args:
            jmeno (str, list, set or dict): Names to inflect (česky: skloňovat). When using a string, separate
                each name by "|". Defaults to "Adelaida".

            pad (int, optional): Grammatical case of inflection. Valid values 
                are 2-7 (representing grammatical cases for nouns used in Czech) or 0.
                Use 0 to obtain information about gender (return value is "m", "f" or "mf" 
                when the gender is arguable)
                Defaults to 5.
            
            osloveni_zeny (str, optional): Phrase to put in front of women's names. 
                Defaults to "paní" (default values are inflicted).
            osloveni_muze (str, optional): Phrase to put in front of men's names.
                Defaults to "pane" (default values are inflicted).
            osloveni_firmy (str, optional): Phrase to put in front of companies' names.
                Defaults to "vážení".
            pohlavi (int, optional): Gender of the name(s). Used to make results more accurate.
                1 - man
                2 - woman
                0 - unknown gender
                Defaults to 0.
            tvar (int, optional): Number code for items the API shall return. 
                For more information see https://www.sklonovani-jmen.cz/dokumentace.
                Defaults to 1.
            format (str, optional): Use "json" to return values in the JSON format.
                Otherwise, list of strings will be returned. Defaults to None.

        Returns:
            [list of strings]: Values returned by the API. 
            Can contain inflected names, gender information ("m", "f" or "mf") or error codes.
        """

        # Creating the first part of url (without the "jmeno" arg)
        kwargs_dict = {
            "osloveni-zeny": osloveni_zeny,
            "osloveni-muze": osloveni_muze,
            "osloveni-firmy": osloveni_firmy,
            "pohlavi": pohlavi,
            "tvar": tvar,
            "format": format
        }
        url_prefix = f"https://www.sklonovani-jmen.cz/api?klic={self.key}&pad={pad}"
        for key, item in kwargs_dict.items():
            if item is not None:
                url_prefix += f"&{key}={item}"

        
        # Creating a list to use as "jmeno" argument in API request 
        if type(jmeno) == str:
            names_str = jmeno
        elif type(jmeno) in (list, set, dict):
            names_str = "|".join(jmeno)

        names_list = self._split_long_url(names_str)
        result_list = []
        # API request for each item in the list
        for names_str in names_list:
            url = url_prefix + f"&jmeno={names_str}"
            result_list += requests.get(url).text.split("|")
        return result_list

    def account_info(self, informace=None):
        """Get information about your account (remaining credit...). 

        Args:
            informace (int, optional): Code of information.
            2 - Remaining credit
            4 - Remaining daily credit
            None - all information
            Defaults to None.

        Returns:
            [list of strings]: Obtained information from the API.
        """
        result = []
        if informace is None:
            for index in (2, 4):
                url = f"https://www.sklonovani-jmen.cz/api?klic={self.key}&informace={index}"
                result.append(requests.get(url).text)
        else:
            url = f"https://www.sklonovani-jmen.cz/api?klic={self.key}&informace={informace}"
            result.append(requests.get(url).text)
        return result
