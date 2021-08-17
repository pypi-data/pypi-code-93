from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for text that filters the simulated radiance grids."""
grid_filter_input = [
    InputAlias.str(
        name='grid_filter',
        description='Text for a grid identifer or a pattern to filter the sensor grids '
        'of the model that are simulated. For instance, first_floor_* will simulate '
        'only the sensor grids that have an identifier that starts with '
        'first_floor_. By default, all grids in the model will be simulated.',
        default='*',
        platform=['grasshopper']
    )
]


"""Alias for inputs that split sensor grids for parallel execution."""
sensor_count_input = [
    InputAlias.int(
        name='sensor_count',
        description='Positive integer for the number of sensor grid points per '
        'parallel execution. Lower numbers will result in sensor grids being '
        'split into more pieces and, since each grid piece is run by a separate worker, '
        'this can mean a faster simulation on machines with several CPUs. However ,'
        'If the number is too low, the overhad of splitting the grid will not be worth '
        'the time gained through parallelization. (Default: 200).',
        default=200,
        platform=['grasshopper']
    )
]
