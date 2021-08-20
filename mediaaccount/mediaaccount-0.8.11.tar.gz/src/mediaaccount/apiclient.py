import requests
from collections import deque
from typing import List, Literal, Optional, Union
import logging

logger = logging.getLogger("mediaaccount")

from .models import Article

class MediaAccountClient(object):
    """
        Client zum Abruf der Daten von der MediaAccount Api
    """

    api_key: str
        
    base_url = 'http://api.media-account.de/api/'
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def articles(self, typ, von = None, bis = None, maxItems = 150, **kwargs):
        """
        Gibt ein Tuple zurück: Artikellist, Link zur nächsten 'seite', gesamtzahl
        """
        headers = {'api_key' : self.api_key}
        params = {'typ' : typ, 'von': von, 'bis':bis, 'maxItems' : maxItems}
        params.update(kwargs)
        
        response = requests.get(f'{self.base_url}v2/articles', headers = headers, params = params)
        response.raise_for_status()
        
        result = self._readResponse(response)
        logger.info(f'Request MediaAccount-API successful - {len(result[0]):,} Articles - total: {result[2]:,} Articles')
        return result

    def articlesUrl(self, url):
        headers = {'api_key' : self.api_key}
        response = requests.get(url, headers = headers)
        response.raise_for_status()

        result = self._readResponse(response)
        logger.info(f'Request MediaAccount-API successful - {len(result[0]):,} Articles - total: {result[2]:,} Articles')
        return result

    def _readResponse(self, response):
        """"lesen der Daten aus der ApiResponse"""
        responseData = response.json()
        nextPageLink = responseData['NextPageLink']
        articles = list(map(lambda x: Article.from_dict(x), responseData['Items']))
        count = responseData['Count']

        return (articles, nextPageLink, count)
    
    def scroll(self, typ, von = None, bis = None, maxItems : int = 150):
        return ArticleScroll(self, typ, von, bis, maxItems)

class ArticleScroll:
    """
        Iterator für alle Artikel
    """
    state : Literal['initialized', 'running']
    totalCount  : int
    currentQueue : deque
    nextLink : Optional[str]
    maxItems : int


    def __init__(self, client : MediaAccountClient, typ : str, von :str, bis : str, maxItems : int):
        self.client = client
        self.typ = typ
        self.von = von
        self.bis = bis
        self.currentQueue = deque()
        self.nextLink = None
        self.maxItems = maxItems

    def __iter__(self):
        logging.debug("Start Interator for Articles")
        self.state = 'initialized'
        self.nextLink = None
        self.currentQueue = deque()
        return self

    def __next__(self):
        if (self.currentQueue):
            return (self.currentQueue.pop(), self.totalCount)
        
        if (self.state == 'initialized'):
            # erster abruf
            articles, nextlink, totalCount = self.client.articles(self.typ, self.von, self.bis, self.maxItems)

            if (len(articles) == 0):
                raise StopIteration
            
            # mapping items
            self.totalCount = totalCount
            self.nextLink = nextlink
            self.currentQueue = deque(articles)
            self.state = 'running'

            return (self.currentQueue.pop(), self.totalCount)

        if (self.nextLink == None):
            raise StopIteration

        if (self.state == 'running'):
            articles, nextlink, totalCount = self.client.articlesUrl(self.nextLink)

            if (len(articles) == 0):
                raise StopIteration
            
            self.totalCount = totalCount
            self.nextLink = nextlink
            self.currentQueue = deque(articles)
            return (self.currentQueue.pop(), self.totalCount)