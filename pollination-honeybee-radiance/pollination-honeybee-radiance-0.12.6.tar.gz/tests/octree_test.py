from pollination.honeybee_radiance.octree import CreateOctree, CreateOctreeWithSky
from queenbee.plugin.function import Function


def test_create_octree():
    function = CreateOctree().queenbee
    assert function.name == 'create-octree'
    assert isinstance(function, Function)


def test_create_octree_with_sky():
    function = CreateOctreeWithSky().queenbee
    assert function.name == 'create-octree-with-sky'
    assert isinstance(function, Function)
