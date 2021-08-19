import requests
import url

class AYBRequest():

    def __init__(self, prefix_url=None, *args, **kwargs):
        super(AYBRequest, self).__init__(*args, **kwargs)
        if prefix_url.endswith('/'):
            prefix_url = prefix_url[:-1]    
        self.prefix_url = prefix_url

    def get(self,url, params=None, **kwargs):
        return requests.get(url.urljoiner(self.prefix_url,url), params=params, **kwargs)


    def options(self,url, **kwargs):
        return requests.options(url.urljoiner(self.prefix_url,url), **kwargs)


    def head(self,url, **kwargs):
        kwargs.setdefault('allow_redirects', False)
        return requests.head(url.urljoiner(self.prefix_url,url), **kwargs)


    def post(self,url, data=None, json=None, **kwargs):
        return requests.post(url.urljoiner(self.prefix_url,url), data=data, json=json, **kwargs)


    def put(self,url, data=None, **kwargs):
        return requests.put(url.urljoiner(self.prefix_url,url), data=data, **kwargs)


    def patch(self,url, data=None, **kwargs):
        return requests.patch(url.urljoiner(self.prefix_url,url), data=data, **kwargs)


    def delete(self,url, **kwargs):
        return requests.delete(url.urljoiner(self.prefix_url,url), **kwargs)
    