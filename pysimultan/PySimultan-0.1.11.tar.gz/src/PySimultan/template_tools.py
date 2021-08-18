from ruamel.yaml import YAML, yaml_object, add_representer
from .config import yaml
import io
import colorlog
from uuid import uuid4

from collections import UserList
from .default_types import SimultanObject
from .default_types import List as SimultanList
from .default_types import ValueField, BuildInFace, BuildInVolume, BuildInZone
from .geo_default_types import geometry_types
from .geometry import GeometryModel

from functools import lru_cache

from ParameterStructure.Values import SimMultiValuePointer


logger = colorlog.getLogger('PySimultan')


template_classes = {}


# create the class for the templates
@yaml_object(yaml)
class Template(object):

    yaml_tag = u'!Template'

    def __init__(self, *args, **kwargs):
        """ Template class to define how SIMULTAN components are imported and parsed

        :param args:
        :param kwargs:

        @keyword template_name: Name of the Template. This name is the name of the created Python class and used for
        TYPE matching the SIMULTAN component
        @keyword template_id: ID of the template; int
        @keyword inherits_from: name of the python template or the template instance this template inherits from
        @keyword content: List of attribute names
        @keyword documentation: Entry to document the template; str
        @keyword units: units of the content. Dictionary
        @keyword types: Dictionary with the type of the content. if the type is 'str' get_TextValue() is returned, param.get_ValueCurrent() otherwise
        @keyword slots:

        """

        self.template_name = kwargs.get('template_name', None)
        self.template_id = kwargs.get('template_id', None)

        self.inherits_from = kwargs.get('inherits_from', None)

        self.content = kwargs.get('content', None)
        self.documentation = kwargs.get('documentation', None)
        self.units = kwargs.get('units', None)
        self.types = kwargs.get('types', None)

        self.slots = kwargs.get('slots', {})
        self.synonyms = kwargs.get('synonyms', {})      # name of the attribute in the python class

        self.template_parser = kwargs.get('template_parser', None)
        self.template_class = kwargs.get('template_class', None)

    def write(self, filename=None):
        """
        write the template as .yml to a file
        :param filename: name and path of the file to save
        :return: None
        """
        if filename is not None:
            yaml.dump([self], open(filename, mode='w'))
        else:
            f = io.StringIO()
            yaml.dump([self], f)
            return f.getvalue()

    def create_template_class(self, template_parser, template_classes):
        """
        Creates a template class for this template.
        :param template_parser: TemplateParser instance
        :param template_classes: list of template classes to inherit from (e.g. default classes)
        :return: TemplateClass
        """

        if (self.template_parser is template_parser) and (self.template_class is not None):
            return self.template_class

        self.template_parser = template_parser

        # for inheritance:
        # template classes must inherit from SimultanObject, UserList or ValueField

        if self.inherits_from is not None:
            if self.inherits_from in self.template_parser.bases.keys():
                base = template_classes[self.inherits_from]

                simultan_base_list = [SimultanObject, UserList, ValueField]

                if any(x in simultan_base_list for x in base.__bases__):
                    bases = (base, )
                else:
                    bases = (SimultanObject, ) + (base, )
                    # bases = (base, ) + (SimultanObject, )

                # if SimultanObject in base.__bases__:
                #     bases = (base, )
                # elif UserList in base.__bases__:
                #     bases = (base, )
                # elif ValueField in base.__bases__:
                #     bases = (base, )
                # else:
                #     bases = (SimultanObject, ) + (base, )
            else:
                base = template_classes[self.inherits_from.template_name]
                bases = (base, )

            def new_init(self, *args, **kwargs):

                for i in range(self.__class__.__bases__.__len__()):
                    self.__class__.__bases__[i].__init__(self, *args, **kwargs)

        else:
            bases = (SimultanObject, )
            # create the class from the template

            def new_init(self, *args, **kwargs):

                self.__class__.__bases__[0].__init__(self, *args, **kwargs)

        new_class_dict = {'__init__': new_init,
                          '_template_name': self.template_name,
                          '_template_id': self.template_id,
                          '_documentation': self.documentation,
                          '_content': [cont for cont in self.content],
                          '_types': self.types,
                          '_units': self.units,
                          '_base': bases,
                          '_template_parser': self,
                          '_slots': self.slots}

        new_class_dict.update(self.get_properties())
        new_class = type(self.template_name, bases, new_class_dict)

        self.template_class = new_class

        return new_class

    def get_properties(self):

        prop_dict = {}

        for prop in self.content:

            syn = self.synonyms.get('prop', prop)

            prop_dict[syn] = add_properties(prop, type=self.types.get(prop, None))

        return prop_dict

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['template_parser']
        del state['template_class']
        return state

    def __setstate__(self, d):
        self.__dict__ = d
        self.template_parser = None
        self.template_class = None

    def __repr__(self):
        return f"Template '{self.template_name}': " + object.__repr__(self)


class TemplateParser(object):

    bases = {'Liste': SimultanList,
             'List': SimultanList,
             'ValueField': ValueField,
             'Geometric Area': BuildInFace,
             'Geometrische_Flächen': BuildInFace,
             'Geometric Volume': BuildInVolume,
             'Geometrische_Volumina': BuildInVolume,
             'BuildInZone': BuildInZone}

    geo_bases = {'base': geometry_types.base,
                 'layer': geometry_types.layer,
                 'vertex': geometry_types.vertex,
                 'edge': geometry_types.edge,
                 'edge_loop': geometry_types.edge_loop,
                 'face': geometry_types.face,
                 'volume': geometry_types.volume,
                 }

    _create_all = False

    def __init__(self, *args, **kwargs):

        """
        Class which handles templates. This class generates python objects from the SIMULTAN data model for templates.

        @keyword templates: list of templates; if templates is None and template_filepath is defined,
        templates are automatically loaded
        @keyword template_filepath: filepath to the template (*.yml)

        """

        self.id = uuid4()

        self._templates = kwargs.get('templates', None)
        self.template_filepath = kwargs.get('template_filepath', None)

        self._template_classes = kwargs.get('template_classes', None)
        self._current_data_model = kwargs.get('current_data_model', None)

        self.data_models = kwargs.get('data_models', {})

        self._typed_geo_models = None

        template_classes[self.id] = self._template_classes

    @property
    def current_data_model(self):
        return self._current_data_model

    @current_data_model.setter
    def current_data_model(self, value):
        self._current_data_model = value
        if self._current_data_model not in self.data_models:
            self.data_models[self._current_data_model.id] = self._current_data_model

    @property
    def templates(self):
        if self.template_filepath is None:
            return None

        if self._templates is None:
            self._templates = self.load_templates_from_file()
        return self._templates

    @property
    def template_classes(self):
        if self._template_classes is None:
            self.create_template_classes()
        return self._template_classes

    @property
    def typed_geo_models(self):
        if self._typed_geo_models is None:
            self._typed_geo_models = self.get_typed_geo_models()
        return self._typed_geo_models

    def get_model_by_file_id(self, id):
        return self.current_data_model.models_dict[id]

    def get_typed_model_by_file_id(self, id):
        return self.typed_geo_models[id]

    def load_templates_from_file(self, filepath=None):
        """
        Load templates from file
        :param filepath: filepath of the file (str)
        :return: templates; list of templates
        """
        if filepath is None:
            filepath = self.template_filepath

        with open(filepath, mode='r', encoding="utf-8") as f_obj:
            templates = yaml.load(f_obj)

        return templates

    def create_template_classes(self):

        template_classes = {**self.bases}

        logger.info('\n\nCreating template-classes:\n-------------------------------------')
        logger.info(f'found {self.templates.__len__()} templates')

        for template in self.templates:

            new_class = template.create_template_class(self, template_classes)
            template_classes[template.template_name] = new_class

            logger.info(f'Created template class {template.template_name}. Inherits from {template.inherits_from}')

        self._template_classes = template_classes
        logger.info('template-class creation finished\n\n')

    @lru_cache(maxsize=None)
    def create_python_object(self, component):

        # get the template or slot
        template_name = None
        if hasattr(component, 'ContainedParameters'):
            template_name = next((x.TextValue for x in component.ContainedParameters.Items if x.Name == 'TYPE'), None)

        if (template_name is None) and (hasattr(component, 'get_CurrentSlot')):
            template_name = component.FitsInSlots[0]

        # if no template and no slot could be found return the plain component

        if template_name is None:
            if isinstance(component, SimMultiValuePointer):
                template_name = 'ValueField'

        if template_name is None:
            if self._create_all:
                if hasattr(component, 'ContainedComponentsAsList'):
                    _ = [self.create_python_object(x) for x in component.ContainedComponentsAsList]
                if hasattr(component, 'ReferencedComponents'):
                    _ = [self.create_python_object(x) for x in component.ReferencedComponents.Items]
            return component

        if template_name not in self.template_classes.keys():

            # create new class for the template / slot
            base = SimultanObject
            bases = (base, )

            def new__init(self, *args, **kwargs):
                self.__class__.__bases__[0].__init__(self, *args, **kwargs)

            new_class_dict = {'__init__': new__init,
                              '_template_name': template_name,
                              '_template_id': None,
                              '_documentation': None,
                              '_content': None,
                              '_types': None,
                              '_units': None,
                              '_base': bases,
                              '_template_parser': self,
                              '_slots': {}}

            new_class = type(template_name, bases, new_class_dict)
            self.template_classes[template_name] = new_class

        template_class = self.template_classes[template_name]

        # init new instance
        template_class._template_parser = self
        new_instance = template_class(wrapped_obj=component,
                                      template_parser=self,
                                      data_model_id=self._current_data_model.id)

        # new_instance._template_parser = self
        return new_instance

    def get_typed_geo_models(self):
        typed_models_dict = {}
        for key, model in self.current_data_model.models_dict.items():
            if model is None:
                typed_models_dict[key] = None
                continue
            typed_models_dict[key] = GeometryModel(wrapped_obj=model,
                                                   geo_types=self.geo_bases)
            # models.append(GeometryModel(wrapped_obj=model))
        return typed_models_dict


def add_properties(prop, type):
    """
    create property for a class
    :param prop: name of the property (str)
    :param type: type of the property; if type == 'str': param.get_TextValue(); else: param.get_ValueCurrent() is returned
    :return: property
    """

    @lru_cache()
    def getx(self):

        obj = None

        idx = next((i for i, x in enumerate(self._wrapped_obj.ContainedParameters.Items) if x.Name == prop), None)
        if idx is not None:
            param = self._wrapped_obj.ContainedParameters.Items[idx]
            obj = param.get_MultiValuePointer()

            if obj is None:
                if type == 'str':
                    obj = param.get_TextValue()
                    # obj = next((x.get_TextValue() for x in self._wrapped_obj.ContainedParameters.Items if x.Name == prop), None)
                else:
                    obj = param.get_ValueCurrent()
                    # obj = next((x.get_ValueCurrent() for x in self._wrapped_obj.ContainedParameters.Items if x.Name == prop), None)

        if obj is None:
            slot = self._slots.get(prop, None)
            if slot is not None:
                obj = next((x for x in self._wrapped_obj.ContainedComponentsAsList if x.get_CurrentSlot() == slot), None)
                if obj is None:
                    obj = next((x.Reference for x in self._wrapped_obj.ReferencedComponents.Items if x.ReferenceFunction.SlotFull == slot), None)

        return self._template_parser.create_python_object(obj)

    def setx(self, value):
        getx.cache_clear()
        return next((x.set_ValueCurrent(value) for x in self._wrapped_obj.ContainedParameters.Items if x.Name == prop), None)

    def delx(self):
        logger.warning('delete method not implemented')

    return property(getx, setx, delx, f"automatic created property")


# def new_getattr(self, attr):
#     try:
#         return object.__getattribute__(self, attr)
#     except KeyError:
#         wrapped = object.__getattribute__(self, '_wrapped_obj')
#         if wrapped is not None:
#             return object.__getattribute__(wrapped, attr)
#         else:
#             raise KeyError
#
#
# def new_setattr(self, attr, value):
#     if (attr in self.__dict__) or (attr in ['_wrapped_obj', '_contained_components', '_contained_parameters']):
#         object.__setattr__(self, attr, value)
#     else:
#         object.__setattr__(self._wrapped_obj, attr, value)
