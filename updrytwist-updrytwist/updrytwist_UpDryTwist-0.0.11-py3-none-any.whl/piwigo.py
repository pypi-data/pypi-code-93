
from . import config
import logging
import requests
import os
import re
import json
import asgiref.sync
import datetime

_LOGGER = logging.getLogger(__name__)

BOOL_TO_STR = { True: 'true', False: 'false'}
MAX_TO_CHECK = 100


class GetPicUrlService:

    def __init__ ( self, configuration : {} ):

        self.configuration = configuration
        self.maxToCheck = config.dictread( configuration, "MaxPicturesToCheck", MAX_TO_CHECK )
        self.baseUrl = config.forceread( configuration, "PiwigoUrl" )

    @staticmethod
    def isDangerousDashes ( picName : str ) -> bool:
        subsplit = picName.split('-')
        tooShort = True
        for subterm in subsplit:
            if len(subterm) > 2:
                tooShort = False
                break
        return tooShort


    @staticmethod
    def cleanQuery ( picName : str ) -> str :

        # Don't split on a dash
        terms = re.split('[/,&\'. ;\\\\]', picName)
        query = ""
        for term in terms:
            if len(term) > 3 and not GetPicUrlService.isDangerousDashes(term):
                if len(query) > 1:
                    query += ' '
                query += term
        return query

    @staticmethod
    def parseResponse ( response : json, picName : str, picDate ) :
        paging = response['paging']
        count = int(paging['count'])
        if count == 0:
            return None
        if picDate and type(picDate) == datetime.datetime:
            compareDate = picDate.strftime('%Y-%m-%d %H:%M:%S')
        else:
            compareDate = picDate
        for image in response['images']:
            # url = image['element_url']
            picUrl = image['page_url']
            matches = True
            if 'file' in image:
                fileName = image['file']
                origName = picName[-len(fileName):]
                if origName != fileName:
                    matches = False
            if 'date_creation' in image:
                createDate = image['date_creation']
                if compareDate and compareDate != createDate:
                    matches = False
            if matches:
                return picUrl
        return None

    @staticmethod
    def clean ( picName : str ):
        return picName.replace( ' ', '%20').replace("'",'_').replace('@','_').replace('#','_').replace('!','_').replace(':','_').replace(';','_')

    @staticmethod
    def getDateBrackets ( picDate ) :
        if not picDate:
            return None, None
        try:
            if type(picDate) == str:
                theDate = datetime.datetime.strptime( picDate, '%Y-%m-%d %H:%M:%S')
            elif type(picDate) == datetime.datetime:
                theDate = picDate
            else:
                raise ValueError(f'Unknown type for expected picDate value: {picDate} type = {type(picDate)}')
            endDate = theDate + datetime.timedelta(seconds=1)
            startDate = theDate + datetime.timedelta(seconds=-1)
            return startDate.strftime('%Y-%m-%d %H:%M:%S'), endDate.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            _LOGGER.info(f'Failed to convert date for search: {picDate} with error {e}')
            return None, None

    async def getUrls ( self, picName : str, picDate ) -> (str, str):

        try:
            piwigo = Piwigo( self.configuration )
            await asgiref.sync.sync_to_async(piwigo.pwg.session.login)( username=piwigo.userId, password=piwigo.password )
            dateStart, dateEnd = self.getDateBrackets(picDate)
            if dateStart and dateEnd:
                response = await asgiref.sync.sync_to_async(piwigo.pwg.images.search)( query=self.cleanQuery(picName),
                                                                                       per_page=self.maxToCheck,
                                                                                       f_min_date_created=dateStart,
                                                                                       f_max_date_created=dateEnd )
            else:
                response = await asgiref.sync.sync_to_async(piwigo.pwg.images.search)( query=self.cleanQuery(picName), per_page=self.maxToCheck )
            picUrl = self.parseResponse(response, picName, picDate )
        except Exception as e:
            _LOGGER.warning( f'Unable to fetch picture URL for {picName} with error {e}', exc_info=True)
            picUrl = None
        galleryUrl = self.baseUrl + '/galleries/' + self.clean(picName)
        return picUrl, galleryUrl


class WsNotExistException(Exception):

    def __init__(self, method):
        self._method = method

    def __str__(self):
        return "Ws %s not exist" % self._method


class WsErrorException(Exception):

    def __init__(self, strerr):
        self._strerr = strerr

    def __str__(self):
        return self._strerr


class WsPiwigoException(Exception):

    def __init__(self, err, message):
        self.err = err
        self.message = message

    def __str__(self):
        return "%s : %s" % (self.err, self.message)


class Piwigo:

    def __init__ ( self, configuration : {} ):

        self.url = config.forceread( configuration, "PiwigoUrl" )
        self.userId = config.forceread( configuration, "PiwigoUserId" )
        self.password = config.forceread( configuration, "PiwigoPassword" )
        self.cookies = None

        if self.url[-1] == '/' :
            self.url = self.url[:-1]
        self.webServiceUrl = f'{self.url}/ws.php?'

    def __getattr__(self, name):
        return PiwigoWebService(self, name)

    def setCookies ( self, webService, request ):

        try:
            if webService.methodName == 'pwg.session.login' and request.json()['stat'] == 'ok':
                self.cookies = request.cookies
            elif webService.methodName == 'pwg.session.logout':
                self.cookies = None
        except Exception as e:
            _LOGGER.info( f'Failed to set cookies for request with error {e}', exc_info=True )


class PiwigoWebService:

    def __init__(self, piwigo : Piwigo, methodName : str):
        self.methodName = methodName
        self.piwigo = piwigo
        self.isPostOnly = False

    def getMethodDetail(self):
        try:
            methodDetail = self.piwigo.reflection.getMethodDetails(methodName=self.methodName)
            return methodDetail
        except WsPiwigoException as e:
            _LOGGER.info( f'getMethodDetail() error {e}' )
            raise WsNotExistException(self.methodName)

    def getPostOnly(self):
        try:
            response = self.getMethodDetail()
            options = response['options']
            if len(options) < 1:
                return False
            else:
                return options['post_only']
        except WsNotExistException as e:
            raise e
        except Exception as e:
            _LOGGER.info( f'Exception in checking for isPostOnly: {e}', exc_info=True)
            return False

    def getParams(self):
        return { param['name'] : param for param in self.getMethodDetail()['params'] }

    def __call__(self, *arg, **kw):
        if self.methodName != 'reflection.getMethodDetails':
            self.isPostOnly = self.getPostOnly()
        for i in kw:
            if type(kw[i]) == bool :
                kw[i] = BOOL_TO_STR[kw[i]]
        serviceUrl = self.piwigo.webServiceUrl
        kw["method"] = self.methodName
        kw["format"] = "json"
        params = kw
        data = {}
        p = None
        if 'image' in kw:
            p = open(kw['image'], 'rb')
            files = {'image': p}
            params = { i : params[i] for i in params if i != 'image'}
        else:
            files = {}
        if self.isPostOnly:
            data = { i : params[i] for i in params if i != 'format'}
            params = { i : params[i] for i in params if i == 'format'}
            r = requests.post(serviceUrl, params=params, data=data, files=files, cookies=self.piwigo.cookies)
        else:
            r = requests.get(serviceUrl, params=params, data=data, files=files, cookies=self.piwigo.cookies)
        if p :
            p.close()
        try:
            result = r.json()
            if result['stat'] == 'fail':
                raise WsPiwigoException(result['err'], result['message'])
            self.piwigo.setCookies(self, r)
            return result['result']
        except Exception as e:
            _LOGGER.info(f'__call__() error {e}')
            raise WsErrorException(r.text)

    def __getattr__(self, name):
        return PiwigoWebService(self.piwigo, '%s.%s' % (self.methodName, name))

    def __str__(self) -> str:
        try:
            return "%s : %s" % (self.methodName, self.getMethodDetail()['description'])
        except WsNotExistException as _e:
            return "%s : not exist" % self._method


if __name__ == '__main__':

    if os.getenv('CONFIGFILE', None) is None:
        config.DEFAULT_CONFIG = 'piclock.yaml'
    config.initialize()
    getUrlService = GetPicUrlService( config.Config.get( "Piwigo" ) )
    #url, gUrl = asgiref.sync.async_to_sync(getUrlService.getUrls)("2018 - Family Trip to Miami, Belize, Guatemala/IMG_2035.JPG", "2018-12-26 16:46:56")
    #print(url)
    #print(gUrl)
    url, gUrl = asgiref.sync.async_to_sync(getUrlService.getUrls)("2011-03-22 Patrick Crans-Montana/2011-03-22 14-50-50.JPG", "2011-03-22 14:50:50")
    print(url)
    print(gUrl)
