import pandas, requests

urls = {
    'Auth': 'https://api.getsubsalt.com/v1/token',
    'Fetch': 'https://api.getsubsalt.com/v1/datasets'
}

class Client(object):
    def __init__(self, client_id=None, client_secret=None):
        if client_id is None:
            raise Exception('Must provide a client_id')

        if client_secret is None:
            raise Exception('Must provide a client_secret')

        self.access_token = None

        self.client_id = client_id
        self.client_secret = client_secret

    def _auth(self) -> None:
        resp = requests.post(urls['Auth'], {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        })

        if resp.ok:
            self.access_token = resp.json()['access_token']
        else:
            raise resp.raise_for_status()


    def get(self, model_id: str, limit: int = 100) -> pandas.DataFrame:
        if self.access_token is None:
            self._auth()
        
        url = '{}/{}?limit={}'.format(urls['Fetch'], model_id, limit)
        resp = requests.get(url, headers={
            'Authorization': 'Bearer %s'.format(self.access_token)
        })

        if resp.ok:
            return pandas.DataFrame(resp.json())
        else:
            raise resp.raise_for_status()