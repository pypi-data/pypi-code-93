import json
import logging
from os import getenv, path
import shelve

import arrow

from ..exceptions import ClientError
from . import Client, HttpAuth

logger = logging.getLogger(__name__)


class NovatiqClient(Client):
    """Client for Novatiq CreatOR API.

    The API documentation can be found on the Platform wiki:
    https://github.com/rockabox/rbx/wiki/Novatiq

    """
    AUTH_PATH = 'auth'
    CATEGORIES = {
        'Family & Parenting': 'Family',
        'Food & Drink': 'Food and Drink',
        'Law, Government & Politics': 'Law & Govt',
        'News': 'Lifestyle',
        'Style & Fashion': 'Fashion',
        'Religion & Spirituality': 'Lifestyle',
        'Uncategorized': 'Lifestyle',
        'Non-Standard Content': 'Lifestyle',
        'Illegal Content': 'Adult Content',
    }
    ENDPOINT = 'https://cpdemo.awsdev.smartpipesolutions.com/api/v1/'
    LIVE_ENDPOINT = 'https://access.cp.novatiq.com/api/v1/'
    TIME_FORMAT = 'YYYY-MM-DD'
    TOKEN = 'accessToken'

    def __init__(self, destination='/tmp'):
        super().__init__()
        if getenv('RBX_ENVIRONMENT', 'dev') == 'live':
            self.ENDPOINT = self.LIVE_ENDPOINT

        self.shelf = path.join(destination, 'novatiq.segments')

    @property
    def auth(self):
        """Novatiq uses Digest Authentication."""
        return HttpAuth(self.token, key='Authorization')

    def create_campaign(self, brand, category, country_code, name, segments, start_date, end_date):
        """Create a campaign.

        If the campaign name already exists, we fetch that campaign to return the existing campaign
        ID. Technically this should never happen, except possibly in a development setting.
        """
        try:
            response = self.request('post', 'campaigns', data=[{
                'name': name,
                'clientName': brand,
                'countryIso': country_code,
                'campaignCategory': self.CATEGORIES.get(category, category),
                'startDate': arrow.get(start_date).format(self.TIME_FORMAT),
                'endDate': arrow.get(end_date).format(self.TIME_FORMAT),
                'segments': segments,
            }])
            return response[0]['id']
        except ClientError as e:
            error = json.loads(str(e))
            if error['errorInfo']['errorCode'] == '1200002':
                # Code '1200002' means 'Given name already exists'
                return self.get_campaign(name=name)['id']
            else:
                raise

    def get_campaign(self, campaign_id=None, name=None):
        """Retrieve the campaign given either its ID or its name."""
        response = self.request('get', 'campaigns')
        field = 'id' if campaign_id else 'name'
        value = campaign_id or name
        try:
            campaign = [row for row in response if row.get(field) == value][0]
        except IndexError:
            return None

        return {
            'id': campaign['id'],
            'segments': [segment['id'] for segment in campaign['segments']],
        }

    def get_message(self, response):
        """Extract the message from the requests response object."""
        return self.get_response(response).get('errorInfo', {}).get('errorMessage')

    def get_segments(self, country_code=None):
        """Get segments from local cache."""
        with shelve.open(self.shelf) as shelf:
            try:
                segments = shelf['segments']
            except KeyError:
                # The cache is empty
                segments = []

        segment_list = []
        for segment in segments:
            if country_code and country_code not in [segment['country'], 'ZZ']:
                continue
            segment_list.append(segment)

        return segment_list

    def list_segments(self):
        """List all segments available.

        According to the documentation, there is no pagination on this endpoint, so we expect the
        full list to be returned with a single call.

        See: https://cpdemo.awsdev.smartpipesolutions.com/api/docs/index.html#/segment/getSegments
        """
        response = self.request('get', 'segments')

        return [{
            'country': segment['countryIso'],
            'cpm': segment['segmentPrice'],
            'currency': 'TRY',
            'expression': segment['expression'],
            'id': segment['id'],
            'name': segment['name'],
        } for segment in response]

    def pause_campaign(self, campaign_id):
        """Pause a campaign."""
        response = self.request('post', f'campaigns/{campaign_id}/pause')
        return response['id']

    def start_campaign(self, campaign_id):
        """Start a campaign."""
        response = self.request('post', f'campaigns/{campaign_id}/start')
        return response['id']

    def store_segments(self):
        """Retrieve the list of segments, and then cache the results on a shelf.

        As no caching mechanism exists on the API, we simply override the content of the cache
        with the results from the list_segments() call.
        """
        segments = self.list_segments()
        with shelve.open(self.shelf) as shelf:
            shelf['segments'] = segments

    def update_campaign(self, campaign_id, name=None, segments=None, end_date=None):
        """Create a campaign.

        Only the name, segments, and end date can be changed.
        When providing a list of segments, the full list of segments must be provided. All missing
        ones will be removed from the campaign.
        """
        payload = {}

        if name is not None:
            payload['name'] = name

        if end_date is not None:
            payload['endDate'] = arrow.get(end_date).format(self.TIME_FORMAT)

        if segments:
            campaign = self.get_campaign(campaign_id=campaign_id)
            if campaign is not None:
                attached = set(campaign['segments'])
                segments_to_add = list(set(segments) - attached)
                if segments_to_add:
                    payload['segmentsToAdd'] = segments_to_add
                segments_to_remove = list(attached - set(segments))
                if segments_to_remove:
                    payload['segmentsToRemove'] = segments_to_remove

        if payload:
            response = self.request('post', f'campaigns/{campaign_id}', data=payload)
            return response['id']

        return campaign_id
