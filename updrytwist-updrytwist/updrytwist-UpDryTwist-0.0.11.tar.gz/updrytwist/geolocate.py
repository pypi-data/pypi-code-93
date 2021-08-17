
from . import config
import pickle
import urllib.request
import json
from typing import Union
import logging

_LOGGER = logging.getLogger(__name__)

LOCATIONIQ_URL = 'https://us1.locationiq.com/v1/reverse.php?format=json'
LOCATIONIQ_KEY = 'pk.0f512caca958cbf439668c75a9c4e0c2'

CACHE_FILE = '/etc/piclock/geolocate.pickle'


class Location:

    def __init__ ( self, latitude : float, longitude : float,
                   displayName : str,
                   houseNumber : str,
                   road : str,
                   theatre: str,
                   pedestrian : str,
                   cityDistrict : str,
                   suburb : str,
                   city : str,
                   county : str,
                   stateDistrict : str,
                   state : str,
                   postcode : str,
                   country : str,
                   countryCode : str ) :
        self.latitude = latitude
        self.longitude = longitude
        self.displayName = displayName
        self.houseNumber = houseNumber
        self.road = road
        self.theatre = theatre
        self.pedestrian = pedestrian
        self.cityDistrict = cityDistrict
        self.suburb = suburb
        self.city = city
        self.county = county
        self.stateDistrict = stateDistrict
        self.state = state
        self.postcode = postcode
        self.country = country
        self.countryCode = countryCode

    def key ( self ) -> str:
        return Location.keyFor( self.latitude, self.longitude )

    @staticmethod
    def keyFor( latitude : float, longitude : float ):
        return f'lat{latitude}lon{longitude}'

    def placeName ( self ) -> str:
        if self.city:
            return f'{self.city}, {self.country}'
        if self.state:
            return f'{self.state}, {self.country}'
        if self.county:
            return f'{self.county}, {self.country}'
        if self.stateDistrict:
            return f'{self.stateDistrict}, {self.country}'
        if self.displayName:
            return self.displayName
        return f'{self.country}'


class Locations:

    def __init__ ( self, cacheFile : str ):
        self.cacheFile = cacheFile
        self.locations = {}

    def addLocation ( self, location : Location ):
        self.locations[ location.key() ] = location

    def find ( self, latitude : float, longitude : float ) -> Union[Location, None] :
        key = Location.keyFor( latitude, longitude )
        if key in self.locations :
            return self.locations[key]
        return None

    @staticmethod
    def loadFromFile ( cacheFile : str ) :
        try:
            return pickle.load( open(cacheFile, 'rb'))
        except Exception as e:
            _LOGGER.info( f'Exception loading cache file {cacheFile}: {e}', exc_info=True)
            return Locations(cacheFile)

    def saveToFile ( self ):
        _LOGGER.debug( f'Saving to file {self.cacheFile} ...')
        pickle.dump( self, open(self.cacheFile, 'wb' ), protocol=pickle.HIGHEST_PROTOCOL )


class GeoLocate:

    def __init__ ( self, configuration : {} ):

        self.url       = config.dictread( configuration, "Url", LOCATIONIQ_URL )
        self.apiKey    = config.dictread( configuration, "ApiKey", LOCATIONIQ_KEY )
        self.cacheFile = config.dictread( configuration, "CacheFile", CACHE_FILE )

        self.locations = Locations.loadFromFile( self.cacheFile )

    def resolveLocation ( self, latitude : float, longitude : float ) -> Location :
        theUrl = f'{self.url}&lat={float(latitude):.10f}&lon={float(longitude):.10f}&key={self.apiKey}'
        with urllib.request.urlopen( theUrl ) as url:
            data = json.loads(url.read().decode())
            address = data['address']
            return Location( latitude, longitude,
                             config.dictread( data, 'display_name', None ),
                             config.dictread( address, 'house_number', None ),
                             config.dictread( address, 'road', None ),
                             config.dictread( address, 'theatre', None ),
                             config.dictread( address, 'pedestrian', None ),
                             config.dictread( address, 'city_district', None ),
                             config.dictread( address, 'suburb', None ),
                             config.dictread( address, 'city', None ),
                             config.dictread( address, 'county', None ),
                             config.dictread( address, 'state_district', None ),
                             config.dictread( address, 'state', None ),
                             config.dictread( address, 'postcode', None ),
                             config.dictread( address, 'country', None ),
                             config.dictread( address, 'countryCode', None ) )

    def lookupLocation ( self, latitude : float, longitude : float ) -> Location :

        location = self.locations.find( latitude, longitude )
        if not location:
            location = self.resolveLocation( latitude, longitude )
            self.locations.addLocation(location)
            self.saveCache()
        return location

    def saveCache ( self ):
        try:
            self.locations.saveToFile()
        except Exception as e:
            _LOGGER.error( f'Failed to save {self.locations.cacheFile} with error {e}', exc_info=True)
