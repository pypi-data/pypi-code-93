import re

class Path:

    # Class to hold paths. makes it easier to check matches

    __slots__ = 'path', 'func', 'url_strict'

    def __init__(self, _path: str, _func, strict = False):
        self.path = _path
        self.func = _func
        self.url_strict = strict

    def match(self, _path):
        # function that is used to check whether a url route matches

        # _path request path
        # self.path route path

        #filter request path
        request_path = _path.split('/')
        
        request_path_params = []

        for x in request_path:
            if x == "":
                None
            else:
                request_path_params.append(x)
        

        #filter route path
        route_path = self.path.split('/')   

        route_path_params = []

        for y in route_path:
            if y == "":
                None
            else:
                route_path_params.append(y)
        
        # print(request_path_params, route_path_params)

        # matching
        c_bool = True
        params = []
        if len(request_path_params) == len(route_path_params):
            t_c_i = 0 
            for y in route_path_params:
                if c_bool == True:
                    if self.url_strict == False and re.match(r"" + y + "$", request_path_params[t_c_i], re.I) is not None:
                        None
                    elif y == request_path_params[t_c_i]:
                        None
                    elif y == "^":
                        params.append(request_path_params[t_c_i])
                        None
                    else:
                        c_bool = False
                t_c_i = t_c_i + 1
        else:
            c_bool = False

        if c_bool == False:
            if len(route_path_params) == 1:
                if route_path_params[0] == "__error__" or route_path_params[0] == "__404__":
                    c_bool = True

        return c_bool, params


class Router:
    
    # Holds all routes in a list. When connection comes it is used to check which of those paths match the url

    __slots__ = 'routes'

    def __init__(self, routes: list = None):
        self.routes: list = list(routes) if routes else []

    def add_route(self,  _path: Path):
        self.routes.append(_path)
        return True

    def get_route(self, path_):
        for path in self.routes:
            
            pass_bool, params = path.match(path_)

            if pass_bool:  # we let the paths themselves check if they match url
                return path.func, params
