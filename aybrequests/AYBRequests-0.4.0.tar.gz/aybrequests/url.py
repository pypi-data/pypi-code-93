def urljoiner(prefix_url,url):
    result = prefix_url
    if not url.startswith('/'):
        result+='/'
    result+=url
    return result