
import string
import random

from ruamel.yaml import YAML, yaml_object, add_representer
import io
import uuid


def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org,2002:null', '')


add_representer(type(None), represent_none)
yaml =YAML()
yaml.default_flow_style =None
yaml.preserve_quotes =True
yaml.allow_unicode =True


# create the class for the templates
@yaml_object(yaml)
class Template(object):

    yaml_tag =u'!Template'

    def __init__(self, *args, **kwargs):

        self.template_name =kwargs.get('template_name', None)
        self.template_id =kwargs.get('template_id', None)

        self.inherits_from =kwargs.get('inherits_from', None)

        self.content =kwargs.get('content', None)
        self.documentation =kwargs.get('documentation', None)
        self.units =kwargs.get('units', None)
        self.types =kwargs.get('types', None)

    def write(self, filename=None):
        if filename is not None:
            yaml.dump([self], open(filename, mode='w'))
        else:
            f =io.StringIO()
            yaml.dump([self], f)
            return f.getvalue()


class SimultanComponent(object):

    def __init__(self, *args, **kwargs):
        self.name =kwargs.get('name', (''.join(random.choice(string.ascii_lowercase) for i in range(10))))
        self.TYPE =kwargs.get('TYPE')

    def simultan_method(self):
        letters =string.ascii_lowercase
        print('simultan method to create random string called:')
        return self.name + (''.join(random.choice(letters) for i in range(10)))


def create_example_template():

    material_template =Template(template_name='Material',
                                 template_id='1',
                                 content=['c', 'w20', 'w80', 'lambda', 'mu', 'rho'],
                                 documentation='c: specific heat capacity in J/kg*K; ',
                                 units={'c': 'J/kg K',
                                        'w20': 'g/m=C2=B3',
                                        'w80': 'g/m=C2=B3',
                                        'lambda': 'W/mK',
                                        'mu': '-',
                                        'rho': 'kg/m=C2=B3'},
                                 types={'c': 'float',
                                        'w20': 'float',
                                        'w80': 'float',
                                        'lambda': 'float',
                                        'mu': 'float',
                                        'rho': 'float'}
                                 )

    layer_template =Template(template_name='Layer',
                              template_id='2',
                              content=['d', 'Material'],
                              documentation="d: thickness of the layer in m, Material: see Template 'Material'",
                              units={'d': 'm', 'Material': '-'},
                              types={'d': 'float'}
                              )

    layer_template2 =Template(inherits_from=layer_template,
                               template_name='Layer2',
                               template_id='2.1',
                               content=['d', 'Material'],
                               documentation="d: thickness of the layer in m, Material: see Template 'Material'",
                               units={'d': 'm', 'Material': '-'},
                               types={'d': 'int'}
                               )

    construction_template =Template(template_name='Construction',
                                     template_id='3',
                                     content=['layers'],
                                     documentation="layers: list of items with type 'Layer'",
                                     units={'layers': '-'}
                                     )

    return [material_template, layer_template, layer_template2, construction_template]


def load_templates(filename):
    with open(filename, mode='r') as f_obj:
        return yaml.load(f_obj)


def create_template_classes(templates):
    new_classes ={}

    for template in templates:

        # create new __init__ method for each class in the template
        def __new__init__(self, *args, **kwargs):
            for key in template.content:
                self.__setattibute__(key, kwargs.get(key, None))

        # as a example add the function python_spec_func to the classes:
        def python_spec_func(self, *args, **kwargs):
            print('python method called:')
            print(self.template_id, self.template_name)

        # check if the class inherits from another class, and if so take the parent class as base
        if template.inherits_from is not None:
            base =(new_classes[template.inherits_from.template_id], )
        else:
            base =(object, )

        # create the class from the template
        new_class =type(template.template_name, base, {'__init__': __new__init__,
                                                        'python_spec_func': python_spec_func,
                                                        'template_name': template.template_name,
                                                        'template_id': template.template_id})
        new_classes[template.template_id] =new_class

    return new_classes


def class_type_simultan_components(components, template_classes):

    # collect component classes in a dictionary:
    component_classes ={}

    # loop trough all components:
    for component in components:
        # get the template-id
        template_id =component.TYPE

        # check if the component class already exists:
        if template_id in component_classes.keys():     # if it already exists take it
            new_component_class =component_classes[template_id]
        else:   # create new component class
            # find the python template class:
            template_class =template_classes[template_id]

            # create a new component class which inherits from new_class and the class of the simultan-component
            new_component_class =type(template_class.__name__, (template_class, component.__class__, ), {})

            # add the new component class to collection
            component_classes[template_id] = new_component_class

        # type cast the component
        component.__class__ = new_component_class

    return components


def create_example_simultan_components(templates, n=5):

    simultan_components =[]

    for template in templates:
        for i in range(n):
            new_component = SimultanComponent(TYPE=template.template_id)

            if template.types is not None:
                # set random values for typed content:
                for key, c_type in template.types.items():
                    if c_type =='float':
                        value =random.random()
                    if c_type =='int':
                        value =random.randint(0, 100)

                    new_component.__setattr__(key, value)

            # add random attribute with random value:
            new_component.__setattr__(random.choice(string.ascii_lowercase), random.random())

            simultan_components.append(new_component)

    return simultan_components


if __name__ =='__main__':

    # create example templates
    templates =create_example_template()

    # write the example templates to a file:
    with open('example_templates.yml', mode='w') as f_obj:
        yaml.dump(templates, f_obj)

    # load the example templates:
    templates =load_templates('example_templates.yml')

    # create classes from the templates:
    template_classes =create_template_classes(templates)

    simultan_components =create_example_simultan_components(templates, n=5)

    simultan_components =class_type_simultan_components(simultan_components, template_classes)

    # the simultan components are now of the type which is defined in the templates
    print(simultan_components)

    # the class typed components still keep all methods and attributes from simultan:
    print(simultan_components[0].simultan_method())

    # and the class typed components have the new defined method python_spec_func:
    simultan_components[10].python_spec_func()
