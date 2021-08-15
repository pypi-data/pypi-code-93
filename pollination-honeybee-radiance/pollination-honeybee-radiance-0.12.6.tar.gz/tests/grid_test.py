from pollination.honeybee_radiance.grid import SplitGrid, SplitGridFromFolder, \
    MergeFiles
from queenbee.plugin.function import Function


def test_split_grid():
    function = SplitGrid().queenbee
    assert function.name == 'split-grid'
    assert isinstance(function, Function)


def test_split_grid_from_folder():
    function = SplitGridFromFolder().queenbee
    assert function.name == 'split-grid-from-folder'
    assert isinstance(function, Function)


def test_merge_files():
    function = MergeFiles().queenbee
    assert function.name == 'merge-files'
    assert isinstance(function, Function)
