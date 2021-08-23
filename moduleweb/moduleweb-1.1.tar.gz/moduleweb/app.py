########################################
# Project name: MEB | ModuleWeb [v1.1] #
# Code&Doc: > github.com/machnevegor   #
# Author's name:    | Link to VK/TG:   #
# > Machnev Egor    | > @machnev_egor  #
# Email: > egorikhelp@gmail.com        #
########################################

from aiohttp import web
from importlib import import_module
from jinja2 import FileSystemLoader, PrefixLoader
from aiohttp_jinja2 import setup


class App:
    """
    Description
    -----------
    A class that allows you to create a async
    application based on the aiohttp library,
    add various modules and statics to it,
    and run everything asynchronously.

    Methods
    -------
    add(self, instances: list)
    run(self, host: str = "localhost", port: int = 8000)
    """

    def __init__(self, root: str = "__main__"):
        """
        Expects
        -------
        :param root: (str, optional)
            If you are creating an instance of the
            application not in the main project
            file, then pass the __name__ variable
            during initialization.
        """

        self.app = web.Application()
        self._root = root.replace(".", "/") + "/" if root != "__main__" else ""
        self._functionality = []

    def __repr__(self):
        """
        Description
        -----------
        A service method. Used to identify an
        instance of the application class.

        Expects
        -------
        Absolutely nothing, the method communicates
        only with an instance of the application class.

        Returns
        -------
        A string of data about an instance of the class.
        """

        return f"<WebApplication level={len(self._functionality)}>"

    def add(self, instances: list):
        """
        Description
        -----------
        A method that allows you to add modules
        and statics to your application.

        Expects
        -------
        :param instances: (list)
            A list of module instances and statics. As a
            feature, you can consider the ability to add an
            instance of the router class if you write all the
            logic in one file, but be careful, because if you
            want to import a router from another file manually,
            errors will occur, so always try to use the modular
            architecture and the modular import method.

        Returns
        -------
        Absolutely nothing, the method changes the
        parameters inside the class instance itself.
        """

        for instance in instances:
            self._functionality.append(instance)

    def run(self, host: str = "localhost", port: int = 8000):
        """
        Description
        -----------
        A method that allows you to completely build
        your application and run it asynchronously.

        Expects
        -------
        :param host: (str, optional)
            The host on which you want to run
            your asynchronous application.
        :param port: (int, optional)
            The port on which you want to run
            your asynchronous application.

        Returns
        -------
        Absolutely nothing, the method changes the
        parameters inside the class instance itself.
        """

        prefixes_dict = {}
        for instance in self._functionality:
            converted_instance = instance._convert_instance(self._root)
            if "middlewares" in converted_instance:
                for middleware in converted_instance["middlewares"]:
                    self.app.middlewares.append(middleware)
            if "routes" in converted_instance:
                self.app.add_routes(converted_instance["routes"])
            if "templates" in converted_instance:
                self.app.add_routes(converted_instance["templates"])
                for template in converted_instance["templates"]:
                    prefixes_dict.update({
                        template.prefix[1:]: FileSystemLoader(template.path)
                    })
        setup(self.app, loader=PrefixLoader(prefixes_dict))
        web.run_app(self.app, host=host, port=port)


class Module:
    """
    Description
    -----------
    A service class. Allows you to store
    the path to the module, as well as the
    router of the same module.
    """

    def __init__(self, module_path: str, router: object):
        """
        Expects
        -------
        :param module_path: (str)
            The path to the module, relative to
            the application instance to which an
            instance of this class will be passed,
            namely the module instance.
        :param router: (object)
            An instance of the router located in the
            module that can be found by the passed path.
        """

        self._module_path = module_path + "/"
        self._router = router

    def __repr__(self):
        """
        Description
        -----------
        A service method. Used to identify
        an instance of the module class.

        Expects
        -------
        Absolutely nothing, the method communicates
        only with an instance of the module class.

        Returns
        -------
        A string of data about an instance of the class.
        """

        return f"<ApplicationModule path={self._module_path}>"

    def _convert_instance(self, app_path: str):
        """
        Description
        -----------
        A service method. Allows you to call
        the conversion of the router instance
        and return the result of this.

        Expects
        -------
        :param app_path: (str)
            The full path to the instance of the application
            class instance from the startup file.

        Returns
        -------
        The result of the router conversion.
        """

        return self._router._convert_instance(app_path + self._module_path)


def module(module_path: str, router_location: str = "view.router"):
    """
    Description
    -----------
    A function that allows you to import a module
    and all its components into your application.
    It is important that you can not simply import
    such a module using standard Python methods!

    Expects
    -------
    :param module_path: (str)
        The path to the module, relative to
        the instance of the application class.
    :param router_location: (str, optional)
        The location of the router inside
        the module you are importing.

    Returns
    -------
    An instance of your module class.
    """

    router_location = router_location.replace("/", ".")
    file_location = ".".join(router_location.split(".")[:-1])
    file_path = f"{module_path}.{file_location}".replace("/", ".")
    file_instance = import_module(file_path)
    router_name = router_location.split(".")[-1]
    router_instance = getattr(file_instance, router_name)
    return Module(module_path, router_instance)


class Static:
    """
    Description
    -----------
    A service class. Allows you to store
    the route and path of the statics that
    you want to add to your application.
    """

    def __init__(self, route: str, path: str):
        """
        Expects
        -------
        :param route: (str)
            The route where the static will be available.
        :param path: (str)
            The path to the folder for static relative to
            the instance of the application class.
        """

        self._route = route
        self._path = path

    def __repr__(self):
        """
        Description
        -----------
        A service method. Used to identify
        an instance of the static class.

        Expects
        -------
        Absolutely nothing, the method communicates
        only with an instance of the static class.

        Returns
        -------
        A string of data about an instance of the class.
        """

        return f"<ApplicationStatic route={self._route}>"

    def _convert_instance(self, app_path: str):
        """
        Description
        -----------
        A service method. The method allows you to
        convert this instance of the static class
        and get a dictionary that will contain an
        array with aiohttp objects of the static.

        Expects
        -------
        :param app_path: (str)
            The path of the application class instance
            location relative to the startup file.
            Required for further path concatenation.

        Returns
        -------
        A dictionary that will contain an array
        with static aiohttp objects.
        """

        return {"templates": [web.static(self._route, app_path + self._path)]}


def static(route: str, path: str):
    """
    Description
    -----------
    A function that allows you to add static
    to an instance of your application's class.

    Expects
    -------
    :param route: (str)
        The route where the static will be available.
    :param path: (str)
        The path to the folder for static relative to
        the instance of the application class.

    Returns
    -------
    An instance of your static class.
    """

    return Static(route, path)

########################################
# Project name: MEB | ModuleWeb [v1.1] #
# Code&Doc: > github.com/machnevegor   #
# Author's name:    | Link to VK/TG:   #
# > Machnev Egor    | > @machnev_egor  #
# Email: > egorikhelp@gmail.com        #
########################################
