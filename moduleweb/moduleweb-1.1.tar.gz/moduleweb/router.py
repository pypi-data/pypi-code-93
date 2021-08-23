########################################
# Project name: MEB | ModuleWeb [v1.1] #
# Code&Doc: > github.com/machnevegor   #
# Author's name:    | Link to VK/TG:   #
# > Machnev Egor    | > @machnev_egor  #
# Email: > egorikhelp@gmail.com        #
########################################

from aiohttp import web


class Router:
    """
    Description
    -----------
    A class that allows you to create a router
    instance for your asynchronous application.

    Methods
    -------
    middleware(self, middleware: object)
    error(self, middleware: object)
    get(self, route: str)
    post(self, route: str)
    """

    def __init__(self, options: list = []):
        """
        Expects
        -------
        :param options: (list, optional)
            List of add-ons that the router will have.
        """

        self._options = options
        self._middlewares = []
        self._routes = []

    def __repr__(self):
        """
        Description
        -----------
        A service method. Used to identify
        an instance of the router class.

        Expects
        -------
        Absolutely nothing, the method communicates
        only with an instance of the router class.

        Returns
        -------
        A string of data about an instance of the class.
        """

        return f"<WebRouter level={len(self._middlewares) + len(self._routes)}>"

    def middleware(self, middleware: object):
        """
        Description
        -----------
        Method for adding middleware to an
        instance of the router class.

        Expects
        -------
        :param middleware: (object)
            The middleware object that was
            wrapped by this decorator.

        Returns
        -------
        Absolutely nothing, the method changes the
        parameters inside the class instance itself.
        """

        self._middlewares.append({
            "type": "common",
            "middleware": middleware
        })

    def error(self, handler: object):
        """
        Description
        -----------
        A method that allows you to add a special
        middleware for handling application errors.

        Expects
        -------
        :param handler: (object)
            The handler that will be
            called when errors occur.

        Returns
        -------
        Absolutely nothing, the method changes the
        parameters inside the class instance itself.
        """

        self._middlewares.append({
            "type": "error",
            "handler": handler
        })

    def get(self, route: str):
        """
        Description
        -----------
        Method for adding a handler
        intended for get requests.

        Expects
        -------
        :param route: (str)
            The route to which the wrapped
            handler will be launched when
            using the get request.

        Returns
        -------
        Absolutely nothing, the method changes the
        parameters inside the class instance itself.
        """

        def decorator(handler: object):
            """
            Description
            -----------
            The decorator that will be used to get
            the handler and registered in the router.

            Expects
            -------
            :param handler: (object)
                The wrapped handler that will be called
                when following the passed route above.

            Returns
            -------
            Absolutely nothing, the method changes the
            parameters inside the class instance itself.
            """

            self._routes.append({
                "type": "get",
                "route": route,
                "handler": handler
            })

        return decorator

    def post(self, route: str):
        """
        Description
        -----------
        Method for adding a handler
        intended for post requests.

        Expects
        -------
        :param route: (str)
            The route to which the wrapped
            handler will be launched when
            using the post request.

        Returns
        -------
        Absolutely nothing, the method changes the
        parameters inside the class instance itself.
        """

        def decorator(handler: object):
            """
            Description
            -----------
            The decorator that will be used to get
            the handler and registered in the router.

            Expects
            -------
            :param handler: (object)
                The wrapped handler that will be called
                when following the passed route above.

            Returns
            -------
            Absolutely nothing, the method changes the
            parameters inside the class instance itself.
            """

            self._routes.append({
                "type": "post",
                "route": route,
                "handler": handler
            })

        return decorator

    def __common_middleware(self, common_middleware: object):
        """
        Description
        -----------
        A service method. Allows you to create a middleware
        of the standard type. This method works as a wrapper,
        so when using it, you don't have to call the second
        argument by the name handler.

        Expects
        -------
        :param common_middleware: (object)
            Middleware, which will be wrapped and
            in which in the future you can call the
            arguments of the function as you want.

        Returns
        -------
        The wrapper that will later call the main middleware.
        """

        @web.middleware
        async def middleware(request: object, handler: object):
            """
            Description
            -----------
            A service method. This wrapper is designed so that
            in the future you can call the second argument by
            a name that you can think of yourself.

            Expects
            -------
            :param request: (object)
                A request object intended for both handlers.
            :param handler: (object)
                The initial handler for the launch attempt.

            Returns
            -------
            Returns the result of the wrapped middleware.
            """

            return await common_middleware(request, handler)

        return middleware

    def __response_parser(self, handler: object):
        """
        Description
        -----------
        A service method. The method allows you to
        process response from handlers of various types.

        Expects
        -------
        :param handler: (object)
            The handler whose response will
            be processed in the future.

        Returns
        -------
        Processed response for further sending.
        """

        async def wrapper(request: object):
            response = await handler(request)
            if isinstance(response, object):
                if "WebRender" in str(response):
                    return response._convert_instance(request)
                elif "WebResponse" in str(response) or "WebRedirect" in str(response):
                    return response._convert_instance()
            return response

        return wrapper

    def __error_middleware(self, error_handler: object):
        """
        Description
        -----------
        A service method. A method that allows you to
        create a middleware that will be responsible
        for running the handler for errors.

        Expects
        -------
        :param error_handler: (object)
            The handler object that will
            be launched when errors occur.

        Returns
        -------
        Middleware that will work out to detect errors.
        """

        @web.middleware
        async def middleware(request: object, handler: object):
            """
            Description
            -----------
            A service method. Middleware that will work to
            detect errors in your asynchronous application.

            Expects
            -------
            :param request: (object)
                A request object intended for both handlers.
            :param handler: (object)
                The initial handler for the launch attempt.

            Returns
            -------
            First, there will be an attempt to return
            the result of the original handler, but if the
            attempt fails, the error handler will be called.
            """

            try:
                return await handler(request)
            except web.HTTPException as exc:
                if exc.status != 404:
                    raise
                return await error_handler(request)

        return middleware

    def __preroutes_searching(self):
        """
        Description
        -----------
        A service method. A method designed to search
        for all instances of the preroute class among
        the options of an instance of the router class.

        Expects
        -------
        Absolutely nothing, the method communicates
        only with an instance of the router class.

        Returns
        -------
        List of all preroute found in the
        options of the router class instance.
        """

        preroutes = []
        for option in self._options:
            if isinstance(option, object) and "RouterPreroute" in str(option):
                preroutes.append(option)
        return preroutes

    def __parse_route(self, route: str):
        """
        Description
        -----------
        A service method. A method designed to search
        for all instances of the preroute class among
        the options of an instance of the router class.

        Expects
        -------
        :param route: (str)
            A method that allows processing
            the transmitted route for the
            presence of preroute.

        Returns
        -------
        The route processed by this method.
        """

        if "__preroutes" not in dir(self):
            self.__preroutes = self.__preroutes_searching()
        for preroute in self.__preroutes:
            if route.startswith(preroute._briefly):
                return preroute._route + route[len(preroute._briefly):]
        return route

    def __templates_searching(self):
        """
        Description
        -----------
        A service method. A method designed to search
        for all instances of the template class among
        the options of an instance of the router class.

        Expects
        -------
        Absolutely nothing, the method communicates
        only with an instance of the router class.

        Returns
        -------
        List of all templates found in the
        options of the router class instance.
        """

        templates = []
        for option in self._options:
            if isinstance(option, object) and "RouterTemplate" in str(option):
                templates.append(option)
        return templates

    def _convert_instance(self, full_path: str):
        """
        Description
        -----------
        A service method. A method that allows you to
        convert all midvers, routes, and templates into a
        dictionary with arrays filled with aiohttp objects.

        Expects
        -------
        :param full_path: (str)
            The full path to this instance of the
            router class from the startup file.

        Returns
        -------
        A dictionary consisting of arrays
        filled with aiohttp objects.
        """

        middlewares = []
        for middleware in self._middlewares:
            if middleware["type"] == "common":
                middlewares.append(self.__common_middleware(middleware["middleware"]))
            elif middleware["type"] == "error":
                error_handler = self.__response_parser(middleware["handler"])
                middlewares.append(self.__error_middleware(error_handler))
        routes = []
        for route in self._routes:
            if route["type"] == "get":
                routes.append(web.get(
                    self.__parse_route(route["route"]),
                    self.__response_parser(route["handler"])
                ))
            elif route["type"] == "post":
                routes.append(web.get(
                    self.__parse_route(route["route"]),
                    self.__response_parser(route["handler"])
                ))
        templates = []
        for template in self.__templates_searching():
            templates.append(web.static("/" + template._name, full_path + template._folder))
        return {"middlewares": middlewares, "routes": routes, "templates": templates}


class Preroute:
    """
    Description
    -----------
    A service class. A class whose instance allows
    you to store data about the preroute, which you
    will pass in the parameters of the router class
    instance when it is initialized.
    """

    def __init__(self, route: str, briefly: str):
        """
        Expects
        -------
        :param route: (str)
            Route, which will be substituted later when
            the application is launched instead of briefly.
        :param briefly: (str)
            Briefly, which you can put at the very
            beginning of your route to further replace
            it with the route specified above.
        """

        self._route = route
        self._briefly = briefly

    def __repr__(self):
        """
        Description
        -----------
        A service method. Used to identify
        an instance of the preroute class.

        Expects
        -------
        Absolutely nothing, the method communicates
        only with an instance of the preroute class.

        Returns
        -------
        A string of data about an instance of the class.
        """

        return f"<RouterPreroute briefly={self._briefly}>"


def preroute(route: str, briefly: str = "~"):
    """
    Description
    -----------
    A function that allows you to get an instance
    of the preroute class, for further passing it
    to the router class instance options.

    Expects
    -------
    :param route: (str)
        Route, which will be substituted later when
        the application is launched instead of briefly.
    :param briefly: (str, optional)
        Briefly, which you can put at the very
        beginning of your route to further replace
        it with the route specified above.

    Returns
    -------
    An instance of your preroute class.
    """

    return Preroute(route, briefly)


class Template:
    """
    Description
    -----------
    A service class. A class whose instance allows
    you to store data about the template, which you
    will pass in the options of the router class
    instance when it is initialized.
    """

    def __init__(self, name: str, folder: str):
        """
        Expects
        -------
        :param name: (str)
            The name of the template that you will
            be able to access later when using rendering
            or already inside components, because the
            name is essentially a route.
        :param folder: (str)
            The folder where the template is located and
            to which the route corresponding to the name
            above will be available. If the folder with the
            template is located inside another folder deeper,
            then you need to specify the path relative to
            the instance of the router class.
        """

        self._name = name
        self._folder = folder

    def __repr__(self):
        """
        Description
        -----------
        A service method. Used to identify
        an instance of the template class.

        Expects
        -------
        Absolutely nothing, the method communicates
        only with an instance of the template class.

        Returns
        -------
        A string of data about an instance of the class.
        """

        return f"<RouterTemplate route=/{self._name}>"


def template(name: str, folder: str = "template"):
    """
    Description
    -----------
    A function that allows you to get an instance
    of the template class, for further passing it
    to the router class instance options.

    Expects
    -------
    :param name: (str)
        The name of the template that you will
        be able to access later when using rendering
        or already inside components, because the
        name is essentially a route.
    :param folder: (str, optional)
        The folder where the template is located and
        to which the route corresponding to the name
        above will be available. If the folder with the
        template is located inside another folder deeper,
        then you need to specify the path relative to
        the instance of the router class.

    Returns
    -------
    An instance of your template class.
    """

    return Template(name, folder)

########################################
# Project name: MEB | ModuleWeb [v1.1] #
# Code&Doc: > github.com/machnevegor   #
# Author's name:    | Link to VK/TG:   #
# > Machnev Egor    | > @machnev_egor  #
# Email: > egorikhelp@gmail.com        #
########################################
