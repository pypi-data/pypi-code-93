from requests import Session
import url

class AYBSession(Session):

    def __init__(self, prefix_url=None, *args, **kwargs):
        super(AYBSession, self).__init__(*args, **kwargs)
        if prefix_url.endswith('/'):
            prefix_url = prefix_url[:-1]    
        self.prefix_url = prefix_url

    def request(self, method, url, *args, **kwargs):
        url = url.urljoiner(self.prefix_url,url)
        return super(AYBSession, self).request(method, url, *args, **kwargs)