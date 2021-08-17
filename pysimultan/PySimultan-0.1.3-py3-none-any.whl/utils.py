from .template_tools import Template
from .config import yaml


class SimultanComponent(object):

    def __init__(self, *args, **kwargs):
        self.data = list(kwargs.get('data'))
        self.component_list = set()
        self.typed_component_list = set()

        self.get_component_list(self.data, self.data[0])
        self.get_typed_component_list()

    def get_component_list(self, components, component):
        if component not in self.typed_component_list:
            self.component_list.add(component)

            component_list = component.ContainedComponentsAsList
            for neighbour in component_list:
                self.get_component_list(component_list, neighbour)

    def get_typed_component_list(self):
        for component in self.component_list:
            for param in component.ContainedParameters.Items:
                if param.Name == 'TYPE':
                    self.typed_component_list.add(component)

    #
    # def dfs(self, visited, components, component):
    #     if component not in visited:
    #         print(component)
    #         visited.add(component)
    #         component_list = component.ContainedComponentsAsList
    #         for neighbour in component_list:
    #             dfs(visited, component_list, neighbour)
    #
    # def visit_components_list(self, visited, components, component, typed_component_list=[]):
    #     if component not in visited:
    #         visited.add(component)
    #
    #         for neighbour in components:
    #             if neighbour.ContainedParameters:
    #                 print('PARAMS')
    #                 print(neighbour.ContainedParameters)
    #                 for el in component.ContainedParameters:
    #                     if el.Name == 'TYPE':
    #                         print('TYPE')
    #                         print(el)
    #                         typed_component_list.append(neighbour)
    #             if neighbour.ContainedComponentsAsList:
    #                 print('LIST')
    #                 print(neighbour.ContainedComponentsAsList)
    #                 visit_components_list(component.ContainedComponentsAsList, neighbour, typed_component_list)
    #
    # def get_flat_list(self, visited, component_list, component):
    #     if component not in visited:
    #         visited.add(component)
    #         component_list = component.ContainedComponentsAsList
    #         for neighbour in component_list:
    #             dfs(visited, component_list, neighbour)
    #
    #     if not component_list:
    #         return []
    #     for comp in component_list:
    #         flat_list.append(comp)
    #         return (get_flat_list((comp.ContainedComponentsAsList, flat_list)))


def create_example_template():

    material_template = Template(template_name='Material',
                                 template_id='1',
                                 content=['c', 'w20', 'w80', 'lambda', 'mu', 'rho'],
                                 documentation='c: specific heat = capacity in J/kg*K; ',
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

    layer_template = Template(template_name='Layer',
                              template_id='2',
                              content=['d', 'Material'],
                              documentation="d: thickness of the layer = in m, Material: see Template 'Material'",
                              units={'d': 'm', 'Material': '-'},
                              types={'d': 'float'}
                              )

    layer_template2 = Template(inherits_from=layer_template,
                               template_name='Layer2',
                               template_id='2.1',
                               content=['d', 'Material'],
                               documentation="d: thickness of the = layer in m, Material: see Template 'Material'",
                               units={'d': 'm', 'Material': '-'},
                               types={'d': 'int'}
                               )

    construction_template = Template(template_name='Construction',
                                     template_id='3',
                                     content=['layers'],
                                     documentation="layers: list of = items with type 'Layer'",
                                     units={'layers': '-'}
                                     )

    return [material_template, layer_template, layer_template2, construction_template]


def create_example_template_bim_bestand_network():

    component_template = Template(template_name='Component',
                                  template_id=1,
                                  content=['AKS-Id', 'Loss Factor'],
                                  documentation='c: specific heat = capacity in J/kg*K;',
                                  units={'AKS-Id': 'J/kg K',
                                         'Loss Factor': 'g/m=C2=B3'},
                                  types={'AKS-Id': 'int',
                                         'Loss Factor': 'float'}
                                  )

    material_template = Template(template_name='Material',
                                 template_id='1',
                                 content=['c', 'w20', 'w80', 'lambda', 'mu', 'rho'],
                                 documentation='c: specific heat = capacity in J/kg*K; ',
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

    edge_template = Template(inherits_from=component_template,
                             template_name='Edge',
                             template_id='2',
                             content=['Start-ID', 'End-ID', 'COMPONENT-ID', 'COMPONENT-TYPE', 'Length', 'Lambda', 'K'],
                             documentation="d: thickness of the layer = in m, Material: see Template 'Material'",
                             units={'d': 'm', 'Material': '-'},
                             types={'d': 'float'}
                             )

    confuser_diffuser_rectangular_template = Template(inherits_from=edge_template,
                                                      template_name='CONFUSERDIFFUSERRECTANGULAR',
                                                      template_id='2.1',
                                                      content=['EndHight', 'EndWidth', 'StartHight', 'StartWidth'],
                                                      documentation="d: thickness of the = layer in m, Material: see Template 'Material'",
                                                      units={'d': 'm', 'Material': '-'},
                                                      types={'d': 'int'}
                                                      )

    confuser_diffuser_round_template = Template(inherits_from=edge_template,
                                                template_name='CONFUSERDIFFUSERROUND',
                                                template_id='3',
                                                content=['EndDiameter', 'StartDiameter'],
                                                documentation="layers: list of = items with type 'Layer'",
                                                units={'layers': '-'}
                                                )

    return [component_template, material_template, edge_template, confuser_diffuser_rectangular_template, confuser_diffuser_round_template]


def class_type_simultan_components(components, template_classes):

    # collect component classes in a dictionary:
    component_classes = {}

    # loop trough all components:
    for component in components:
        # get the template-id
        template_name = None
        for comp_type in component.ContainedParameters.Items:
            if comp_type.Name == 'TYPE':
                template_name = comp_type.TextValue

        # check if the component class already exists:
        if template_name in component_classes.keys():     # if it already = exists take it
            new_component_class_dict = component_classes[template_name]
        elif template_name in template_classes.keys():   # create new component class
            # find the python template class:
            template_class = template_classes[template_name]

            # init new instance
            new_instance = template_class(wrapped_obj=component)

            print(new_instance)


    return components


def create_example_simultan_components(templates, flat_list_components):

    simultan_components = []

    for template in templates:
        for component in flat_list_components:
            print(template)
            print(component)

    return simultan_components


if __name__ == '__main__':

    # create example templates
    # templates = create_example_template()
    templates = create_example_template_bim_bestand_network()

    # write the example templates to a file:
    with open('example_templates.yml', mode='w') as f_obj:
        yaml.dump(templates, f_obj)

    # load the example templates:
    templates = load_templates('example_templates.yml')

    # create classes from the templates:
    template_classes = create_template_classes(templates)

    simultan_components = create_example_simultan_components(templates, n=5)
    simultan_components = class_type_simultan_components(simultan_components, template_classes)


    # the simultan components are now of the type which is defined in the templates
    print(simultan_components)

    # the class typed components still keep all methods and attributes from simultan:
    print(simultan_components[0].simultan_method())

    # and the class typed components have the new defined method python_spec_func:
    simultan_components[10].python_spec_func()

