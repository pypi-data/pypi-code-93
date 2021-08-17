from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for inputs that expect an annual schedule as a .csv file."""
schedule_csv_input = [
    InputAlias.any(
        name='schedule',
        description='An annual occupancy schedule, either as a path to a csv file (with '
        '8760 rows), a Ladybug Hourly Continuous Data Collection or a HB-Energy '
        'schedule object. This can also be the identifier of a schedule in '
        'your HB-Energy schedule library. Any value in this schedule that is '
        '0.1 or above will be considered occupied.',
        optional=True,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.schedule',
                function='schedule_to_csv'
            )
        ]
    )
]
