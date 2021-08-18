import requests
import json

class VideosApi:
    
    def __init__(self, api_key: str, library_id: str):
        """
        Initialize API for managing videos.

        Parameters:
        api_key (str): Your private API key
        library_id (str): The ID of the video library you want to operate on
        """
        self._api_key = api_key
        self._library_id = library_id
        self._base_url = 'http://video.bunnycdn.com/library'
        self._headers = { 'AccessKey' : self._api_key }


    def get_video(self, video_id: str) -> dict:
        """
        Request details from a given video.

        Parameters:
        video_id (str): The id of the video

        Returns:
        dict: Details from video
        """
        headers = self._headers
        headers.update({'Content-Type': 'application/*+json'})
        url = f'{self._base_url}/{self._library_id}/videos/{video_id}'
        r = requests.get(url, headers=self._headers)
        r.raise_for_status()
        return r.json()
    
    def update_video(self, video: dict) -> dict:
        """
        Update details about a video.

        Parameters:
        video (dict): The video to update (as retrieved by get_video)

        Returns:
        dict: HTTP status message
        """
        video_id = video.get('guid', None)
        url = f'{self._base_url}/{self._library_id}/videos/{video_id}'
        headers = self._headers
        headers.update({'Content-Type': 'application/*+json'})
        r = requests.post(url, headers=headers, data=json.dumps(video))
        r.raise_for_status()
        return r.json()
    
    def delete_video(self, video_id: str) -> dict:
        """
        Delete a video from your library.

        Paramaters:
        video_id (str): the id of the video

        Returns:
        dict: HTTP status report.
        """
        url = f'{self._base_url}/{self._library_id}/videos/{video_id}'
        r = requests.delete(url, headers=self._headers)
        r.raise_for_status()
        return r.json()
    
    def upload_video(self, video_id: str, path: str) -> dict:
        """
        Upload a video file to a video object.

        Parameters:
        video_id (str): The id of the video
        path (str): path of the file to upload
        
        Returns:
        dict: HTTP status response
        """
        url = f'{self._base_url}/{self._library_id}/videos/{video_id}'
        with open(path, 'rb') as f:
            r = requests.put(url, headers=self._headers, data=f)
            r.raise_for_status()
            return r.json()

    
    def list_videos(self, page='1', items_per_page='100', order_by='date', search=None, collection_id=None):
        """
        Retrieve a list of all videos from a library.

        Parameters:
        page (str): The page number
        items_per_page (str): The number of items per page
        search (str): A search string
        order_by (str): Order result by date, ???

        Returns:
        dict: ??
        """
        url = f'{self._base_url}/{self._library_id}/videos'
        params = {
            'page' : page,
            'itemsPerPage' : items_per_page,
            'orderBy' : order_by,
        }
        if search:
            params['search'] = search
        if collection_id:
            params['collection'] = collection_id

        r = requests.get(url, headers=self._headers, params=params)
        r.raise_for_status()
        return r.json()
    
    def create_video(self, title: str, collection_id=None) -> dict:
        """
        Create a video object in your library.

        Paramaters:
        title (str): The title of the video

        Returns:
        dict: The created video object
        """
        url = f'{self._base_url}/{self._library_id}/videos'
        headers = self._headers
        headers.update({'Content-Type': 'application/*+json'})
        payload = {'title' : title}
        if collection_id:
            payload['collectionId'] = collection_id
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        r.raise_for_status()
        return r.json()
    
    def set_thumbnail(self, video_id: str, path: str) -> dict:
        """
        Upload a custom thumbnail

        Parameters:
        video_id (str): ID of the video to set the thumbnail for
        path (str): Path of the file to upload

        Returns:
        dict: ???
        """
        url = f'{self._base_url}/{self._library_id}/videos/{video_id}/thumbnail'
        with open(path, 'rb') as f:
            r = requests.post(url, headers=self._headers, data=f)
            r.raise_for_status()
            return r.json()
    
    # TODO: TEST
    def fetch_video(self, video_id: str, video_url: str, fetch_headers=None) -> dict:
        """
        Fetch a video from a url
        
        Parameters:
        video_id (str): ID of the video to fetch.
        url (str): URL from where to fetch the video file.
        fetch_headers: The headers that will be sent together with the fetch request

        Returns:
        dict: HTTP status message
        """
        url = f'{self._base_url}/{self._library_id}/videos/{video_id}/fetch'
        payload = {'url' : video_url}
        if fetch_headers:
            payload.update(fetch_headers)
        r = requests.post(url, data=json.dumps(payload), headers=self._headers)
        r.raise_for_status()
        return r.json()
    
    # TODO: TEST
    def add_caption(self, video_id: str, srclang: str, label: str, captions_file: str) -> dict:
        """
        Add captions to a video

        Parameters:
        video_id (str): ID of the video to add captions to
        srclang (str): The unique srclang shortcode for the caption
        label (str): The text description label for the caption
        captions_file (str): Local path of captions file

        Returns:
        dict: HTTP status message
        """
        url = f'{self._base_url}/{self._library_id}/{video_id}/captions/{srclang}'
        with open(captions_file, 'rb') as f:
            data = f.read()
        payload = {
            'srclang' : srclang,
            'label' : label,
            'captionsFile' : data
        }
        r = requests.post(url, headers=self._headers, data=payload)
        r.raise_for_status()
        return r.json()
    
    def delete_caption(self, video_id: str, srclang: str) -> dict:
        """
        Remove a caption from a video

        Parameters:
        video_id (str): ID of the video to add captions to
        srclang (str): The unique srclang shortcode for the caption

        Returns:
        dict: HTTP status message
        """
        url = f'{self._base_url}/{self._library_id}/{video_id}/captions/{srclang}'
        r = requests.delete(url, headers=self._headers)
        r.raise_for_status()
        return r.json()
