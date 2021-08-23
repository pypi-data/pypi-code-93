########################################
# Project name: MEB | ModuleWeb [v1.1] #
# Code&Doc: > github.com/machnevegor   #
# Author's name:    | Link to VK/TG:   #
# > Machnev Egor    | > @machnev_egor  #
# Email: > egorikhelp@gmail.com        #
########################################

from typing import Union
from aiohttp import web
from aiohttp_jinja2 import render_template


class Response:
    """
    Description
    -----------
    A service class. The class whose instance is
    responsible for sending the response. This class
    is special because the router knows it.
    """

    def __init__(self, data: Union[str, dict]):
        """
        Expects
        -------
        :param data: (Union[str, dict])
            The data that you want to send as a
            response. It is important to know that
            if you pass a dictionary, the response
            is sent as a JSON object.
        """

        self._data = data

    def __repr__(self):
        """
        Description
        -----------
        A service method. Used to identify
        an instance of the response class.

        Expects
        -------
        Absolutely nothing, the method communicates
        only with an instance of the response class.

        Returns
        -------
        A string of data about an instance of the class.
        """

        return f"<WebResponse data={self._data}>"

    def _convert_instance(self):
        """
        Description
        -----------
        A service method. The method is called by the
        router itself. It is intended for converting this
        instance of the class into an aiohttp object.

        Expects
        -------
        Absolutely nothing, the method communicates
        only with an instance of the response class.

        Returns
        -------
        If data was originally a dictionary, then JSON
        will be returned in an aiohttp object, and if it
        is just a string, then an aiohttp string object.
        """

        if type(self._data) == dict:
            return web.json_response(self._data)
        return web.Response(text=str(self._data))


def response(data: Union[str, dict]):
    """
    Description
    -----------
    A function that allows you to create an
    instance of the response class for further
    return by the handler to the router.

    Expects
    -------
    :param data: (Union[str, dict])
        The data that you want to send as a
        response. It is important to know that
        if you pass a dictionary, the response
        is sent as a JSON object.

    Returns
    -------
    An instance of your response class.
    """

    return Response(data)


class Render:
    """
    Description
    -----------
    A service class. The class whose instance
    is responsible for rendering the template
    for the response. This class is special
    because the router knows it.
    """

    def __init__(self, entry_point: str, context: dict):
        """
        Expects
        -------
        :param entry_point: (str)
            The input point to start rendering the template. You need
            to specify the route to the starting template in the path
            format (without a slash at the beginning)! The template
            will generate thanks to jinja2 and aiohttp_jinja2.
        :param context: (dict)
            The context that will be passed to an instance
            of the template class for further rendering.
        """

        self._entry_point = entry_point
        self._context = context

    def __repr__(self):
        """
        Description
        -----------
        A service method. Used to identify
        an instance of the render class.

        Expects
        -------
        Absolutely nothing, the method communicates
        only with an instance of the render class.

        Returns
        -------
        A string of data about an instance of the class.
        """

        return f"<WebRender entry_point={self._entry_point}>"

    def _convert_instance(self, request: object):
        """
        Description
        -----------
        A service method. The method is called by the
        router itself. It is intended for rendering a
        template selected by an instance of the class.

        Expects
        -------
        :param request: (object)
            Request intended for rendering the template.

        Returns
        -------
        Rendered template using aiohttp_jinja2.
        """

        return render_template(self._entry_point, request, self._context)


def render(entry_point: str, context: dict = {}):
    """
    Description
    -----------
    A function that allows you to render a template
    selected in an instance of the render class for
    further return by the handler to the router.

    Expects
    -------
    :param entry_point: (str)
        The input point to start rendering the template. You need
        to specify the route to the starting template in the path
        format (without a slash at the beginning)! The template
        will generate thanks to jinja2 and aiohttp_jinja2.
    :param context: (dict, optional)
        The context that will be passed to an instance
        of the template class for further rendering.

    Returns
    -------
    An instance of your render class.
    """

    return Render(entry_point, context)


class Redirect:
    """
    Description
    -----------
    A service class. A class whose instance is
    responsible for redirecting to a specific route.
    This class is special because the router knows it.
    """

    def __init__(self, route: str):
        """
        Expects
        -------
        :param route: (str)
            The route to be redirected to.
        """

        self._route = route

    def __repr__(self):
        """
        Description
        -----------
        A service method. Used to identify
        an instance of the redirect class.

        Expects
        -------
        Absolutely nothing, the method communicates
        only with an instance of the redirect class.

        Returns
        -------
        A string of data about an instance of the class.
        """

        return f"<WebRedirect to={self._route}>"

    def _convert_instance(self):
        """
        Description
        -----------
        A service method. The method is called by the
        router itself. The service method. The method is
        called by the router itself. It is intended for
        redirection to a specified resource.

        Expects
        -------
        Absolutely nothing, the method communicates
        only with an instance of the redirect class.

        Returns
        -------
        Absolutely nothing, raise is called for redirection.
        """

        raise web.HTTPFound(self._route)


def redirect(route: str):
    """
    Description
    -----------
    A function that allows you to redirect to the route
    selected in an instance of the redirect class.

    Expects
    -------
    :param route: (str)
        The route to be redirected to.

    Returns
    -------
    An instance of your redirect class.
    """

    return Redirect(route)

########################################
# Project name: MEB | ModuleWeb [v1.1] #
# Code&Doc: > github.com/machnevegor   #
# Author's name:    | Link to VK/TG:   #
# > Machnev Egor    | > @machnev_egor  #
# Email: > egorikhelp@gmail.com        #
########################################
