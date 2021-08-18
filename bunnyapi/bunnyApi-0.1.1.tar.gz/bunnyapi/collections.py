import requests
import json

class CollectionsApi:
    
    def __init__(self, api_key: str, library_id: str):
        """
        Initialize API for managing collections.

        Parameters:
        api_key (str): Your private API key
        library_id (str): The ID of the video library you want to operate on
        """
        self._api_key = api_key
        self._library_id = library_id
        self._base_url = 'http://video.bunnycdn.com/library'
        self._headers = { 'AccessKey' : self._api_key }
    
    def get_collection(self, collection_id: str) -> dict:
        """
        Retrieve collection.

        Parameters:
        collection_id (str): ID of the collection to retrieve

        Returns:
        dict: The collection
        """
        url = f'{self._base_url}/{self._library_id}/collections/{collection_id}'
        r = requests.get(url, headers=self._headers)
        r.raise_for_status()
        return r.json()
    
    def update_collection(self, collection_id: str, collection: dict) -> dict:
        """
        Update details about from a collection.

        Parameters:
        collection_id (str): ID of the collection to update
        collection: The updated collection object
        
        Returns:
        dict: HTTP status message
        """
        url = f'{self._base_url}/{self._library_id}/collections/{collection_id}'
        headers = self._headers
        headers.update({'Content-Type' : 'application/*+json'})
        r = requests.post(url, headers=headers, data=json.dumps(collection))
        r.raise_for_status()
        return r.json()

    def delete_collection(self, collection_id: str) -> dict:
        """
        Delete a collection and all its videos.

        Paramaters:
        collection_id (str): ID of the collection to delete

        Returns:
        dict: HTTP status message
        """
        url = f'{self._base_url}/{self._library_id}/collections/{collection_id}'
        r = requests.delete(url, headers=self._headers)
        r.raise_for_status()
        return r.json()
    
    def list_collections(self, page='1', items_per_page='100', search=None, order_by='data') -> dict:
        """
        Retrieve a list of all collections

        Parameters:
        page (str): The page number
        items_per_page (str): Number of items per page
        search (str): A search string
        order_by (str): order result by date, ???

        Returns:
        dict: ???
        """
        url = f'{self._base_url}/{self._library_id}/collections'
        r = requests.get(url, headers=self._headers)
        params = {
            'page' : page,
            'itemsPerPage' : items_per_page,
            'orderBy' : order_by
        }
        if search:
            params['search'] = search
        r = requests.get(url, headers=self._headers, params=params)
        r.raise_for_status()
        return r.json()

    def create_collection(self, name: str) -> dict:
        """
        Creates a new collection

        Parameters:
        name (str): Name of the new collection

        Returns:
        dict: HTTP status message
        """
        url = f'{self._base_url}/{self._library_id}/collections'
        headers = self._headers
        headers.update({'Content-Type' : 'application/*+json'})
        payload = {
            'name' : name
        }
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        r.raise_for_status()
        return r.json()
