from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for inputs that expect a simulation parameter .json file as the recipe input."""
energy_simulation_parameter_input = [
    InputAlias.any(
        name='sim_par',
        description='A SimulationParameter object that describes all of the setting for '
        'the energy simulation. If None, some default simulation parameters will '
        'automatically be used. This can also be the path to a SimulationParameter '
        'JSON file.',
        optional=True,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.simulation',
                function='energy_sim_par_to_json'
            )
        ]
    )
]


"""Alias for inputs that expect a IDF string input."""
idf_additional_strings_input = [
    InputAlias.any(
        name='add_str',
        description='THIS OPTION IS JUST FOR ADVANCED USERS OF ENERGYPLUS. '
        'An additional text string to be appended to the IDF before '
        'simulation. The input should include complete EnergyPlus objects as a '
        'single string following the IDF format. This input can be used to include '
        'EnergyPlus objects that are not currently supported by honeybee.',
        default='',
        platform=['grasshopper']
    )
]
