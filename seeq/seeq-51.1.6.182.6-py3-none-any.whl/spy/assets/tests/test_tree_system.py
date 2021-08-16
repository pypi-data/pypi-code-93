import pytest
import pandas as pd
import numpy as np

from seeq import spy
from seeq.sdk import *
from seeq.spy.assets import Tree

from seeq.spy import _common
from seeq.spy.tests import test_common


def setup_module():
    test_common.login()


start_cleanup_names = {'test_tree_system', 'test_tree_system2'}
end_cleanup_ids = set()


@pytest.mark.system
def test_create_new_tree_then_repull_and_edit():
    tree = Tree('test_tree_system')
    tree.insert(['Cooling Tower 1', 'Cooling Tower 2'])
    tree.insert(children=['Area A', 'Area B', 'Area C'], parent='Cooling Tower 1')
    tree.insert(children=['Area E', 'Area F', 'Area G', 'Area H'], parent='Cooling Tower 2')
    tree.insert(children=['Temperature', 'Optimizer', 'Compressor'], parent=3)

    tower1_areas = ['Area A', 'Area B', 'Area C']
    tower2_areas = ['Area E', 'Area F', 'Area G', 'Area H']
    leaves = ['Temperature', 'Optimizer', 'Compressor']

    expected = list()
    expected.append({
        'Name': 'test_tree_system',
        'Path': '',
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'Cooling Tower 1',
        'Path': 'test_tree_system',
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'Cooling Tower 2',
        'Path': 'test_tree_system',
        'Type': 'Asset'
    })
    for area in tower1_areas:
        expected.append({
            'Name': area,
            'Path': 'test_tree_system >> Cooling Tower 1',
            'Type': 'Asset'
        })
        for leaf in leaves:
            expected.append({
                'Name': leaf,
                'Path': f'test_tree_system >> Cooling Tower 1 >> {area}',
                'Type': 'Asset'
            })
    for area in tower2_areas:
        expected.append({
            'Name': area,
            'Path': 'test_tree_system >> Cooling Tower 2',
            'Type': 'Asset'
        })
        for leaf in leaves:
            expected.append({
                'Name': leaf,
                'Path': f'test_tree_system >> Cooling Tower 2 >> {area}',
                'Type': 'Asset'
            })
    assert_tree_equals_expected(tree, expected)

    tree.push()
    assert not tree._dataframe['ID'].isnull().values.any(), "Pushing should set the dataframe's ID for all items"
    assert not tree._dataframe['Type'].isnull().values.any(), "Pushing should set the dataframe's Type for all items"
    search_results_df = spy.search({
        'Path': 'test_tree_system'
    })
    expected.pop(0)  # Since we're searching using Path, the root node won't be retrieved.
    assert_search_results_equals_expected(search_results_df, expected)
    add_all_pushed_ids_to_cleanup(search_results_df)

    # Pull in the previously-created test_tree_system by name
    tree = Tree('test_tree_system')
    add_all_pushed_ids_to_cleanup(tree._dataframe)
    original_root_id, original_root_referenced_id = get_root_node_ids(tree)
    assert _common.is_guid(original_root_id), \
        f'Pulled root ID should be a GUID: {original_root_id}'
    assert str(original_root_referenced_id) == str(np.nan), \
        f'Pulled root Reference ID should be {np.nan}: {original_root_referenced_id}'

    expected_existing_items = 1 + 2 + 3 + 4 + (3 * 3) + (4 * 3)
    assert len(tree._dataframe) == expected_existing_items, \
        f'Pulled tree items do not match count: Real={len(tree._dataframe)}, Expected={expected_existing_items}'
    expected_nodes = create_expected_list_from_tree(tree)

    # Add a single node
    tree.insert(children='Area I', parent='Cooling Tower 2')
    expected_nodes.append({
        'Name': 'Area I',
        'Path': 'test_tree_system >> Cooling Tower 2',
        'Type': 'Asset'
    })
    expected_existing_items += 1
    assert_tree_equals_expected(tree, expected_nodes)
    tree.push()
    # The ID column should be fully filled in when the push occurs
    assert not tree._dataframe['ID'].isnull().any()

    # Pull it again, but by ID
    tree2 = Tree(original_root_id)
    add_all_pushed_ids_to_cleanup(tree2._dataframe)
    assert len(tree2._dataframe) == expected_existing_items, \
        f'Edited tree items do not match count: Real={len(tree2._dataframe)}, Expected={expected_existing_items}'
    updated_root_id, updated_root_referenced_id = get_root_node_ids(tree2)
    assert original_root_id == updated_root_id, \
        f'Pulled root ID should be the same as before: Original={original_root_id}, Updated={updated_root_id}'
    assert str(original_root_referenced_id) == str(np.nan), \
        f'Pulled root Reference ID should be the same as before: ' \
        f'Original={original_root_referenced_id}, Updated={updated_root_referenced_id}'
    assert_tree_equals_expected(tree2, expected_nodes)


@pytest.mark.system
def test_insert_referenced_single_item():
    # Setup: Find the IDs of actual Example Data items
    items_api = ItemsApi(test_common.get_client())
    result = items_api.search_items(filters=['Name==Area A && Datasource ID==Example Data'],
                                    types=['Asset'])  # type: ItemSearchPreviewPaginatedListV1
    assert len(result.items) >= 1, 'There should be at least one global Area A asset'
    area_a_asset = result.items[0].id
    result = items_api.search_items(filters=['Name==Temperature'], types=['StoredSignal'], asset=area_a_asset)
    assert len(result.items) >= 1, 'There should be at least one global Area A Temperature signal'
    area_a_temperature = result.items[0].id

    # Test inserting an item by ID. It should be made into a reference.
    tree = Tree('test_tree_system2')
    tree.insert(area_a_temperature)
    expected = [{
        'Name': 'test_tree_system2',
        'Path': '',
        'Type': 'Asset'
    }, {
        'Referenced ID': area_a_temperature,
        'Name': 'Temperature',
        'Path': 'test_tree_system2',
        'Type': 'CalculatedSignal',
        'Formula Parameters': f'signal={area_a_temperature}'
    }]
    assert_tree_equals_expected(tree, expected)
    # Inserting it again will result in no change
    tree.insert(area_a_temperature)
    assert_tree_equals_expected(tree, expected)

    # Test inserting a dataframe with a custom name and ID. It too should be made into a reference that is distinct
    # from the previous one.
    df = pd.DataFrame([{'Name': 'Temperature with new name', 'ID': area_a_temperature}])
    tree.insert(df)
    expected.append({
        'Referenced ID': area_a_temperature,
        'Name': 'Temperature with new name',
        'Path': 'test_tree_system2',
        'Type': 'CalculatedSignal',
        'Formula Parameters': f'signal={area_a_temperature}'
    })
    assert_tree_equals_expected(tree, expected)
    # Inserting it again will still result in no change
    tree.insert(df)
    assert_tree_equals_expected(tree, expected)

    # 'Friendly Name' should work in the same way as above.
    df = pd.DataFrame([{'Friendly Name': 'Temperature with friendly name', 'ID': area_a_temperature}])
    tree.insert(df)
    expected.append({
        'Referenced ID': area_a_temperature,
        'Name': 'Temperature with friendly name',
        'Path': 'test_tree_system2',
        'Type': 'CalculatedSignal',
        'Formula Parameters': f'signal={area_a_temperature}'
    })
    assert_tree_equals_expected(tree, expected)
    # Inserting it again will still result in no change
    tree.insert(df)
    assert_tree_equals_expected(tree, expected)


@pytest.mark.system
def test_insert_referenced_tree_item():
    # Setup: Find the IDs of actual Example Data items
    items_api = ItemsApi(test_common.get_client())
    result = items_api.search_items(filters=['Name==Area A && Datasource ID==Example Data'], types=['Asset'])
    assert len(result.items) >= 1, 'There should be at least one global Area A asset'
    area_a_asset = result.items[0].id
    result = items_api.search_items(types=['StoredSignal'], asset=area_a_asset, order_by=['Name'])
    assert len(result.items) >= 5, 'There should be at least five global Area A signals'
    area_a_signals = list()
    for item in result.items:
        area_a_signals.append({'Name': item.name, 'ID': item.id})

    def create_expected_tuples(asset_name):
        expected_items = [{
            'Referenced ID': area_a_asset,
            'Name': asset_name,
            'Path': 'test_tree_system2',
            'Type': 'Asset'
        }]
        for signal in area_a_signals:
            expected_items.append({
                'Referenced ID': signal['ID'],
                'Name': signal['Name'],
                'Path': f'test_tree_system2 >> {asset_name}',
                'Type': 'CalculatedSignal',
                'Formula Parameters': f"signal={signal['ID']}"
            })
        return expected_items

    # Test inserting an asset by ID. It should be made into a reference and children pulled.
    tree = Tree('test_tree_system2')
    tree.insert(area_a_asset)
    expected = [{
        'Name': 'test_tree_system2',
        'Path': '',
        'Type': 'Asset'
    }] + create_expected_tuples('Area A')
    assert_tree_equals_expected(tree, expected)
    # Inserting it again will result in no change
    tree.insert(area_a_asset)
    assert_tree_equals_expected(tree, expected)

    # Test inserting a dataframe with a custom name and ID. It too should be made into a reference that is distinct
    # from the previous one.
    df = pd.DataFrame([{'Name': 'Area A with new name', 'ID': area_a_asset}])
    tree.insert(df)
    expected.extend(create_expected_tuples('Area A with new name'))
    assert_tree_equals_expected(tree, expected)
    # Inserting it again will still result in no change
    tree.insert(df)
    assert_tree_equals_expected(tree, expected)

    # 'Friendly Name' should work in the same way as above.
    df = pd.DataFrame([{'Friendly Name': 'Area A with friendly name', 'ID': area_a_asset}])
    tree.insert(df)
    expected.extend(create_expected_tuples('Area A with friendly name'))
    assert_tree_equals_expected(tree, expected)
    # Inserting it again will still result in no change
    tree.insert(df)
    assert_tree_equals_expected(tree, expected)

    # Inserting a mix of names+IDs should automatically figure out which is which. In this case, insert only
    # existing items. The lack of new rows will prove the resolution was successful (although some of the properties
    # will be lost on 'Area A with new name' due to this call no longer being a reference).
    tree.insert(['Area A with new name', area_a_asset])
    assert len(tree._dataframe) == len(expected)


@pytest.mark.system1
def test_comprehension_funcs_on_example_data():
    example = Tree('Example')

    assert example.height == 4
    assert example.size == 75

    counts = example.count()
    expected_counts = {
        'Asset': 14,
        'Signal': 61
    }
    for key in ['Asset', 'Signal']:
        assert counts[key] == expected_counts[key]
        assert example.count(key) == expected_counts[key]
    for key in ['Condition', 'Scalar', 'Formula']:
        assert example.count(key) == 0

    missing_items_dict = example.missing_items('dict')
    area_f = 'Example >> Cooling Tower 2 >> Area F'
    expected_missing_names = ['Compressor Stage', 'Optimizer', 'Relative Humidity', 'Temperature', 'Wet Bulb']
    assert len(missing_items_dict) == 1
    assert area_f in missing_items_dict
    assert len(missing_items_dict[area_f]) == 5
    for name in expected_missing_names:
        assert name in missing_items_dict[area_f]


def assert_tree_equals_expected(tree, expected_nodes):
    pd.set_option('display.max_columns', None)  # Print all columns if something errors
    tree_dataframe = tree._dataframe
    for expected_node in expected_nodes:
        found_series = pd.Series(data=([True] * len(tree_dataframe)))
        for key, value in expected_node.items():
            found_series = found_series & (tree_dataframe[key] == value)

        assert found_series.sum() == 1, \
            f"Found item {expected_node}" \
            f"\n{found_series.sum()} times in Dataframe" \
            f"\n{tree_dataframe}"
    assert len(tree_dataframe) == len(expected_nodes), \
        f'Tree items do not match count: Real={len(tree_dataframe)}, Expected={len(expected_nodes)}'


def assert_search_results_equals_expected(search_results_df, expected_nodes):
    pd.set_option('display.max_columns', None)  # Print all columns if something errors

    for expected_node in expected_nodes:
        asset = np.nan
        # Extract the parent asset from that path
        if expected_node['Path'].count('>>') > 0:
            asset = expected_node['Path'].rpartition(' >> ')[2]
        elif expected_node['Path'] is not '':
            asset = expected_node['Path']

        node_df = search_results_df[
            (search_results_df['Name'] == expected_node['Name']) &
            (search_results_df['Asset'] == asset) &
            (search_results_df['Type'] == expected_node['Type'])]

        assert len(node_df) == 1, \
            f"Expected item ({expected_node['Name']}, {asset}, {expected_node['Type']})" \
            f"\n was not found in Dataframe" \
            f"\n{search_results_df}"
    assert len(search_results_df) == len(expected_nodes), \
        f'Search result items do not match count: Real={len(search_results_df)}, Expected={len(expected_nodes)}'


def create_expected_list_from_tree(tree):
    # Create a list of node dicts from an existing tree.
    tree_dataframe = tree._dataframe
    expected = list()
    for index, row in tree_dataframe.iterrows():
        expected.append({
            'Name': row['Name'],
            'Path': row['Path'],
            'Type': row['Type']
        })
    return expected


def get_root_node_ids(tree):
    # Get the ID and Reference ID from the tree's root
    tree_dataframe = tree._dataframe
    root_df = tree_dataframe[(tree_dataframe['Path'] == '')]
    assert len(root_df) == 1, \
        f"Exactly one root node was not found in Dataframe: \n{tree_dataframe}"
    id = root_df['ID'].values[0]
    referenced_id = root_df['Referenced ID'].values[0]
    return id, referenced_id


def add_all_pushed_ids_to_cleanup(dataframe):
    # Get all IDs from the tree and add it to the set of cleanup_ids.
    for index, row in dataframe.iterrows():
        end_cleanup_ids.add(row['ID'])


@pytest.fixture(scope='module', autouse=True)
def setup_and_teardown():
    items_api = ItemsApi(test_common.get_client())
    # Setup: Make sure any previously-created versions of these trees are not present when beginning the test
    for cleanup_name in start_cleanup_names:
        cleanup_df = spy.search(query={'Name': cleanup_name})
        for index, cleanup_row in cleanup_df.iterrows():
            items_api.archive_item(id=cleanup_row['ID'])
    yield None
    # Teardown: Trash any items that we created
    for cleanup_id in end_cleanup_ids:
        items_api.archive_item(id=cleanup_id)
