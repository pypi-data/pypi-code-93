#filter request function

import cgi
import urllib.parse

def bodyParser(request):
    data = {}
    
    if request.method != "POST":
        return data
   
    environ = request.environ
   
    field_storage = cgi.FieldStorage(
        fp=environ['wsgi.input'],
        environ=environ,
        keep_blank_values=True
    )

    for item in field_storage.list:
        if not item.filename:
            data[item.name] = item.value
        else:
            data[item.name] = item
    
    return data

def cookiesParser(request):
    cookies = {}
    if request.cookies is not None:
        for cp in request.cookies.split("; "):
            c = cp.split("=")
            if len(c) == 2:
                if c[1] == None or c[1] == '':
                    cookies[c[0]] = None
                else:
                    cookies[c[0]] = c[1]
            else:
                cookies[c[0]] = None
    return cookies

def queryParser(request):
    query = {}
    for qp in urllib.parse.unquote(request.query_string).split("&"):        
        q = qp.split("=")
        if len(q) == 2:
            query[q[0]] = q[1]
        else:
            query[q[0]] = None
    return query
