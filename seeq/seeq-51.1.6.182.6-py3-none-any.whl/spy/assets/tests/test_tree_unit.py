import pytest

import pandas as pd
from pandas._testing import assert_frame_equal
import numpy as np

from seeq import spy
from seeq.spy.assets import _tree


def _tree_from_nested_dict(d):
    if len(d) != 1:
        raise ValueError('Cannot have more than one root.')

    root_name, root_branches = [(k, v) for k, v in d.items()][0]
    tree = spy.assets.Tree(root_name)

    def _add_branches(parent_name, branches_dict):
        for branch_name, sub_branches in branches_dict.items():
            tree.insert(branch_name, parent_name)
            _add_branches(branch_name, sub_branches)

    _add_branches(root_name, root_branches)
    return tree


def _build_dataframe_from_path_name_depth_triples(data):
    df = pd.DataFrame(columns=_tree._dataframe_columns)
    return df.append([{
        'Type': 'Asset',
        'Path': path,
        'Depth': depth,
        'Name': name,
    } for path, name, depth in data])


@pytest.mark.unit1
def test_constructor_invalid():
    # Basic property validation
    with pytest.raises(TypeError, match="Argument 'data' should be type DataFrame or str, but is type int"):
        spy.assets.Tree(0)
    with pytest.raises(TypeError, match="'data' must be a name, Seeq ID, or Metadata dataframe"):
        spy.assets.Tree(data='')
    with pytest.raises(ValueError, match="DataFrame with no rows"):
        spy.assets.Tree(pd.DataFrame(columns=['Name']))
    with pytest.raises(TypeError, match="Argument 'description' should be type str"):
        spy.assets.Tree('name', description=0)
    with pytest.raises(TypeError, match="Argument 'workbook' should be type str"):
        spy.assets.Tree('name', workbook=0)
    with pytest.raises(TypeError, match="should be type DataFrame or str, but is type Tree"):
        spy.assets.Tree(spy.assets.Tree('Tree Inception'))

    df = pd.DataFrame([{'Name': 'root1', 'Type': 'Asset'}, {'Name': 'root2', 'Type': 'Asset'}])
    with pytest.raises(RuntimeError, match="Error encountered"):
        spy.assets.Tree(df)

    with pytest.raises(RuntimeError, match="Not logged in"):
        spy.assets.Tree('8DEECF16-A500-4231-939D-6C24DD123A30')


@pytest.mark.unit1
def test_constructor_dataframe_duplicate_roots_catalog_errors():
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root1', 1),
        ('Root1', 'Location A', 2)
    ])
    df = pd.DataFrame([{'Name': 'Root1', 'Type': 'Asset'},
                       {'Name': 'Root2', 'Type': 'Asset'},  # Root2 will not be added because errors=Catalog
                       {'Name': 'Location A', 'Type': 'Asset', 'Asset': 'Root1'}])
    tree = spy.assets.Tree(df, errors='catalog')
    assert_frame_equal(tree._dataframe, expected)


@pytest.mark.unit1
def test_constructor_name():
    # Valid constructor for a new root asset with all other properties default
    name = 'test name'
    expected = pd.DataFrame({
        'ID': np.nan,
        'Referenced ID': np.nan,
        'Type': 'Asset',
        'Path': '',
        'Depth': 1,
        'Name': name,
        'Description': np.nan,
        'Formula': np.nan,
        'Formula Parameters': np.nan,
        'Cache Enabled': np.nan
    }, index=[0])
    test_tree = spy.assets.Tree(name)
    assert test_tree._dataframe.columns.equals(expected.columns)
    assert test_tree._dataframe.iloc[0].equals(expected.iloc[0])
    assert test_tree._workbook == spy._common.DEFAULT_WORKBOOK_PATH

    # Valid constructor for a new root asset with all other properties assigned to non-defaults
    description = 'test description'
    workbook = 'test workbook'
    expected = pd.DataFrame({
        'ID': np.nan,
        'Referenced ID': np.nan,
        'Type': 'Asset',
        'Path': '',
        'Depth': 1,
        'Name': name,
        'Description': description,
        'Formula': np.nan,
        'Formula Parameters': np.nan,
        'Cache Enabled': np.nan
    }, index=[0])
    test_tree = spy.assets.Tree(name, description=description, workbook=workbook)
    assert test_tree._dataframe.columns.equals(expected.columns)
    assert test_tree._dataframe.iloc[0].equals(expected.iloc[0])
    assert test_tree._workbook == workbook


@pytest.mark.unit1
def test_insert_by_name():
    tree_dict = {
        'Root Asset': {
            'L Asset': {
                'LL Asset': {},
                'LR Asset': {}
            },
            'R Asset': {}
        }
    }
    test_tree = _tree_from_nested_dict(tree_dict)
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root Asset', 1),
        ('Root Asset', 'L Asset', 2),
        ('Root Asset >> L Asset', 'LL Asset', 3),
        ('Root Asset >> L Asset', 'LR Asset', 3),
        ('Root Asset', 'R Asset', 2),
    ])
    assert test_tree._dataframe.shape[0] == 5
    for i in range(5):
        assert test_tree._dataframe.iloc[i].equals(expected.iloc[i])


@pytest.mark.unit1
def test_insert_by_name_list():
    tree_dict = {
        'Root Asset': {
            'Location A': {},
            'Location B': {}
        }
    }
    test_tree = _tree_from_nested_dict(tree_dict)
    test_tree.insert([f'Equipment {n}' for n in range(1, 4)], parent='Location A')
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root Asset', 1),
        ('Root Asset', 'Location A', 2),
        ('Root Asset >> Location A', 'Equipment 1', 3),
        ('Root Asset >> Location A', 'Equipment 2', 3),
        ('Root Asset >> Location A', 'Equipment 3', 3),
        ('Root Asset', 'Location B', 2),
    ])
    assert test_tree._dataframe.shape[0] == 6
    for i in range(6):
        assert test_tree._dataframe.iloc[i].equals(expected.iloc[i])


@pytest.mark.unit1
def test_insert_at_depth():
    tree_dict = {
        'Root Asset': {
            'Location A': {},
            'Location B': {}
        }
    }
    test_tree = _tree_from_nested_dict(tree_dict)
    test_tree.insert([f'Equipment {n}' for n in range(1, 4)], parent=2)
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root Asset', 1),
        ('Root Asset', 'Location A', 2),
        ('Root Asset >> Location A', 'Equipment 1', 3),
        ('Root Asset >> Location A', 'Equipment 2', 3),
        ('Root Asset >> Location A', 'Equipment 3', 3),
        ('Root Asset', 'Location B', 2),
        ('Root Asset >> Location B', 'Equipment 1', 3),
        ('Root Asset >> Location B', 'Equipment 2', 3),
        ('Root Asset >> Location B', 'Equipment 3', 3),
    ])
    assert test_tree._dataframe.shape[0] == 9
    for i in range(9):
        assert test_tree._dataframe.iloc[i].equals(expected.iloc[i])


@pytest.mark.unit1
def test_insert_at_path():
    tree_dict = {
        'Root Asset': {
            'Factory': {
                'Location A': {},
                'Location B': {}
            }
        }
    }
    test_tree = _tree_from_nested_dict(tree_dict)
    # Test partial path match with regex
    test_tree.insert('Equipment 1', parent='Factory >> Location [A-Z]')
    # Test full path match with case insensitivity
    test_tree.insert('Equipment 2', parent='rOoT aSsEt >> FaCtOrY >> lOcAtIoN b')
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root Asset', 1),
        ('Root Asset', 'Factory', 2),
        ('Root Asset >> Factory', 'Location A', 3),
        ('Root Asset >> Factory >> Location A', 'Equipment 1', 4),
        ('Root Asset >> Factory', 'Location B', 3),
        ('Root Asset >> Factory >> Location B', 'Equipment 1', 4),
        ('Root Asset >> Factory >> Location B', 'Equipment 2', 4),
    ])
    assert test_tree._dataframe.shape[0] == 7
    for i in range(7):
        assert test_tree._dataframe.iloc[i].equals(expected.iloc[i])


@pytest.mark.unit1
def test_insert_at_root():
    tree_dict = {
        'Root Asset': {
            'Location A': {},
            'Location B': {}
        }
    }
    test_tree = _tree_from_nested_dict(tree_dict)
    test_tree.insert('Location C')
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root Asset', 1),
        ('Root Asset', 'Location A', 2),
        ('Root Asset', 'Location B', 2),
        ('Root Asset', 'Location C', 2),
    ])
    assert test_tree._dataframe.shape[0] == 4
    for i in range(4):
        assert test_tree._dataframe.iloc[i].equals(expected.iloc[i])


@pytest.mark.unit1
def test_insert_at_regex():
    tree_dict = {
        'Root Asset': {
            'Factory': {
                'Location Z': {}
            },
            'Area 51': {}
        }
    }
    test_tree = _tree_from_nested_dict(tree_dict)
    test_tree.insert('Equipment 1', parent='Area [1-9][0-9]*|Location [A-Z]+')
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root Asset', 1),
        ('Root Asset', 'Area 51', 2),
        ('Root Asset >> Area 51', 'Equipment 1', 3),
        ('Root Asset', 'Factory', 2),
        ('Root Asset >> Factory', 'Location Z', 3),
        ('Root Asset >> Factory >> Location Z', 'Equipment 1', 4)
    ])
    assert test_tree._dataframe.shape[0] == 6
    for i in range(6):
        assert test_tree._dataframe.iloc[i].equals(expected.iloc[i])


@pytest.mark.unit1
def test_insert_at_glob():
    tree_dict = {
        'Root Asset': {
            'Location A': {},
            'Location 1': {}
        }
    }
    test_tree = _tree_from_nested_dict(tree_dict)
    test_tree.insert('Equipment 1', parent='Location ?')
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root Asset', 1),
        ('Root Asset', 'Location 1', 2),
        ('Root Asset >> Location 1', 'Equipment 1', 3),
        ('Root Asset', 'Location A', 2),
        ('Root Asset >> Location A', 'Equipment 1', 3)
    ])
    assert test_tree._dataframe.shape[0] == 5
    for i in range(5):
        assert test_tree._dataframe.iloc[i].equals(expected.iloc[i])


@pytest.mark.unit1
def test_insert_preexisting_node():
    tree_dict = {
        'Root': {
            'Location A': {}
        }
    }
    tree = _tree_from_nested_dict(tree_dict)
    expected_dict = {
        'Root': {
            'lOcAtIoN a': {}
        }
    }
    expected = _tree_from_nested_dict(expected_dict)
    tree.insert('lOcAtIoN a')
    assert_frame_equal(tree._dataframe, expected._dataframe)


@pytest.mark.unit1
def test_insert_same_node_twice():
    tree_dict = {
        'Root': {}
    }
    tree = _tree_from_nested_dict(tree_dict)
    expected_dict = {
        'Root': {
            'Location A': {}
        }
    }
    expected = _tree_from_nested_dict(expected_dict)
    tree.insert(['Location A', 'Location A'])
    assert_frame_equal(tree._dataframe, expected._dataframe)


@pytest.mark.unit1
def test_insert_bad_depth():
    tree = spy.assets.Tree('Root')
    out_df = tree.insert('Location A', parent=2)
    assert len(out_df) == 1
    assert 'Ignored: No matching parent found' in out_df['Result'][0]
    assert len(tree._dataframe) == 1

    out_df = tree.insert('Location A', parent=-1)
    assert len(out_df) == 1
    assert 'Ignored: No matching parent found' in out_df['Result'][0]
    assert len(tree._dataframe) == 1


@pytest.mark.unit1
def test_constructor_dataframe_implied_and_leading_assets():
    # The constructor will imply assets and remove redundant leading assets.
    # Even though 'Root' and 'Location B' are not explicitly stated, they must exist for this to be a valid tree.
    insertions = _build_dataframe_from_path_name_depth_triples([
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root', 'Location A', 7),
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root >> Location A', 'Equipment 1', 8),
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root >> Location B', 'Equipment 2', 8),
    ])
    tree = spy.assets.Tree(insertions)
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 2),
        ('Root >> Location A', 'Equipment 1', 3),
        ('Root', 'Location B', 2),
        ('Root >> Location B', 'Equipment 2', 3),
    ])
    assert_frame_equal(tree._dataframe, expected)

    # And try with Path+Asset columns
    insertions = _build_dataframe_from_path_name_depth_triples([
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root', 'Equipment 1', 8),
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root', 'Equipment 2', 8),
    ])
    insertions['Asset'] = ['Location A', 'Location B']
    tree = spy.assets.Tree(insertions)
    assert_frame_equal(tree._dataframe, expected)


@pytest.mark.unit1
def test_insert_dataframe_implied_and_leading_assets():
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 2),
        ('Root >> Location A', 'Equipment 1', 3),
        ('Root', 'Location B', 2),
        ('Root >> Location B', 'Equipment 2', 3),
    ])
    insertions = _build_dataframe_from_path_name_depth_triples([
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root >> Location A', 'Equipment 1', 8),
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root >> Location B', 'Equipment 2', 8),
    ])
    tree = spy.assets.Tree('Root')
    result_df = tree.insert(insertions)
    assert_frame_equal(tree._dataframe, expected)
    assert len(result_df) == 4  # 2 explicit insertions + 2 implied
    assert (result_df['Result'] == 'Success').all()

    # And try with Path+Asset columns
    insertions = _build_dataframe_from_path_name_depth_triples([
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root', 'Equipment 1', 8),
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root', 'Equipment 2', 8),
    ])
    insertions['Asset'] = ['Location A', 'Location B']
    tree = spy.assets.Tree('Root')
    result_df = tree.insert(insertions)
    assert_frame_equal(tree._dataframe, expected)
    assert len(result_df) == 4  # 2 explicit insertions + 2 implied
    assert (result_df['Result'] == 'Success').all()


@pytest.mark.unit1
def test_constructor_and_insert_tree_dataframe():
    # The input properties (particularly the Referenced ID and Formula information) should come though
    root = {'Name': 'Root',
            'Type': 'Asset',
            'Referenced ID': 'Root_ID',
            'Path': '',
            'Depth': 1}
    signal = {'Name': 'Root',
              'Type': 'Asset',
              'Referenced ID': 'Signal_ID',
              'Formula': '$signal',
              'Formula Parameters': '$signal=Signal_ID',
              'Path': 'Root',
              'Depth': 2}
    expected = pd.DataFrame(columns=_tree._dataframe_columns)
    expected = expected.append([root, signal], ignore_index=True)
    tree = spy.assets.Tree(pd.DataFrame([root, signal]))
    assert_frame_equal(tree._dataframe, expected)

    tree = spy.assets.Tree('Root')
    result_df = tree.insert(pd.DataFrame([root, signal]))
    assert_frame_equal(tree._dataframe, expected)
    assert len(result_df) == 2
    assert (result_df['Result'] == 'Success').all()


@pytest.mark.unit1
def test_insert_dataframe_name_only():
    expected1 = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 2),
        ('Root', 'Location B', 2),
    ])
    insertions1 = pd.DataFrame([{'Name': 'Location A', 'Type': 'Asset'},
                                {'Name': 'Location B', 'Type': 'Asset'}])
    tree = spy.assets.Tree('Root')
    result_df1 = tree.insert(insertions1)
    assert_frame_equal(tree._dataframe, expected1)
    assert len(result_df1) == 2
    assert (result_df1['Result'] == 'Success').all()

    expected2 = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 2),
        ('Root >> Location A', 'Equipment 1', 3),
        ('Root >> Location A', 'Equipment 2', 3),
        ('Root', 'Location B', 2),
        ('Root >> Location B', 'Equipment 1', 3),
        ('Root >> Location B', 'Equipment 2', 3),
    ])
    insertions2 = pd.DataFrame([{'Name': 'Equipment 1'},
                                {'Name': 'Equipment 2'}])
    result_df2 = tree.insert(insertions2, parent='location *')
    assert_frame_equal(tree._dataframe, expected2)
    assert len(result_df2) == 4
    assert (result_df2['Result'] == 'Success').all()


@pytest.mark.unit1
def test_insert_dataframe_missing_name():
    insertions = pd.DataFrame([{'ID': 'Some ID'}])
    tree = spy.assets.Tree('Root')
    with pytest.raises(ValueError, match="'Name' or 'Friendly Name' must be provided"):
        tree.insert(insertions)


@pytest.mark.unit1
def test_insert_dataframe_bad_type():
    insertions = pd.DataFrame([{'Name': 'Location A', 'Type': 'UnknownType'}])
    tree = spy.assets.Tree('Root')
    result_df = tree.insert(insertions, errors='catalog')
    assert len(result_df) == 1
    assert 'Type UnknownType is not supported' in result_df.iloc[0]['Result']


@pytest.mark.unit1
def test_insert_dataframe_weird_index():
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Optimizer', 2),
        ('Root', 'Temperature', 2),
    ])
    insertions = pd.DataFrame([{'Name': 'Optimizer'},
                               {'Name': 'Temperature'}],
                              index=['some index', 'does not actually matter'])
    tree = spy.assets.Tree('Root')
    result_df = tree.insert(insertions)
    assert_frame_equal(tree._dataframe, expected)
    assert len(result_df) == 2
    assert (result_df['Result'] == 'Success').all()


@pytest.mark.unit1
def test_insert_dataframe_mixed_scope():
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Optimizer', 2),
        ('Root', 'Temperature', 2),
    ])
    insertions = pd.DataFrame([{'Name': 'Optimizer', 'Scoped To': np.nan},
                               {'Name': 'Temperature', 'Scoped To': '48C3002F-BBEA-4143-8765-D7DADD4E0CA2'}])
    tree = spy.assets.Tree('Root')
    result_df = tree.insert(insertions)
    assert_frame_equal(tree._dataframe, expected)
    assert len(result_df) == 2
    assert (result_df['Result'] == 'Success').all()


@pytest.mark.unit1
def test_insert_dataframe_with_mixed_path_existence():
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 2),
        ('Root >> Location A', 'Equipment 1', 3),
    ])
    # Inserting a NaN path implies that 'Location A' is the sub-root
    insertions = pd.DataFrame([{'Name': 'Location A', 'Type': 'Asset', 'Path': np.nan},
                               {'Name': 'Equipment 1', 'Type': 'Asset', 'Path': 'Location A'}])
    tree = spy.assets.Tree('Root')
    result_df1 = tree.insert(insertions)
    assert_frame_equal(tree._dataframe, expected)
    assert len(result_df1) == 2
    assert (result_df1['Result'] == 'Success').all()


@pytest.mark.unit1
def test_validate_insert_bad_parent():
    tree_dict = {
        'Root': {}
    }
    tree = _tree_from_nested_dict(tree_dict)
    insertions = _build_dataframe_from_path_name_depth_triples([
        ('', 'Location A', 2),
        ('Root >> Location A', 'Equipment 1', 3),
        ('Root', 'Location B', 2),
    ])
    out_df, insertion_df, error_summaries, num_success, num_failure = spy.assets._tree._validate_and_insert(
        tree._dataframe, insertions, 0)
    assert num_success == 1 and num_failure == 2
    assert len(out_df.index) == 2
    assert len(error_summaries) == 2
    assert 'Node\'s parent has mismatching path.' in error_summaries[0]
    assert 'Node\'s parent could not be inserted.' in error_summaries[1]
    assert 'Failure' in insertion_df.iloc[0]['Result'] and 'Failure' in insertion_df.iloc[1]['Result']
    assert 'Success' in insertion_df.iloc[2]['Result']


@pytest.mark.unit1
def test_validate_bad_depth():
    tree = spy.assets.Tree('Root')
    tree._dataframe = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 2),
        ('Root >> Location A', 'Equipment 1', 3),
        ('Root >> Location A', 'Equipment 2', 1),
    ])
    # This will actually throw a bad path error because _validate() checks nodes recursively by depth instead of path
    error_summaries, error_details, num_bad_nodes = spy.assets._tree._validate(tree._dataframe)
    print(error_summaries)
    assert num_bad_nodes == 1
    assert len(error_summaries) == 1
    error_msg = 'Node\'s parent has mismatching path.'
    assert error_msg in error_summaries[0]
    assert error_msg in error_details[3]

    tree = spy.assets.Tree('Root')
    tree._dataframe = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 3)
    ])
    error_summaries, error_details, num_bad_nodes = spy.assets._tree._validate(tree._dataframe)
    assert num_bad_nodes == 1
    assert len(error_summaries) == 1
    error_msg = 'Node\'s depth must be one more than the depth of its parent.'
    assert error_msg in error_summaries[0]
    assert error_msg in error_details[1]


@pytest.mark.unit1
def test_validate_bad_path():
    tree = spy.assets.Tree('Root')
    tree._dataframe = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 2),
        ('Root >> Locat--TYPO--ion A', 'Equipment 1', 3),
        ('Root >> Location A', 'Equipment 2', 3),
    ])
    error_summaries, error_details, num_bad_nodes = spy.assets._tree._validate(tree._dataframe)
    assert num_bad_nodes == 1
    assert len(error_summaries) == 1
    error_msg = 'Node\'s parent has mismatching path.'
    assert error_msg in error_summaries[0]
    assert error_msg in error_details[2]


@pytest.mark.unit1
def test_validate_insert_bad_parent():
    tree = spy.assets.Tree('Root')
    tree._dataframe = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('', 'Location A', 2),
        ('Root >> Location A', 'Equipment 1', 3),
        ('Root', 'Location B', 2),
    ])
    error_summaries, error_details, num_bad_nodes = spy.assets._tree._validate(tree._dataframe)
    assert num_bad_nodes == 2
    assert len(error_summaries) == 2
    assert 'Node\'s parent has mismatching path.' in error_summaries[0]
    assert 'Node\'s parent has mismatching path.' in error_details[1]
    assert 'Node\'s parent is invalid.' in error_summaries[1]
    assert 'Node\'s parent is invalid.' in error_details[2]


@pytest.mark.unit1
def test_insert_no_parent_match():
    tree = spy.assets.Tree('Root')
    bad_depth_df = tree.insert(children=['Child 1', 'Child 2'], parent=3)
    bad_name_df = tree.insert(children=['Child 1', 'Child 2'], parent='asdf')
    assert len(bad_depth_df.index) == 2
    assert len(bad_name_df.index) == 2
    assert (bad_depth_df['Result'] == 'Ignored: No matching parent found.').all()
    assert (bad_name_df['Result'] == 'Ignored: No matching parent found.').all()


@pytest.mark.unit1
def test_insert_other_tree():
    tree_to_insert = spy.assets.Tree('Area A')
    tree_to_insert.insert(['Optimizer', 'Temperature'])

    # Insert a tree directly below the root. The old 'Area A' root will not be transferred over.
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Real Root', 1),
        ('Real Root', 'Area A', 2),
        ('Real Root >> Area A', 'Optimizer', 3),
        ('Real Root >> Area A', 'Temperature', 3),
        ('Real Root', 'Tower', 2),
    ])
    tree = spy.assets.Tree('Real Root')
    tree.insert('Tower')
    tree.insert(tree_to_insert)
    assert_frame_equal(tree._dataframe, expected_df)
    # Do it again to show it up-serts the nodes
    tree.insert(tree_to_insert)
    assert_frame_equal(tree._dataframe, expected_df)

    # Insert a tree below multiple parents
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Real Root', 1),
        ('Real Root', 'Tower 1', 2),
        ('Real Root >> Tower 1', 'Area A', 3),
        ('Real Root >> Tower 1 >> Area A', 'Optimizer', 4),
        ('Real Root >> Tower 1 >> Area A', 'Temperature', 4),
        ('Real Root', 'Tower 2', 2),
        ('Real Root >> Tower 2', 'Area A', 3),
        ('Real Root >> Tower 2 >> Area A', 'Optimizer', 4),
        ('Real Root >> Tower 2 >> Area A', 'Temperature', 4),
    ])
    tree = spy.assets.Tree('Real Root')
    tree.insert(['Tower 1', 'Tower 2'])
    tree.insert(tree_to_insert, parent='Tower*')
    assert_frame_equal(tree._dataframe, expected_df)


@pytest.mark.unit1
def test_trim_unneeded_paths_constructor():
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Real Root', 1),
        ('Real Root', 'Tower', 2),
        ('Real Root >> Tower', 'Area A', 3),
        ('Real Root >> Tower >> Area A', 'Optimizer', 4),
        ('Real Root >> Tower >> Area A', 'Temperature', 4),
    ])
    # Test three leading nodes to be removed
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2', 'Real Root', 4),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root', 'Tower', 5),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower', 'Area A', 6),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower >> Area A', 'Optimizer', 7),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower >> Area A', 'Temperature', 7),
    ])
    tree = spy.assets.Tree(test_df)
    assert_frame_equal(tree._dataframe, expected_df)

    # Test one leading node to be removed
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Dupe Root', 'Real Root', 2),
        ('Dupe Root >> Real Root', 'Tower', 3),
        ('Dupe Root >> Real Root >> Tower', 'Area A', 4),
        ('Dupe Root >> Real Root >> Tower >> Area A', 'Temperature', 5),
        ('Dupe Root >> Real Root >> Tower >> Area A', 'Optimizer', 5),
    ])
    tree = spy.assets.Tree(test_df)
    assert_frame_equal(tree._dataframe, expected_df)

    # Test no changes needed
    test_df = expected_df.copy()
    tree = spy.assets.Tree(test_df)
    assert_frame_equal(tree._dataframe, expected_df)

    # Test with implied shared roots only
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Real Root', 1),
        ('Real Root', 'Tower 1', 2),
        ('Real Root >> Tower 1', 'Area A', 3),
        ('Real Root >> Tower 1 >> Area A', 'Optimizer', 4),
        ('Real Root >> Tower 1 >> Area A', 'Temperature', 4),
        ('Real Root', 'Tower 2', 2),
        ('Real Root >> Tower 2', 'Area A', 3),
        ('Real Root >> Tower 2 >> Area A', 'Optimizer', 4),
        ('Real Root >> Tower 2 >> Area A', 'Temperature', 4),
    ])
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower 1 >> Area A', 'Temperature', 4),
        ('Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower 1 >> Area A', 'Optimizer', 4),
        ('Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower 2 >> Area A', 'Temperature', 4),
        ('Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower 2 >> Area A', 'Optimizer', 4),
    ])
    tree = spy.assets.Tree(test_df)
    assert_frame_equal(tree._dataframe, expected_df)


@pytest.mark.unit1
def test_trim_unneeded_paths_insert():
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Real Root', 1),
        ('Real Root', 'Tower', 2),
        ('Real Root >> Tower', 'Area A', 3),
        ('Real Root >> Tower >> Area A', 'Optimizer', 4),
        ('Real Root >> Tower >> Area A', 'Temperature', 4),
    ])
    # Test three leading nodes to be removed with the same root as parent
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2', 'Real Root', 4),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root', 'Tower', 5),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower', 'Area A', 6),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower >> Area A', 'Temperature', 7),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower >> Area A', 'Optimizer', 7),
    ])
    tree = spy.assets.Tree('Real Root')
    tree.insert(test_df)
    assert_frame_equal(tree._dataframe, expected_df)

    # Test one leading node to be removed
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Dupe Root', 'Real Root', 2),
        ('Dupe Root >> Real Root', 'Tower', 3),
        ('Dupe Root >> Real Root >> Tower', 'Area A', 4),
        ('Dupe Root >> Real Root >> Tower >> Area A', 'Temperature', 5),
        ('Dupe Root >> Real Root >> Tower >> Area A', 'Optimizer', 5),
    ])
    tree = spy.assets.Tree('Real Root')
    tree.insert(test_df)
    assert_frame_equal(tree._dataframe, expected_df)

    # Test no changes needed
    tree = spy.assets.Tree('Real Root')
    tree.insert(expected_df.copy())
    assert_frame_equal(tree._dataframe, expected_df)

    # Test three leading nodes to be removed with a different root as parent
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Real Root', 1),
        ('Real Root', 'Sub Root', 2),
        ('Real Root >> Sub Root', 'Tower', 3),
        ('Real Root >> Sub Root >> Tower', 'Area A', 4),
        ('Real Root >> Sub Root >> Tower >> Area A', 'Optimizer', 5),
        ('Real Root >> Sub Root >> Tower >> Area A', 'Temperature', 5),
    ])
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2', 'Sub Root', 4),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Sub Root', 'Tower', 5),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Sub Root >> Tower', 'Area A', 6),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Sub Root >> Tower >> Area A', 'Temperature', 7),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Sub Root >> Tower >> Area A', 'Optimizer', 7),
    ])
    tree = spy.assets.Tree('Real Root')
    tree.insert(test_df)
    assert_frame_equal(tree._dataframe, expected_df)

    # Test with implied shared roots only
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Real Root', 1),
        ('Real Root', 'Sub Root', 2),
        ('Real Root >> Sub Root', 'Tower 1', 3),
        ('Real Root >> Sub Root >> Tower 1', 'Area A', 4),
        ('Real Root >> Sub Root >> Tower 1 >> Area A', 'Optimizer', 5),
        ('Real Root >> Sub Root >> Tower 1 >> Area A', 'Temperature', 5),
        ('Real Root >> Sub Root', 'Tower 2', 3),
        ('Real Root >> Sub Root >> Tower 2', 'Area A', 4),
        ('Real Root >> Sub Root >> Tower 2 >> Area A', 'Optimizer', 5),
        ('Real Root >> Sub Root >> Tower 2 >> Area A', 'Temperature', 5),
    ])
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Dupe Path >> Sub Root >> Tower 1 >> Area A', 'Temperature', 5),
        ('Dupe Path >> Sub Root >> Tower 1 >> Area A', 'Optimizer', 5),
        ('Dupe Path >> Sub Root >> Tower 2 >> Area A', 'Temperature', 5),
        ('Dupe Path >> Sub Root >> Tower 2 >> Area A', 'Optimizer', 5),
    ])
    tree = spy.assets.Tree('Real Root')
    tree.insert(test_df)
    assert_frame_equal(tree._dataframe, expected_df)
    # Inserting that same thing again should be idempotent.
    tree.insert(test_df)
    assert_frame_equal(tree._dataframe, expected_df)


@pytest.mark.unit1
def test_reify_missing_assets():
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Tower', 2),
        ('Root >> Tower', 'Region 1', 3),
        ('Root >> Tower >> Region 1', 'Area A', 4),
        ('Root >> Tower >> Region 1 >> Area A', 'Optimizer', 5),
        ('Root >> Tower >> Region 1 >> Area A', 'Temperature', 5),
        ('Root >> Tower >> Region 1', 'Area B', 4),
        ('Root >> Tower >> Region 1 >> Area B', 'Optimizer', 5),
        ('Root >> Tower', 'Region 2', 3),
        ('Root >> Tower >> Region 2', 'Area C', 4),
        ('Root >> Tower >> Region 2 >> Area C', 'Temperature', 5),
    ])
    # Test everything missing except the leaf nodes
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Root >> Tower >> Region 1 >> Area A', 'Optimizer', 5),
        ('Root >> Tower >> Region 1 >> Area A', 'Temperature', 5),
        ('Root >> Tower >> Region 1 >> Area B', 'Optimizer', 5),
        ('Root >> Tower >> Region 2 >> Area C', 'Temperature', 5),
    ])
    result_df, _ = spy.assets._tree._reify_missing_assets(test_df)
    spy.assets._tree._sort_by_node_path(result_df)
    assert_frame_equal(result_df, expected_df)

    # Test everything missing between the root and the leaves
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root >> Tower >> Region 1 >> Area A', 'Optimizer', 5),
        ('Root >> Tower >> Region 1 >> Area A', 'Temperature', 5),
        ('Root >> Tower >> Region 1 >> Area B', 'Optimizer', 5),
        ('Root >> Tower >> Region 2 >> Area C', 'Temperature', 5),
    ])
    result_df, _ = spy.assets._tree._reify_missing_assets(test_df)
    spy.assets._tree._sort_by_node_path(result_df)
    assert_frame_equal(result_df, expected_df)

    # Test missing the root-most two levels
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Root >> Tower', 'Region 1', 3),
        ('Root >> Tower >> Region 1', 'Area A', 4),
        ('Root >> Tower >> Region 1 >> Area A', 'Optimizer', 5),
        ('Root >> Tower >> Region 1 >> Area A', 'Temperature', 5),
        ('Root >> Tower >> Region 1', 'Area B', 4),
        ('Root >> Tower >> Region 1 >> Area B', 'Optimizer', 5),
        ('Root >> Tower', 'Region 2', 3),
        ('Root >> Tower >> Region 2', 'Area C', 4),
        ('Root >> Tower >> Region 2 >> Area C', 'Temperature', 5),
    ])
    result_df, _ = spy.assets._tree._reify_missing_assets(test_df)
    spy.assets._tree._sort_by_node_path(result_df)
    assert_frame_equal(result_df, expected_df)

    # Test no changes needed
    test_df = expected_df.copy()
    result_df, _ = spy.assets._tree._reify_missing_assets(test_df)
    spy.assets._tree._sort_by_node_path(result_df)
    assert_frame_equal(result_df, expected_df)

    # Test where the first two levels should not be reified.
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('Root >> Tower', 'Region 1', 3),
        ('Root >> Tower >> Region 1', 'Area A', 4),
        ('Root >> Tower >> Region 1 >> Area A', 'Optimizer', 5),
        ('Root >> Tower >> Region 1 >> Area A', 'Temperature', 5),
        ('Root >> Tower >> Region 1', 'Area B', 4),
        ('Root >> Tower >> Region 1 >> Area B', 'Optimizer', 5),
        ('Root >> Tower', 'Region 2', 3),
        ('Root >> Tower >> Region 2', 'Area C', 4),
        ('Root >> Tower >> Region 2 >> Area C', 'Temperature', 5),
    ])
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Root >> Tower >> Region 1 >> Area A', 'Optimizer', 5),
        ('Root >> Tower >> Region 1 >> Area A', 'Temperature', 5),
        ('Root >> Tower >> Region 1 >> Area B', 'Optimizer', 5),
        ('Root >> Tower >> Region 2 >> Area C', 'Temperature', 5),
    ])
    result_df, _ = spy.assets._tree._reify_missing_assets(test_df, 'Root >> Tower')
    spy.assets._tree._sort_by_node_path(result_df)
    assert_frame_equal(result_df, expected_df)


@pytest.mark.unit1
def test_upsert_node():
    input_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Area A', 2),
        ('Root >> Area A', 'Optimizer', 3),
        ('Root >> Area A', 'Temperature', 3),
        ('Root', 'Area B', 2),
        ('Root >> Area B', 'Optimizer', 3),
        ('Root', 'Area C', 2),
        ('Root >> Area C', 'Temperature', 3),
    ])

    # Test adding a new node using a row
    row_to_add = _build_dataframe_from_path_name_depth_triples(
        [('Root >> Area B', 'Temperature', 3)]).iloc[0]
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Area A', 2),
        ('Root >> Area A', 'Optimizer', 3),
        ('Root >> Area A', 'Temperature', 3),
        ('Root', 'Area B', 2),
        ('Root >> Area B', 'Optimizer', 3),
        ('Root >> Area B', 'Temperature', 3),
        ('Root', 'Area C', 2),
        ('Root >> Area C', 'Temperature', 3),
    ])
    result_df, did_upsert = spy.assets._tree._upsert_node(input_df.copy(), row_to_add, False)
    spy.assets._tree._sort_by_node_path(result_df)
    assert_frame_equal(result_df, expected_df)
    assert did_upsert is True

    # Test adding a new node using a dict
    dict_to_add = {
        'ID': np.nan,
        'Referenced ID': np.nan,
        'Type': 'Asset',
        'Path': 'Root >> Area C',
        'Depth': 3,
        'Name': 'Optimizer',
        'Description': np.nan,
        'Formula': np.nan,
        'Formula Parameters': np.nan,
        'Cache Enabled': np.nan
    }
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Area A', 2),
        ('Root >> Area A', 'Optimizer', 3),
        ('Root >> Area A', 'Temperature', 3),
        ('Root', 'Area B', 2),
        ('Root >> Area B', 'Optimizer', 3),
        ('Root', 'Area C', 2),
        ('Root >> Area C', 'Optimizer', 3),
        ('Root >> Area C', 'Temperature', 3),
    ])
    result_df, did_upsert = spy.assets._tree._upsert_node(input_df.copy(), dict_to_add, False)
    spy.assets._tree._sort_by_node_path(result_df)
    assert_frame_equal(result_df, expected_df)
    assert did_upsert is True

    # Test not updating an existing node because prefer_existing_row=True
    dict_to_update = {
        'ID': 'Some ID',
        'Referenced ID': 'Some Referenced ID',
        'Type': 'CalculatedSignal',
        'Path': 'RoOt >> ArEa A',
        'Depth': 3,
        'Name': 'OpTiMiZeR',
        'Description': 'Some Description',
        'Formula': 'sinusoid()+$a',
        'Formula Parameters': ['a=some-referenced-id'],
        'Cache Enabled': False
    }
    result_df, did_upsert = spy.assets._tree._upsert_node(input_df.copy(), dict_to_update, True)
    assert_frame_equal(result_df, input_df)
    assert did_upsert is False

    # Test updating an existing node
    expected_df = input_df.copy()
    for key, value in dict_to_update.items():
        expected_df[key][2] = value
    result_df, did_upsert = spy.assets._tree._upsert_node(input_df.copy(), dict_to_update, False)
    assert_frame_equal(result_df, expected_df)
    assert did_upsert is True
