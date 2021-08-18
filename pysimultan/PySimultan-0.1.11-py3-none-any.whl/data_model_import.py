import colorlog
import atexit
from uuid import uuid4
from functools import lru_cache

from .SIMULTAN.Project.Services import *
from .SIMULTAN.Project.ProjectData import *
from .SIMULTAN.Project.ProjectLoaders import *
from .SIMULTAN.UI.Services import *
from .SIMULTAN.DataExchange import *
from .ParameterStructure.Component import ComponentManagerType
from .ParameterStructure.Users import *
from .GeometryViewer import *
from .GeometryViewer.Service import *
from .GeometryViewer.Model import *
from .GeometryViewer.IO import *
from System.Security import SecureString
from System.IO import FileInfo

# from .utils import *
# from .geo_default_types import *

from .geometry import GeometryModel


logger = colorlog.getLogger('PySimultan')


class IAuthenticationServiceNew(IAuthenticationService):
    __namespace__ = "authenticate_namespace"

    def Authenticate(self, user_manager, project_file):
        user_name = 'admin'
        password = 'admin'

        sec_str = SecureString()
        for char in password:
            sec_str.AppendChar(char)

        user = user_manager.Authenticate(user_name, sec_str)

        user_manager.CurrentUser = user.Item1
        user_manager.EncryptionKey = user.Item2

        return user.Item1


class DataModel:

    def __init__(self, *args, **kwargs):

        atexit.register(self.cleanup)

        self.id = uuid4()
        self.data = None
        self._project_data_manager = None
        self._user = None
        self._project = None
        self._zip_loader = None

        self.project_path = kwargs.get('project_path', None)
        # self.user = kwargs.get('user', ComponentManagerType.ADMINISTRATOR)

        self.service_provider = ServicesProvider()
        self.get_service_provider().AddService[IAuthenticationService](IAuthenticationServiceNew())
        # self.zip_loader = ZipProjectIO(self.service_provider)

        _ = self.project

        # self.project = self.zip_loader.Load(FileInfo(self.project_path), self.project_data_manager)

        # self.zip_loader.AuthenticateUserAfterLoading(self.project, self.project_data_manager,
        #                                              bytearray('ThWmZq4t6w9z$C&F', 'ascii'))
        # self.zip_loader.OpenAfterAuthentication(self.project, self.project_data_manager)

        self.serv = GeometryViewerService([], self.service_provider)

        self.exch = ComponentGeometryExchange(self.project_data_manager.ComponentAndNetworkManager)
        self.exch.ModelStore = self.serv
        self.inst = TemporaryGeometryViewerInstance(self.exch)

        # replace 0 with the id of the file from GeoIDs (x value)
        # self.resources = [None] * self.project_data_manager.AssetManager.Resources.__len__()
        self.resources = {}
        # self.models = [None] * self.project_data_manager.AssetManager.Resources.__len__()
        self.models_dict = {}

        if self.project_data_manager.AssetManager.Resources.__len__() > 0:
            for resource in self.project_data_manager.AssetManager.Resources:
                # resource = self.project_data_manager.AssetManager.Resources.get_Item(i)
                if resource is None:
                    continue
                self.resources[resource.Key] = resource
                self.models_dict[resource.Key] = None
                current_full_path = resource.CurrentFullPath
                if current_full_path == '?':
                    continue

                file_info = FileInfo(resource.CurrentFullPath)
                if file_info.Extension == '.simgeo':
                    model = SimGeoIO.Load(file_info, self.inst, self.serv)
                    self.models_dict[resource.Key] = model
                    self.serv.AddGeometryModel(model)

        self.ValueFields = self.project_data_manager.ValueManager.Items
        self.import_data_model()

        # self._typed_geo_models = None

    @property
    def models(self):
        return self.models_dict.values()

    @property
    def project_data_manager(self):
        if (self._project_data_manager) is None and (self.user is not None):
            self._project_data_manager = ProjectDataManager(self.user)
        return self._project_data_manager

    @project_data_manager.setter
    def project_data_manager(self, value):
        self._project_data_manager = value

    @property
    def user(self):
        if self._user is None:
            self._user = ComponentManagerType.ADMINISTRATOR
        return self._user

    @user.setter
    def user(self, value):
        if value != self._user:
            self.project_data_manager = None
            self._project = None
        self._user = value

    @property
    def project(self):
        if (self._project is None) and (self.project_path is not None) and (self.project_data_manager is not None):
            logger.debug('loading project')
            self._project = self.zip_loader.Load(FileInfo(self.project_path), self.project_data_manager)
            self.zip_loader.AuthenticateUserAfterLoading(self.project, self.project_data_manager,
                                                         bytearray('ThWmZq4t6w9z$C&F', 'ascii'))
            self.zip_loader.OpenAfterAuthentication(self.project, self.project_data_manager)
            logger.debug('project loaded successfull')
        return self._project

    @project.setter
    def project(self, value):
        self._project = value

    @property
    def zip_loader(self):
        if self._zip_loader is None:
            self._zip_loader = ZipProjectIO(self.service_provider)
        return self._zip_loader

    @zip_loader.setter
    def zip_loader(self, value):
        self._zip_loader = value

    # @property
    # def typed_geo_models(self):
    #     if self._typed_geo_models is None:
    #         self._typed_geo_models = self.get_typed_geo_models()
    #     return self._typed_geo_models

    def set_user(self, user=''):
        # TODO generalize
        self.user = ComponentManagerType.ADMINISTRATOR

    def get_service_provider(self):
        return self.service_provider

    def get_zip_loader(self):
        return self.zip_loader

    def get_typed_data(self, template_parser, create_all=False):

        template_parser._create_all = create_all
        template_parser.current_data_model = self

        for cls in template_parser.template_classes.values():
            if create_all:
                cls._create_all = True
            else:
                cls._create_all = False

        data = []

        for item in self.data.Items:
            logger.info(f'Creating python object for: {item.Name}')

            data.append(template_parser.create_python_object(item))

        logger.info('\n\nType info: \n----------------------------------')
        logger.info(f'created {data.__len__()} top level instances')
        for cls in set(template_parser.template_classes.values()):
            if hasattr(cls, 'cls_instances'):
                logger.info(f'created {cls.cls_instances.__len__()} instances of type {cls.__name__}')
        return data

    def import_data_model(self):
        self.data = self.project_data_manager.ComponentAndNetworkManager.ComponentRecord
        return self.data

    # def get_model_by_file_id(self, id):
    #     return self.models_dict[id]
    #
    # def get_typed_model_by_file_id(self, id):
    #     return self.typed_geo_models[id]

    @lru_cache(maxsize=None)
    def get_geo_instance(self, file_id, type, id):
        geo_model = self.models[file_id]
        objects = getattr(geo_model.Geometry, type)

        return next((x for x in objects.Items if x.Id == id), None)

    # def get_typed_geo_models(self):
    #     typed_models_dict = {}
    #     for key, model in self.models_dict.items():
    #         if model is None:
    #             typed_models_dict[key] = None
    #             continue
    #         typed_models_dict[key] = GeometryModel(wrapped_obj=model)
    #         # models.append(GeometryModel(wrapped_obj=model))
    #     return typed_models_dict

    def save(self):
        # https://github.com/bph-tuwien/SIMULTAN/blob/master/EngineTest/Apps/ComponentBuilder/ViewNEW/MainWindowContent/SaveProjectVM.cs
        self.zip_loader.Save(self.project, False)

    def cleanup(self):
        logger.info('closing project...')
        if (self._zip_loader is not None) and self._project is not None:
            self._zip_loader.Close(self._project, False, True)


# if __name__ == '__main__':
#
#     # create example templates
#     templates = create_example_template_bim_bestand_network()
#
#     # write the example templates to a file:
#     with open('example_templates.yml', mode='w') as f_obj:
#         yaml.dump(templates, f_obj)
#
#     # load the example templates:
#     templates = load_templates('example_templates.yml')
#
#     # create classes from the templates:
#     template_classes = create_template_classes(templates)
#
#     simultan_components = create_example_simultan_components(templates, n=5)
#
#     simultan_components = class_type_simultan_components(simultan_components, template_classes)
#
#     # the simultan components are now of the type which is defined in the templates
#     print(simultan_components)
#
#     # the class typed components still keep all methods and attributes from simultan:
#     print(simultan_components[0].simultan_method())
#
#     # and the class typed components have the new defined method python_spec_func:
#     simultan_components[10].python_spec_func()
