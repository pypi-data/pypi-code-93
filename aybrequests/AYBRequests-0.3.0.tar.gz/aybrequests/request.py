import requests

class AYBRequest():

    def urljoiner(self,url):
        result = self.prefix_url
        if not url.beginswith('/'):
            result+='/'
        result+=url
        return 


    def __init__(self, prefix_url=None, *args, **kwargs):
        super(AYBRequest, self).__init__(*args, **kwargs)
        if prefix_url.endswith('/'):
            prefix_url = prefix_url[:-1]    
        self.prefix_url = prefix_url

    def get(self,url, params=None, **kwargs):
        return requests.get(self.urljoiner(url), params=params, **kwargs)


    def options(self,url, **kwargs):
        return requests.options(self.urljoiner(url), **kwargs)


    def head(self,url, **kwargs):
        kwargs.setdefault('allow_redirects', False)
        return requests.head(self.urljoiner(url), **kwargs)


    def post(self,url, data=None, json=None, **kwargs):
        return requests.post(self.urljoiner(url), data=data, json=json, **kwargs)


    def put(self,url, data=None, **kwargs):
        return requests.put(self.urljoiner(url), data=data, **kwargs)


    def patch(self,url, data=None, **kwargs):
        return requests.patch(self.urljoiner(url), data=data, **kwargs)


    def delete(self,url, **kwargs):
        return requests.delete(self.urljoiner(url), **kwargs)
    