
class modules_importer:

    def __init__(self, pipe):

        self.__project_path__ = pipe.get_path()


    def load_module(self, module_name):

        complete_path = f"{self.__project_path__}/tools/{module_name.replace('.', '/')}.py"
        self.__load_module__(complete_path)


    def __load_module__(self, complete_path):

        from importlib.util import spec_from_file_location, module_from_spec

        spec = spec_from_file_location("*", complete_path)
        self.module = module_from_spec(spec)
        spec.loader.exec_module(self.module)
