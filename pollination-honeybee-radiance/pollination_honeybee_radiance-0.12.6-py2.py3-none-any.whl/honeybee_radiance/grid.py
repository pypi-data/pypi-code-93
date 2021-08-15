from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class SplitGrid(Function):
    """Split a single sensor grid file into multiple smaller grids."""

    sensor_count = Inputs.int(
        description='Number of maximum sensors in each generated grid.',
        spec={'type': 'integer', 'minimum': 1}
    )

    input_grid = Inputs.file(description='Input grid file.', path='grid.pts')

    @command
    def split_grid(self):
        return 'honeybee-radiance grid split grid.pts ' \
            '{{self.sensor_count}} --folder output --log-file output/grids_info.json'

    grids_list = Outputs.list(
        description='A JSON array that includes information about generated sensor '
        'grids.', path='output/grids_info.json'
    )

    output_folder = Outputs.folder(
        description='Output folder with new sensor grids.', path='output'
    )


@dataclass
class SplitGridFromFolder(SplitGrid):
    """Split a single sensor grid file into multiple grids based on maximum number
    of sensors.

    This function takes a folder of sensor grids and find the target grid based on
    grid-name.
    """

    name = Inputs.str(description='Grid name.')

    input_grid = Inputs.folder(description='Path to sensor grids folder.', path='.')

    @command
    def split_grid(self):
        return 'honeybee-radiance grid split {{self.name}}.pts ' \
            '{{self.sensor_count}} --folder output --log-file output/grids_info.json'


@dataclass
class MergeFiles(Function):
    """Merge several files with similar starting name into one."""

    name = Inputs.str(
        description='Base name for files to be merged.',
        default='grid'
    )

    extension = Inputs.str(
        description='File extension including the . before the extension (e.g. .res, '
        '.ill)'
    )

    folder = Inputs.folder(
        description='Target folder with the input files.',
        path='input_folder'
    )

    @command
    def merge_files(self):
        return 'honeybee-radiance grid merge input_folder grid ' \
            ' {{self.extension}} --name {{self.name}}'

    result_file = Outputs.file(
        description='Output result file.', path='{{self.name}}{{self.extension}}'
    )
