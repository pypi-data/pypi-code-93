import fnmatch
import re

import numpy as np
import pandas as pd

from seeq import spy
from seeq.sdk import *
from seeq.spy import _common
from seeq.spy import _config
from seeq.spy import _login
from seeq.spy import _metadata
from seeq.spy import _push
from seeq.spy import _search
from seeq.spy._errors import *

_reference_types = ['StoredSignal', 'StoredCondition']
_calculated_types = ['CalculatedScalar', 'CalculatedSignal', 'CalculatedCondition']
_data_types = _calculated_types + _reference_types
_supported_input_types = _data_types + ['Asset']
_supported_output_types = _calculated_types + ['Asset']
_dataframe_columns = ['ID', 'Referenced ID', 'Type', 'Path', 'Depth', 'Name', 'Description',
                      'Formula', 'Formula Parameters', 'Cache Enabled']


class Tree:
    _dataframe = pd.DataFrame()
    _workbook = _common.DEFAULT_WORKBOOK_PATH
    _workbook_id = _common.EMPTY_GUID

    quiet = False
    errors = 'raise'

    _conditions_api = None
    _formulas_api = None
    _items_api = None
    _scalars_api = None
    _signals_api = None
    _trees_api = None
    _workbooks_api = None

    def __init__(self, data, *, description=None, workbook='Data Lab >> Data Lab Analysis',
                 quiet=False, errors='raise', status=None):
        """
        Utilizes a Python Class-based tree to produce a set of item definitions as
        a metadata DataFrame. Allows users to manipulate the tree using various functions.

        Parameters
        ----------
        data : {pandas.DataFrame, str}
            Defines which element will be inserted at the root.
            If an existing tree already exists in Seeq, the entire tree will be pulled recursively.
            If this tree doesn't already within the scope of the workbook, new tree elements
            will be created (by deep-copy or reference if applicable).
            The following options are allowed:
            1) A name string. If an existing tree with that name (case-insensitive) is found,
                all children will be recursively pulled in.
            2) An ID string of an existing item in Seeq. If that item is in a tree, all
                children will be recursively pulled in.
            3) spy.search results or other custom dataframes. The 'Path' column must be present
                and represent a single tree structure.

        description : str, optional
            The description to set on the root-level asset.

        workbook : str, default 'Data Lab >> Data Lab Analysis'
            The path to a workbook (in the form of 'Folder >> Path >> Workbook Name')
            or an ID that all pushed items will be 'scoped to'. You can
            push to the Corporate folder by using the following pattern:
            '__Corporate__ >> Folder >> Path >> Workbook Name'. A Tree currently
            may not be globally scoped. These items will not be visible/searchable
            using the data panel in other workbooks.

        quiet : bool, default False
            If True, suppresses progress output. This setting will be the default for all
            operations on this Tree. This option can be changed later using
            `tree.quiet = True` or by specifying the option for individual function calls.
            Note that when status is provided, the quiet setting of the Status object
            that is passed in takes precedent.

        errors : {'raise', 'catalog'}, default 'raise'
            If 'raise', any errors encountered will cause an exception. If 'catalog',
            errors will be added to a 'Result' column in the status.df DataFrame. The
            option chosen here will be the default for all other operations on this Tree.
            This option can be changed later using `tree.errors = 'catalog'` or by
            specifying the option for individual function calls.

        status : spy.Status, optional
            If specified, the supplied Status object will be updated as the command
            progresses. It gets filled in with the same information you would see
            in Jupyter in the blue/green/red table below your code while the
            command is executed. The table itself is accessible as a DataFrame via
            the status.df property.
        """
        _common.validate_argument_types([
            (data, 'data', (pd.DataFrame, str)),
            (description, 'description', str),
            (workbook, 'workbook', str),
            (quiet, 'quiet', bool),
            (errors, 'errors', str),
            (status, 'status', _common.Status)
        ])
        _common.validate_errors_arg(errors)
        self.quiet = quiet
        self.errors = errors
        status = _common.Status.validate(status, quiet)
        if _login.client:
            self._conditions_api = ConditionsApi(_login.client)
            self._formulas_api = FormulasApi(_login.client)
            self._items_api = ItemsApi(_login.client)
            self._scalars_api = ScalarsApi(_login.client)
            self._signals_api = SignalsApi(_login.client)
            self._trees_api = TreesApi(_login.client)
            self._workbooks_api = WorkbooksApi(_login.client)

        self._workbook = workbook if workbook else _common.DEFAULT_WORKBOOK_PATH
        self._find_workbook_id(quiet, status)

        self._dataframe = pd.DataFrame(columns=_dataframe_columns)

        if isinstance(data, pd.DataFrame):
            if len(data) == 0:
                status.exception(SPyValueError("A tree may not be created from a DataFrame with no rows"), throw=True)
            self._add_dataframe(data, errors, quiet, status=status)
        elif data and isinstance(data, str):
            if _common.is_guid(data):
                existing_node_id = data
            else:
                existing_node_id = _find_existing_root_node_id(data, status, self._trees_api, self._workbook_id)
            if existing_node_id:
                self._pull_node_recursively(existing_node_id, errors, quiet, status=status)
            else:
                # Define a brand new root asset
                root_node = {
                    'Type': 'Asset',
                    'Path': '',
                    'Depth': 1,
                    'Name': data,
                    'Description': description if description else np.nan
                }
                self._dataframe = self._dataframe.append(root_node, ignore_index=True)
                status.update(f"No existing root found. New root '{data}' defined."
                              f"{'' if _login.client else ' If an existing tree was expected, please log in.'}",
                              _common.Status.SUCCESS)
        else:
            e = SPyTypeError("Input 'data' must be a name, Seeq ID, or Metadata dataframe when creating a Tree")
            status.exception(e, throw=True)
        _sort_by_node_path(self._dataframe)
        if description:
            self._dataframe.loc[0, 'Description'] = description
        error_summaries, error_details, num_bad_nodes = _validate(self._dataframe)
        if errors == 'raise' and num_bad_nodes:
            status.exception(SPyRuntimeError(_format_error_summaries(error_summaries)), throw=True)

    def insert(self, children, parent=None, *, friendly_name=None, formula=None, formula_params=None,
               errors=None, quiet=None, status=None):
        """
        Insert the specified elements into the tree.

        Parameters
        ----------
        children : {pandas.DataFrame, str, list, Tree}, optional
            Defines which element or elements will be inserted below each parent. If an existing
            node already existed at the level in the tree with that name (case-insensitive),
            it will be updated. If it doesn't already exist, a new node will be created
            (by deep-copy or reference if applicable).
            The following options are allowed:
            1) A basic string or list of strings to create a new asset.
            2) Another SPy Tree.
            3) spy.search results or other custom dataframes.

        parent : {pandas.DataFrame, str, int}, optional
            Defines which element or elements the children will be inserted below.
            If a parent match is not found and non-glob/regex string or path is used,
            the parent (or entire path) will be created too.
            The following options are allowed:
            1) No parent specified will insert directly to the root of the tree.
            2) String name match (case-insensitive equality, globbing, regex, column
                values) will find any existing nodes in the tree that match.
            3) String path match, including partial path matches.
            4) ID. This can either be the actual ID of the tree.push()ed node or the
                ID of the source item.
            5) Number specifying tree level. This will add the children below every
                node at the specified level in the tree (1 being the root node).
            6) spy.search results or other custom dataframe.

        friendly_name : str, optional
            Use this specified name rather than the referenced item's original name.

        formula : str, optional
            The formula for a calculated item. The `formula` and `formula_parameters` are
            used in place of the `children` argument.

        formula_params : dict, optional
            The parameters for a formula.

        errors : {'raise', 'catalog'}, optional
            If 'raise', any errors encountered will cause an exception. If 'catalog',
            errors will be added to a 'Result' column in the status.df DataFrame. This
            input will be used only for the duration of this function; it will default
            to the setting on the Tree if not specified.

        quiet : bool, optional
            If True, suppresses progress output. This input will be used only for the
            duration of this function; it will default to the setting on the Tree if
            not specified. Note that when status is provided, the quiet setting of
            the Status object that is passed in takes precedent.

        status : spy.Status, optional
            If specified, the supplied Status object will be updated as the command
            progresses. It gets filled in with the same information you would see
            in Jupyter in the blue/green/red table below your code while the
            command is executed. The table itself is accessible as a DataFrame via
            the status.df property.
        """

        if children is None:
            if formula and formula_params:
                # TODO CRAB-24291 Insert calculations
                raise SPyValueError('Inserting calculations is not currently supported')
            else:
                e = SPyValueError('Formula and formula parameters must be specified if no children argument is given.')
                status.exception(e, throw=True)
        else:
            if formula or formula_params:
                e = SPyValueError('Formula and formula parameters must be None if a children argument is given.')
                status.exception(e, throw=True)

        _common.validate_argument_types([
            (children, 'children', (pd.DataFrame, Tree, str, list)),
            (parent, 'parent', (pd.DataFrame, str, int)),
            (friendly_name, 'friendly_name', str),
            (formula, 'formula', str),
            (formula_params, 'formula_params', dict)
        ])
        errors = self._get_or_default_errors(errors)
        quiet = self._get_or_default_quiet(quiet)
        status = _common.Status.validate(status, quiet)

        if isinstance(children, str):
            children = [children]
        if isinstance(children, list):
            temp_children = pd.DataFrame(columns=['Name', 'ID', 'Type'])
            for child in children:
                if _common.is_guid(child):
                    temp_children = temp_children.append({'ID': child}, ignore_index=True)
                else:
                    temp_children = temp_children.append({'Name': child, 'Type': 'Asset'}, ignore_index=True)
            children = temp_children
        elif isinstance(children, Tree):
            children = children._dataframe
        # Order doesn't matter for the children dataframe, but we require standard indexing for the result output later
        children = children.reset_index(drop=True)

        # Ensure the minimum properties are present and filled out so that we can work with them in a reliable way
        if 'Name' not in children and 'Friendly Name' not in children:
            e = SPyValueError("'Name' or 'Friendly Name' must be provided")
            status.exception(e, throw=True)
        if 'Depth' in children:
            children['Depth'] = children['Depth'].fillna(1)
        if 'Path' in children:
            children['Path'] = children['Path'].fillna('')
        if 'Path' in children or 'Asset' in children:
            children['Path'] = children.apply(lambda row: _get_relative_path_from_dataframe_row(row), axis=1)
            if 'Asset' in children:
                children = children.drop(['Asset'], axis=1)

        error_summaries = list()
        children_added_count = 0
        children_failed_count = 0
        # A bool for each of the children, indicating that a parent was properly found
        parents_found = pd.Series([False] * len(children))
        results_df = pd.DataFrame(columns=_dataframe_columns + ['Result'])

        def _get_children_to_add(children_df, parent_node):
            children_to_add = children_df.copy()
            # TODO CRAB-24298: filter children by column names using the match object
            parents_found[:] = True
            parent_full_path = f"{parent_node['Path']} >> {parent_node['Name']}" \
                if parent_node['Depth'] != 1 else parent_node['Name']
            if 'Parent' in children_df.columns:
                # TODO CRAB-24290: Allow 'Parent' to be directly specified in the input dataframe
                raise SPyValueError("'Parent' input column is not yet supported.")
            elif 'Path' in children_df.columns and not pd.isna(children_df['Path']).all():
                # Since Path is already in this input, make the path as simple as possible before sending to
                # _add_dataframe() so that the subtree structure is maintained.
                children_to_add = _trim_unneeded_paths(children_to_add, parent_full_path)
                children_to_add, _ = _reify_missing_assets(children_to_add, parent_full_path)
            else:
                # No path found in the input children DF. All children will be below this parent.
                children_to_add['Path'] = parent_full_path
                children_to_add['Depth'] = parent_node['Depth'] + 1
            return children_to_add

        # A list of parent+child_df pairs to add to the dataframe. We should discover what all the items to be added
        # are before actually adding them so that we do not modify the dataframe while iterating over it.
        # TODO CRAB-24290 Insert with parents defined by dataframes
        # TODO CRAB-24298 Insert using Column Values from a dataframe
        items_to_add = list()
        use_string_match = isinstance(parent, str) and not _common.is_guid(parent)
        parent_pattern = None if not use_string_match else _node_match_string_to_regex(parent)
        for i, parent_row in self._dataframe.iterrows():
            if use_string_match:
                is_match = _node_match_using_regex(parent_row, parent_pattern)
            else:
                is_match = _node_match_no_regex(parent_row, parent)
            if is_match:
                maybe_children = _get_children_to_add(children, parent_row)
                valid_children = pd.DataFrame(columns=_dataframe_columns)
                for j, child_row in maybe_children.iterrows():
                    error_message = _validate_properties_single_node(child_row)
                    if error_message:
                        children_failed_count += 1
                        error_summaries += error_message
                        result_row = child_row.copy()
                        result_row['Result'] = 'Failure: ' + error_message
                        results_df = results_df.append(result_row, ignore_index=True)
                    else:
                        children_added_count += 1
                        valid_children = valid_children.append(child_row, ignore_index=True)
                        # The results_df for successes will be added to due to _add_dataframe
                items_to_add.append((parent_row, valid_children))

        if error_summaries:
            status.warn(f'Failed to insert {children_failed_count} items of '
                        f'{children_added_count + children_failed_count} attempted. '
                        f'See the output dataframe for details.'
                        f'\n{_format_error_summaries(error_summaries)}')
            # We will eventually make exceptions more readable using Status objects. This is somewhat of a
            # placeholder
            if errors == 'raise':
                status.exception(SPyRuntimeError('Error encountered while inserting.'), throw=True)

        for parent_row, children_df_full in items_to_add:
            add_dataframe_results = self._add_dataframe(children_df_full, errors, quiet, status, parent_row, False)
            results_df = results_df.append(add_dataframe_results, ignore_index=True)
        _sort_by_node_path(self._dataframe)
        status.update(f'Successfully completed element insertion.',
                      _common.Status.SUCCESS)
        children_with_no_parents_found = children[~parents_found]
        children_with_no_parents_found['Result'] = 'Ignored: No matching parent found.'
        results_df = pd.concat([results_df, children_with_no_parents_found], ignore_index=True)

        self.summarize()
        return results_df

    def remove(self, elements, *, errors=None, quiet=None, status=None):
        """
        Remove the specified elements from the tree recursively.

        Parameters
        ----------
        elements : {pandas.DataFrame, str, int}
            Defines which element or elements will be removed.
            1) String name match (case-insensitive equality, globbing, regex, column
                values) will find any existing nodes in the tree that match.
            2) String path match, including partial path matches.
            3) ID. This can either be the actual ID of the tree.push()ed node or the
                ID of the source item.
            4) Number specifying tree level. This will add the children below every
                node at the specified level in the tree (1 being the root node).
            5) spy.search results or other custom dataframe.

        errors : {'raise', 'catalog'}, optional
            If 'raise', any errors encountered will cause an exception. If 'catalog',
            errors will be added to a 'Result' column in the status.df DataFrame. This
            input will be used only for the duration of this function; it will default
            to the setting on the Tree if not specified.

        quiet : bool, optional
            If True, suppresses progress output. This input will be used only for the
            duration of this function; it will default to the setting on the Tree if
            not specified. Note that when status is provided, the quiet setting of
            the Status object that is passed in takes precedent.

        status : spy.Status, optional
            If specified, the supplied Status object will be updated as the command
            progresses. It gets filled in with the same information you would see
            in Jupyter in the blue/green/red table below your code while the
            command is executed. The table itself is accessible as a DataFrame via
            the status.df property.
        """
        errors = self._get_or_default_errors(errors)
        quiet = self._get_or_default_quiet(quiet)
        status = _common.Status.validate(status, quiet)
        # TODO CRAB-24292 Allow removing nodes
        raise SPyValueError('Removing is not currently supported')

        _validate(self._dataframe)
        self.summarize()

    def move(self, source, *, destination=None, errors=None, quiet=None, status=None):
        """
        Move the specified elements (and all children) from one location in
        the tree to another.

        Parameters
        ----------
        source : {pandas.DataFrame, str}
            Defines which element or elements will be removed.
            1) String path match.
            2) ID. This can either be the actual ID of the tree.push()ed node or the
                ID of the source item.
            3) spy.search results or other custom dataframe.
            4) Another SPy Tree.

        destination : {pandas.DataFrame, str}; optional
            Defines which element or elements will be removed.
            1) No destination specified will move the elements to just below
              the root of the tree.
            2) String path match.
            3) ID. This can either be the actual ID of the tree.push()ed node or the
                ID of the source item.
            4) spy.search results or other custom dataframe.
            5) Another SPy Tree (root).

        errors : {'raise', 'catalog'}, optional
            If 'raise', any errors encountered will cause an exception. If 'catalog',
            errors will be added to a 'Result' column in the status.df DataFrame. This
            input will be used only for the duration of this function; it will default
            to the setting on the Tree if not specified.

        quiet : bool, optional
            If True, suppresses progress output. This input will be used only for the
            duration of this function; it will default to the setting on the Tree if
            not specified. Note that when status is provided, the quiet setting of
            the Status object that is passed in takes precedent.

        status : spy.Status, optional
            If specified, the supplied Status object will be updated as the command
            progresses. It gets filled in with the same information you would see
            in Jupyter in the blue/green/red table below your code while the
            command is executed. The table itself is accessible as a DataFrame via
            the status.df property.
        """
        errors = self._get_or_default_errors(errors)
        quiet = self._get_or_default_quiet(quiet)
        status = _common.Status.validate(status, quiet)
        # TODO CRAB-24293 Allow moving nodes
        _validate(self._dataframe)
        raise SPyValueError('Moving is not currently supported')
        self.summarize()

    @property
    def size(self):
        """
        Property that gives the number of elements currently in the tree.
        """
        return len(self._dataframe)

    def __len__(self):
        return self.size

    @property
    def height(self):
        """
        Property that gives the current height of the tree. This is the length
        of the longest item path within the tree.
        """
        return self._dataframe['Depth'].max()

    def items(self):
        return self._dataframe.copy()

    def count(self, item_type=None):
        """
        Count the number of elements in the tree of each Seeq type. If item_type
        is not specified, then returns a dictionary with keys 'Asset', 'Signal',
        'Condition', 'Scalar', and 'Unknown'. If item_type is specified, then
        returns an int.

        Parameters
        ----------
        item_type : {'Asset', 'Signal', 'Condition', 'Scalar', 'Uncompiled Formula'}, optional
            If specified, then the method will return an int representing the
            number of elements with Type item_type. Otherwise, a dict will be
            returned.
        """

        simple_types = ['Asset', 'Signal', 'Condition', 'Scalar', 'Uncompiled Formula']
        if item_type:
            if not isinstance(item_type, str) or item_type.capitalize() not in (simple_types + ['Formula',
                                                                                                'Uncompiled']):
                raise SPyValueError(f'"{item_type}" is not a valid node type. Valid types are: '
                                    f'{", ".join(simple_types)}')
            if item_type in ['Uncompiled Formula', 'Uncompiled', 'Formula']:
                return sum(pd.isnull(self._dataframe['Type']) | (self._dataframe['Type'] == ''))
            else:
                return sum(self._dataframe['Type'].str.contains(item_type.capitalize(), na=False))

        def _simplify_type(t):
            if not pd.isnull(t):
                for simple_type in simple_types:
                    if simple_type in t:
                        return simple_type
            return 'Uncompiled Formula'

        return self._dataframe['Type'] \
            .apply(_simplify_type) \
            .value_counts() \
            .to_dict()

    def summarize(self, ret=False):
        """
        Generate a human-readable summary of the tree.

        Parameters
        ----------
        ret : bool, default False
            If True, then this method returns a string summary of the tree. If
            False, then this method prints the summary and returns nothing.
        """
        counts = self.count()

        def _get_descriptor(k, v):
            singular_descriptors = {
                key: key.lower() if key != 'Unknown' else 'calculation whose type has not yet been determined'
                for key in counts.keys()
            }
            plural_descriptors = {
                key: f'{key.lower()}s' if key != 'Unknown' else 'calculations whose types have not yet been determined'
                for key in counts.keys()
            }
            if v == 1:
                return singular_descriptors[k]
            else:
                return plural_descriptors[k]

        nonzero_counts = {k: v for k, v in counts.items() if v != 0}
        if len(nonzero_counts) == 1:
            count_string = ''.join([f'{v} {_get_descriptor(k, v)}' for k, v in nonzero_counts.items()])
        elif len(nonzero_counts) == 2:
            count_string = ' and '.join([f'{v} {_get_descriptor(k, v)}' for k, v in nonzero_counts.items()])
        elif len(nonzero_counts) > 2:
            count_string = ', '.join([f'{v} {_get_descriptor(k, v)}' for k, v in nonzero_counts.items()])
            last_comma = count_string.rfind(',')
            count_string = count_string[:last_comma + 2] + 'and ' + count_string[last_comma + 2:]

        root_name = self._dataframe.iloc[0]['Name']

        summary = f'The tree "{root_name}" has height {self.height} and contains {count_string}.'

        if ret:
            return summary
        else:
            print(summary)

    def missing_items(self, return_type='print'):
        """
        Identify elements that may be missing child elements based on the contents of other sibling nodes.

        Parameters
        ----------
        return_type : {'print', 'string', 'dict'}, default 'print'
            If 'print', then a string that enumerates the missing items will be
            printed. If 'string', then that same string will be returned and not
            printed. If 'dict', then a dictionary that maps element paths to lists
            of their potential missing children will be returned.
        """
        if return_type.lower() not in ['print', 'str', 'string', 'dict', 'dictionary', 'map']:
            raise SPyValueError(f"Illegal argument {return_type} for return_type. Acceptable values are 'print', "
                                f"'string', and 'dict'.")
        return_type = return_type.lower()

        if self.count(item_type='Asset') == self.size:
            missing_string = 'There are no non-asset items in your tree.'
            if return_type in ['dict', 'dictionary', 'map']:
                return dict()
            elif return_type == 'print':
                print(missing_string)
                return
            else:
                return missing_string

        repeated_grandchildren = dict()

        prev_row = None
        path_stack = []
        for row in self._dataframe.itertuples():
            if prev_row is None:
                pass
            elif row.Depth > prev_row.Depth:
                path_stack.append((prev_row, set()))
            else:
                path_stack = path_stack[:row.Depth - 1]
            if len(path_stack) > 1:
                grandparent, grandchildren_set = path_stack[-2]
                if row.Name in grandchildren_set:
                    repeated_grandchildren.setdefault(grandparent, set()).add(row.Name)
                else:
                    grandchildren_set.add(row.Name)
            prev_row = row

        missing_item_map = dict()
        path_stack = []
        for row in self._dataframe.itertuples():
            if prev_row is None:
                pass
            elif row.Depth > prev_row.Depth:
                if path_stack and path_stack[-1][0] in repeated_grandchildren:
                    required_children = repeated_grandchildren[path_stack[-1][0]].copy()
                else:
                    required_children = set()
                path_stack.append((prev_row, required_children))
            else:
                for parent, required_children in path_stack[row.Depth - 1:]:
                    if len(required_children) != 0:
                        missing_item_map[_get_full_path(parent._asdict())] = sorted(required_children)
                path_stack = path_stack[:row.Depth - 1]
            if len(path_stack) != 0:
                _, required_children = path_stack[-1]
                required_children.discard(row.Name)
            prev_row = row
        for parent, required_children in path_stack:
            if len(required_children) != 0:
                missing_item_map[_get_full_path(parent._asdict())] = sorted(required_children)

        if return_type in ['dict', 'dictionary', 'map']:
            return missing_item_map

        if len(missing_item_map):
            missing_string = 'The following elements appear to be missing:'
            for parent_path, missing_children in missing_item_map.items():
                missing_string += f"\n{parent_path} is missing: {', '.join(missing_children)}"
        else:
            missing_string = 'No items are detected as missing.'

        if return_type == 'print':
            print(missing_string)
        else:
            return missing_string

    def push(self, *, errors=None, quiet=None, status=None):
        """
        Imports the tree into Seeq Server.

        errors : {'raise', 'catalog'}, optional
            If 'raise', any errors encountered will cause an exception. If 'catalog',
            errors will be added to a 'Result' column in the status.df DataFrame. This
            input will be used only for the duration of this function; it will default
            to the setting on the Tree if not specified.

        quiet : bool, optional
            If True, suppresses progress output. This input will be used only for the
            duration of this function; it will default to the setting on the Tree if
            not specified. Note that when status is provided, the quiet setting of
            the Status object that is passed in takes precedent.

        status : spy.Status, optional
            If specified, the supplied Status object will be updated as the command
            progresses. It gets filled in with the same information you would see
            in Jupyter in the blue/green/red table below your code while the
            command is executed. The table itself is accessible as a DataFrame via
            the status.df property.
        """
        errors = self._get_or_default_errors(errors)
        quiet = self._get_or_default_quiet(quiet)
        status = _common.Status.validate(status, quiet)
        error_summaries, error_details, num_bad_nodes = _validate(self._dataframe)
        if num_bad_nodes and errors == 'raise':
            status.exception(SPyRuntimeError(_format_error_summaries(error_summaries)), throw=True)

        push_results = _push.push(metadata=self._dataframe, workbook=self._workbook, errors=errors, quiet=quiet,
                                  status=status)
        for index, row in push_results.iterrows():
            # Save the ID and Type for each of the pushed rows back to the internal dataframe
            pushed_dict = _convert_dataframe_row_to_tree_dict(row, push_results.columns, '', True,
                                                              None, None, None)
            row_selection = ((self._dataframe['Path'] == pushed_dict['Path']) &
                             (self._dataframe['Name'] == pushed_dict['Name']))
            if 'ID' in row and not pd.isna(row['ID']):
                self._dataframe.loc[row_selection, 'ID'] = pushed_dict['ID']
            if 'Type' in row and not pd.isna(row['Type']):
                self._dataframe.loc[row_selection, 'Type'] = pushed_dict['Type']
        return push_results

    def _repr_html_(self):
        # noinspection PyProtectedMember
        return self._dataframe._repr_html_()

    def __iter__(self):
        return self._dataframe.itertuples(index=False, name='Item')

    def _find_workbook_id(self, quiet, status):
        """
        Set the _workbook_id based on the workbook input. This will enable us to know whether we should set
        the `ID` or `Referenced ID` column when pulling an item.
        """
        if _common.is_guid(self._workbook):
            self._workbook_id = _common.sanitize_guid(self._workbook)
        elif self._workbooks_api:
            search_query, _ = _push.create_analysis_search_query(self._workbook)
            search_df = spy.workbooks.search(search_query,
                                             quiet=quiet,
                                             status=status.create_inner('Find Workbook', quiet=quiet))
            self._workbook_id = search_df.iloc[0]['ID'] if len(search_df) > 0 else _common.EMPTY_GUID
        else:
            self._workbook_id = _common.EMPTY_GUID

    def _validate(self):
        error_summaries_properties, error_details_properties = self._validate_properties()
        error_summaries_tree, error_details_tree = self._validate_tree()

        error_string = None
        if error_summaries_properties or error_summaries_tree:
            error_string = f'{len(error_details_properties) + len(error_details_tree)} errors were found in the tree.\n'
            error_string += '\n- '.join(error_summaries_properties + error_summaries_tree)

        error_dataframe = None
        if len(error_details_properties) or len(error_details_tree):
            error_dataframe = pd.concat([error_details_properties, error_details_tree])

        return error_string, error_dataframe

    def _validate_properties(self):
        # TODO CRAB-24294, CRAB-24296 Validate dataframe rows by properties
        return [], pd.DataFrame()

    def _validate_tree(self):
        # TODO CRAB-24295 Validate tree structure
        return [], pd.DataFrame()

    def _pull_node_recursively(self, node_id, errors, quiet, status, root_path=None):
        """
        Given the ID of an Item, pulls that node and all children recursively and places it into the tree at the
        specified path.
        """
        if not self._items_api or not self._formulas_api:
            e = SPyRuntimeError('Not logged in. Execute spy.login() before calling this function.')
            status.exception(e, throw=True)
        # Get the requested node itself
        root_node_dict = _pull_node_as_tree_dict(self._items_api, self._formulas_api, self._workbook_id,
                                                 node_id, root_path, status)
        if not root_node_dict:
            return
        is_pulled_tree_from_spy = not pd.isna(root_node_dict['ID'])
        self._dataframe = self._dataframe.append(root_node_dict, ignore_index=True)
        self._dataframe, pull_results = _pull_all_children_of_node(self._dataframe, node_id, root_node_dict['Name'],
                                                                   False, is_pulled_tree_from_spy, self._workbook_id,
                                                                   errors, status)
        status.update(f"Recursively pulled {'SPy-created' if is_pulled_tree_from_spy else 'existing'} "
                      f"asset tree:\n{self.summarize()}", _common.Status.SUCCESS)

    def _add_dataframe(self, dataframe_input, errors, quiet, status, parent=None, is_pulled_tree_from_spy=False):
        """
        Adds the the contents of the dataframe below the root_path. If more than one row is supplied,
        the `Path` and/or `Asset` columns must be present such that this can form a valid tree.
        Any rows that include an `ID` will have all children recursively pulled in.
        Assets will be implicitly generated if there is no row corresponding to a node in any row's path.
        If all rows' paths begin identically, the identical leading nodes will be trimmed (so if you
        were to spy.search for 'Area [AB]_.*' signals, the root node would be 'Cooling Tower 1' rather
        than 'Example').
        """

        if 'Scoped To' in dataframe_input.columns:
            is_pulled_tree_from_spy = is_pulled_tree_from_spy | dataframe_input['Scoped To'].apply(
                lambda row_scope: (isinstance(row_scope, str)) & (row_scope == self._workbook_id)).all()
        parent_path = '' if parent is None else _get_full_path(parent)

        # working_df should be the same format as the self._dataframe, but may not be fully valid until later.
        working_df = self._dataframe.copy()
        # results_df keeps track of each inserted node and status of that insertion.
        results_df = pd.DataFrame(columns=_dataframe_columns + ['Result'])

        nodes_added_count = 0
        nodes_failed_count = 0

        for index, row in dataframe_input.iterrows():
            try:
                child_node_dict = _convert_dataframe_row_to_tree_dict(row, dataframe_input.columns, parent_path,
                                                                      is_pulled_tree_from_spy, self._items_api,
                                                                      self._formulas_api, self._workbook_id)
                working_df, row_error = _validate_and_upsert_node(working_df, child_node_dict)
                if row_error:
                    nodes_failed_count += 1
                    child_node_dict['Result'] = 'Failure: ' + row_error
                else:
                    nodes_added_count += 1
                    child_node_dict['Result'] = 'Success'
                results_df = results_df.append(child_node_dict, ignore_index=True)
                status.update(f'Successfully inserted {nodes_added_count} elements of '
                              f'{nodes_added_count + nodes_failed_count}.', _common.Status.RUNNING)
            except ValueError as e:
                nodes_failed_count += 1
                child_node_dict = row.to_dict()
                child_node_dict['Result'] = f'Failure: {e}'
                results_df = results_df.append(child_node_dict, ignore_index=True)

        if parent is None:
            # This is called from the constructor (rather than insert) so automatically take care of assets.
            # This process should be done before calling _add_dataframe() when called from insert.
            working_df = _trim_unneeded_paths(working_df)
            working_df, reify_results_df = _reify_missing_assets(working_df)
            results_df = results_df.append(reify_results_df, ignore_index=True)

        if nodes_failed_count:
            status.warn(f'Failed to insert {nodes_failed_count} items of '
                        f'{nodes_added_count + nodes_failed_count} attempted. '
                        f'See the output dataframe for details.')
            status.df = results_df
            # We will eventually make exceptions more readable using Status objects. This is somewhat of a
            # placeholder
            if errors == 'raise':
                status.exception(SPyRuntimeError('Error encountered while inserting.'), throw=True)
        else:
            status.update(f'Successfully inserted {nodes_added_count} elements without any failures.',
                          _common.Status.SUCCESS)
        working_df, pull_results = _pull_all_children_of_all_nodes(working_df, is_pulled_tree_from_spy,
                                                                   self._workbook_id, quiet, errors, status)
        results_df = results_df.append(pull_results, ignore_index=True)
        self._dataframe = working_df
        _sort_by_node_path(self._dataframe)
        status.update(f"Completed addition of {len(results_df[results_df['Result'] == 'Success'])} elements."
                      f"\n{self.summarize()}", _common.Status.SUCCESS)
        return results_df

    def _get_or_default_errors(self, errors_input):
        if isinstance(errors_input, str):
            _common.validate_errors_arg(errors_input)
            return errors_input
        return self.errors

    def _get_or_default_quiet(self, quiet_input):
        if isinstance(quiet_input, bool):
            return quiet_input
        return self.quiet


def _sort_by_node_path(df):
    _decorate_with_full_path(df)
    df.sort_values(by='Full Path List', inplace=True, ignore_index=True)
    _remove_full_path(df)


def _decorate_with_full_path(df):
    """
    From the 'Path' and 'Name' columns, add a 'Full Path List' column.
    """
    df['Full Path List'] = df.apply(lambda node: _common.path_string_to_list(_get_full_path(node)), axis=1)


def _remove_full_path(df):
    """
    Remove the 'Full Path List' column.
    """
    df.drop('Full Path List', axis=1, inplace=True)


def _update_path_from_full_path_list(df):
    """
    From the 'Full Path List' column, set the 'Path' column.
    """
    df['Path'] = df.apply(lambda node: _common.path_list_to_string(node['Full Path List'][:-1]), axis=1)


def _trim_unneeded_paths(df, parent_full_path=None, maintain_last_shared_root=None):
    """
    Remove any leading parts of the path that are shared across all rows. Then add the parent_path back onto the
    front of the path.

    E.G. If all rows have a path of 'USA >> Texas >> Houston >> Cooling Tower >> Area {x} >> ...',
    'Cooling Tower' would become the root asset for this Tree. Then if parent_path was 'My Tree >> Cooling Tower',
    all rows would have a path 'My Tree >> Cooling Tower >> Area {x} >> ...'
    """

    def _get_shared_root(full_path_series):
        first_full_path_list = full_path_series.iloc[0]
        if not len(first_full_path_list):
            return None
        root_name = first_full_path_list[0]
        all_roots_same = full_path_series.apply(lambda l: len(l) and l[0] == root_name).all()
        return root_name if all_roots_same else None

    if len(df) == 0:
        return df

    # Get the path of the first node. It doesn't matter which we start with since we're only removing paths that are
    # shared across ALL rows.
    _decorate_with_full_path(df)
    shared_root = _get_shared_root(df['Full Path List'])
    # Trim the path until we're left with the last universally shared node.
    while shared_root:
        trimmed_full_path_list = df['Full Path List'].apply(lambda l: l[1:])
        remaining_shared_root = _get_shared_root(trimmed_full_path_list)
        keep_last_shared_root = True
        if parent_full_path and remaining_shared_root:
            # We only want to remove the root-most path if it is already going to be the parent (due to insert)
            parent_name = _common.path_string_to_list(parent_full_path)[-1]
            keep_last_shared_root = remaining_shared_root != parent_name
        elif parent_full_path and shared_root and isinstance(maintain_last_shared_root, bool):
            # We explicitly want to remove the last shared root so it can be replaced.
            keep_last_shared_root = maintain_last_shared_root
        if not remaining_shared_root and keep_last_shared_root:
            # We need to keep the last shared root so do not save trimmed_full_path_list
            break
        df['Full Path List'] = trimmed_full_path_list
        if 'Depth' in df:
            df['Depth'] -= 1
        shared_root = remaining_shared_root

    if parent_full_path:
        # Prepend the parent path if applicable
        parent_path_list = _common.path_string_to_list(parent_full_path)
        parent_name = parent_path_list[-1]
        if _get_shared_root(df['Full Path List']) == parent_name:
            parent_path_list.pop()
        if parent_path_list:
            df['Full Path List'] = df['Full Path List'].apply(lambda l: parent_path_list + l)
            if 'Depth' in df:
                df['Depth'] += len(parent_path_list)
    _update_path_from_full_path_list(df)
    _remove_full_path(df)
    return df


def _reify_missing_assets(df, existing_parent_path=None):
    """
    Automatically generate any assets that are referred to by path only.
    E.G. If this tree were defined using a dataframe containing only leaf signals, but with a Path column of
    'Cooling Tower >> Area {x} >> {signal}', the 'Cooling Tower' and 'Area {x}' assets would be generated.

    If existing_parent_path is provided, the reification will not occur for any existing parents.
    E.G. 'Example >> Cooling Tower >> Area {x} >> {signal}' with existing_parent_path='Example'
     would only generate 'Cooling Tower' and 'Area {x}' assets, not 'Example'.
    """
    results_df = pd.DataFrame(columns=_dataframe_columns + ['Result'])
    for index, row in df.iterrows():
        missing_assets = list()
        path_list = _common.path_string_to_list(row['Path'])
        for i in range(len(path_list)):
            path = _common.path_list_to_string(path_list[:i]) if i > 0 else ''
            name = path_list[i]
            full_path = _common.path_list_to_string(path_list[:i + 1])
            if name and not ((df['Path'] == path) & (df['Name'] == name)).any() \
                    and (existing_parent_path is None or full_path not in existing_parent_path):
                missing_assets.append({'Name': name, 'Path': path})

        if missing_assets:
            for missing_asset in missing_assets:
                path = missing_asset['Path']
                asset_dict = {
                    'Type': 'Asset',
                    'Path': path,
                    'Depth': 1 if not path else path.count('>>') + 2,
                    'Name': missing_asset['Name']
                }
                df = df.append(asset_dict, ignore_index=True)
                asset_dict['Result'] = 'Success'
                results_df.append(asset_dict, ignore_index=True)
        # It's sometimes bad practice to keep iterating over a modified dataframe because iterrows() is based on the
        # original DF. This case is fine because elements from missing_assets will always be fully reified.
    return df, results_df


def _pull_all_children_of_all_nodes(df, is_pulled_tree_from_spy, workbook_id, quiet, errors, status):
    """
    For each node in the tree that contains an 'ID' or 'Referenced ID', recursively pull in any asset tree children.
    If any nodes already exist in the dataframe (by case-insensitive Path+Name), the existing row will be kept.
    """
    # Gather all Paths+IDs into a list upfront. It's bad practice to iterate over a dataframe while it's being modified.
    results_df = pd.DataFrame(columns=_dataframe_columns + ['Result'])
    items_to_pull_children = list()
    for index, row in df.iterrows():
        node_full_path = _get_full_path(row)
        if _common.is_guid(row['ID']):
            items_to_pull_children.append({'Full Path': node_full_path, 'ID': row['ID']})
        elif _common.is_guid(row['Referenced ID']):
            items_to_pull_children.append({'Full Path': node_full_path, 'ID': row['Referenced ID']})

    for item_to_pull in items_to_pull_children:
        df, pull_results = _pull_all_children_of_node(df, item_to_pull['ID'], item_to_pull['Full Path'], True,
                                                      is_pulled_tree_from_spy, workbook_id, errors, status)
        results_df = results_df.append(pull_results, ignore_index=True)
    return df, results_df


def _pull_all_children_of_node(df, node_id, node_full_path, prefer_existing_rows, is_pulled_tree_from_spy,
                               workbook_id, errors, status):
    """
    Given the ID of an Item in an asset tree, pulls all children recursively and places it into the
    tree below parent_path.
    """
    status.update(f"Recursively pulling {'SPy-created' if is_pulled_tree_from_spy else 'existing'} "
                  f"asset tree below '{node_full_path}' ({node_id}).", _common.Status.RUNNING)

    insert_df = pd.DataFrame(columns=_dataframe_columns)
    results_df = pd.DataFrame(columns=_dataframe_columns + ['Result'])
    # Get all children of the requested asset
    search_results = _search.search(query={'Asset': node_id}, all_properties=True, workbook=workbook_id,
                                    status=status.create_inner('Find Children', quiet=True))
    status.update(f"Found a total of {len(search_results)} elements in the tree below '{node_full_path}' ({node_id}).",
                  _common.Status.RUNNING)
    if len(search_results) == 0:
        return df, results_df

    # Step 1: Convert the search results dataframe into a Tree-style dataframe. The empty parent path enables Step 2.
    for index, row in search_results.iterrows():
        insert_dict = _convert_dataframe_row_to_tree_dict(row, search_results.columns, '',
                                                          is_pulled_tree_from_spy, None, None, None)
        insert_df = insert_df.append(insert_dict, ignore_index=True)

    # Step 2: If the node_id's original name does not match what the node's name is in the Tree, trim off any extra
    # path from the input.
    _decorate_with_full_path(insert_df)
    parent_name = _common.path_string_to_list(node_full_path)[-1]
    if parent_name:
        maintain_last_shared_root = parent_name in insert_df.iloc[0]['Full Path List']
        insert_df = _trim_unneeded_paths(insert_df, node_full_path, maintain_last_shared_root)

    # Step 3: Actually insert the nodes
    for index, row in insert_df.iterrows():
        child_node_dict = row.to_dict()
        try:
            df, did_upsert = _upsert_node(df, child_node_dict, prefer_existing_rows)
            child_node_dict['Result'] = 'Success'
            if did_upsert:
                results_df = results_df.append(child_node_dict, ignore_index=True)
        except ValueError as e:
            if errors == 'raise':
                status.exception(e, throw=True)
            child_node_dict['Result'] = f'Failure: {e}'
            results_df = results_df.append(child_node_dict, ignore_index=True)
    status.update(f"Pulled {len(df)} elements so far.", _common.Status.RUNNING)
    return df, results_df


def _upsert_node(df, node, prefer_existing_row):
    """
    Either insert or update the dataframe that's uniquely identified by the `node`'s Path and Name
    (case-insensitive). If prefer_existing_row=True, an existing row matching the Path+Name will not be altered.
    """
    path_to_compare = ''
    if 'Path' in node and node['Path']:
        path_to_compare = node['Path'].lower()
    existing_row_indices = df.index[
        (df['Path'].str.lower() == path_to_compare) & (df['Name'].str.lower() == node['Name'].lower())].tolist()
    did_upsert = False
    if len(existing_row_indices) == 1 and not prefer_existing_row:
        # The node already exists in the dataframe and we want to update it.
        index = existing_row_indices[0]
        for column in _dataframe_columns:
            if column in node:
                df[column][index] = node[column]
        did_upsert = True
    elif len(existing_row_indices) == 0:
        # The node doesn't exist so add it.
        if node['Depth'] == 1 and df['Depth'].min() == 1:
            existing_root = df[df['Depth'] == 1]['Name']
            raise SPyValueError(f"The tree may not have multiple root elements. Attempted to set '{node['Name']}' and "
                                f"'{existing_root}' as roots. Please try again with unambiguous input.")
        df = df.append(node, ignore_index=True)
        did_upsert = True
    elif len(existing_row_indices) > 1:
        # The dataframe somehow got into an invalid state. Error.
        raise SPyValueError(
            f"The tree is in an invalid state. More than one existing '{node['Name']}' element was found "
            f"at path '{node['Path']}'. Please recreate this tree anew or contact Seeq support if this "
            f"error persists.")
    return df, did_upsert


def _validate_and_upsert_node(df, node):
    """
    Validate and perform an insertion.

    :param df: The dataframe representing a tree object into which the insertions will be made
    :param node: A dataframe row to be inserted (without modification) into df
    :return: out_df: The updated dataframe if the insertion was valid or the unchanged dataframe if not
    :return: error_message: A string summarizing all errors encountered while validating the insertion
    :return: did_upsert: True if an insert or update was performed
    """
    error_message = _validate_properties_single_node(node)
    if not error_message:
        try:
            df, _ = _upsert_node(df, node, False)
        except ValueError as e:
            error_message = str(e)
    return df, error_message


def _validate_insertion(df, insertions, insertion_index):
    """
    Validate that a collection of rows to be inserted into a dataframe representing an asset tree will not put that
    tree into a bad state.

    :param df: The dataframe representing the tree that is being operated on
    :param insertions: A dataframe of rows that will be tentatively inserted into df
    :return: error_summaries: A list of strings summarizing all errors encountered while validating the insertions
    :return: error_details: A pd.Series object whose index is the same as `insertions` and whose data specifies
    errors specific to the corresponding row in `insertions`
    :return: num_success: Integer specifying the number of insertions that can be performed successfully
    :return: num_failure: Integer specifying the number of insertions that would put the tree in a bad state
    """
    error_summaries_properties, error_details_properties = _validate_properties(insertions)
    error_summaries_tree, error_details_tree = _validate_insertion_tree_structure(df, insertions, insertion_index)

    error_summaries = error_summaries_properties + error_summaries_tree
    error_details = _update_error_msg(error_details_properties, error_details_tree)

    num_failure = len(error_details[error_details != ''].index)
    num_success = len(error_details.index) - num_failure

    return error_summaries, error_details, num_success, num_failure


def _validate_insertion_tree_structure(df, insertions, insertion_index):
    # Check:
    # - That the 'Path' and 'Depth' columns reflect that performing the insertions will maintain a DFS tree traversal
    # order when inserted into df
    # - That no parent node has two children with the same name (so paths are unambiguous)
    # - Will check more when we introduce Calculations and Stored Items, not just bare Assets
    # Assumptions:
    # - df represents a valid asset tree
    # - All nodes in `insertions` are intended to lie below the parent node df.iloc[insertion_index] after being
    # inserted

    num_insertions = len(insertions)
    if num_insertions == 0:
        return [], pd.Series()
    error_series = pd.Series([''] * len(insertions))

    insertion_parent = df.iloc[insertion_index]
    _validate_tree_rec(parent=insertion_parent, node_df=insertions, current_index=0, num_nodes=num_insertions,
                       error_series=error_series,
                       root=True, dead_path_msg='Node\'s parent could not be inserted.')

    error_summaries = _write_error_summaries(insertions, error_series,
                                             'Attempted to insert a node with path "{}" and name "{}":')

    return error_summaries, error_series


def _validate(df):
    """
    Validate that df represents a valid asset tree that can be pushed to Workbench

    CAUTION: Use this function sparingly. We ideally do not want to have to iterate through the entire dataframe each
    time we invoke a method on a Tree object. If at all possible, use this validation function and its
    subfunctions as a template for writing functions that validate specific methods of the Tree class.

    :param df: The dataframe representing the asset tree
    :return: error_summaries: A list of strings summarizing all errors encountered while validating the dataframe
    :return: error_details: A pd.Series object whose index is the same as df and whose data specifies errors specific
    to the corresponding row in df
    :return: num_bad_nodes: Integer specifying the number of invalid nodes found
    """
    error_summaries_properties, error_details_properties = _validate_properties(df)
    error_summaries_tree, error_details_tree = _validate_tree_structure(df)

    error_summaries = error_summaries_properties + error_summaries_tree
    error_details = _update_error_msg(error_details_properties, error_details_tree)

    num_bad_nodes = len(error_details[error_details != ''].index)

    return error_summaries, error_details, num_bad_nodes


def _validate_tree_structure(df):
    # Check:
    # - That the 'Path' and 'Depth' columns reflect that the order of the nodes in df specify a DFS tree traversal order
    # - Will check more when we introduce Calculations and Stored Items, not just bare Assets
    # Assumptions:
    # - None currently

    size = len(df)
    if size == 0:
        return ['Tree must be non-empty.'], pd.Series()
    error_series = pd.Series([''] * len(df))

    root_node = df.iloc[0]
    if not _is_valid_root_path(root_node['Path']):
        error_series.iloc[0] = f'The root of the tree has the following malformed path: "{root_node["Path"]}".'
        dead_tree = True
    else:
        dead_tree = False

    _validate_tree_rec(parent=root_node, node_df=df, current_index=1, num_nodes=size, error_series=error_series,
                       dead_path=dead_tree, root=True)

    error_summaries = _write_error_summaries(df, error_series,
                                             'Invalid node with path "{}" and name "{}":')

    return error_summaries, error_series


def _validate_tree_rec(parent, node_df, current_index, num_nodes, error_series, dead_path=False, root=False,
                       dead_path_msg="Node's parent is invalid."):
    while current_index < num_nodes and (node_df.iloc[current_index]['Depth'] > parent['Depth'] or root):
        child = node_df.iloc[current_index]
        if dead_path:
            error_message = dead_path_msg
        else:
            error_message = _validate_parent_child_relationship(parent, child)
        error_series[current_index] = _update_error_msg(error_series[current_index], error_message)
        current_index = _validate_tree_rec(child, node_df, current_index + 1, num_nodes, error_series,
                                           dead_path=dead_path or error_message,
                                           root=False,
                                           dead_path_msg=dead_path_msg)
    return current_index


def _write_error_summaries(data, error_series, summary_header_format):
    error_headers = pd.Series({
        i: summary_header_format.format(data.loc[i]['Path'], data.loc[i]['Name'])
        if error_series[i] != '' else '' for i in data.index
    }, dtype=str, index=data.index)
    full_errors = _update_error_msg(error_headers, error_series)
    return full_errors[full_errors != ''].tolist()


def _validate_parent_child_relationship(parent, child):
    if child['Path'] != _get_full_path(parent):
        return f"Node's parent has mismatching path. Full path of invalid parent: '{_get_full_path(parent)}'."
    elif child['Depth'] != parent['Depth'] + 1:
        return f"Node's depth must be one more than the depth of its parent. Node depth: " \
               f"{child['Depth']}. Depth of parent: {parent['Depth']}."
    else:
        return None


def _validate_properties(df):
    # TODO CRAB-24294, CRAB-24296 Validate dataframe rows by properties
    return [], pd.Series(pd.Series([''] * len(df)))


def _validate_properties_single_node(item):
    # TODO CRAB-24294, CRAB-24296 Validate dataframe rows by properties
    return ''


def _update_error_msg(old_msg, new_msg):
    if new_msg is None or isinstance(new_msg, str) and new_msg == '':
        return old_msg
    out = old_msg + ' ' + new_msg
    if isinstance(out, pd.Series):
        return out.str.strip()
    else:
        return out.strip()


def _format_error_summaries(error_summaries):
    if len(error_summaries) == 0:
        return None
    else:
        return '- ' + '\n- '.join(error_summaries)


def _get_full_path(node):
    if 'Path' in node and isinstance(node['Path'], str) and node['Path']:
        return f"{node['Path']} >> {node['Name']}"
    else:
        return node['Name']


def _is_valid_root_path(path):
    try:
        if np.isnan(path):
            return True
    except TypeError:
        return path is None or path == ''


def _node_match_string_to_regex(pattern):
    """
    :param pattern: String name match (case-insensitive equality, globbing, regex, column values)
                    or string path match (full or partial; case-insensitive equality, globbing, or regex)
    :return: A regular expression that matches correctly on f"{node['Path']} >> {node['Name']}"
    """
    # TODO: CRAB-24298 incorporate column values into this regex match
    # This will require using groups to sort of invert the column value matching -- this will be a little
    # difficult to logic through, but will make it so we don't have to iterate through self._dataframe more
    # than once during an insert
    patterns = _common.path_string_to_list(pattern)
    return [_exact_or_glob_or_regex(p) for p in patterns]


def _exact_or_glob_or_regex(pat):
    try:
        re.compile(pat)
        return re.compile('(?i)' + '(' + ')|('.join([re.escape(pat), fnmatch.translate(pat), pat]) + ')')
    except re.error:
        return re.compile('(?i)' + '(' + ')|('.join([re.escape(pat), fnmatch.translate(pat)]) + ')')


def _node_match_using_regex(node, pattern_list):
    path_list = _common.path_string_to_list(_get_full_path(node))
    offset = len(path_list) - len(pattern_list)
    if offset < 0:
        return None
    out = []
    for i in range(len(pattern_list)):
        match = pattern_list[i].fullmatch(path_list[offset + i])
        if match is None:
            return None
        out.append(match)
    return out


def _node_match_no_regex(node, pattern):
    if pattern is None:
        return node['Depth'] == 1
    if isinstance(pattern, int):
        return node['Depth'] == pattern
    if isinstance(pattern, pd.DataFrame):
        # TODO CRAB-24290 Insert with parents & children defined by dataframes
        return False
    if isinstance(pattern, str):
        if isinstance(node['ID'], str) and pattern.upper() == node['ID'].upper():
            return True
        if isinstance(node['Referenced ID'], str) and pattern.upper() == node['Referenced ID'].upper():
            return True
    return False


def _find_existing_root_node_id(name, status, trees_api=None, workbook_id=None):
    """
    Finds the Seeq ID of a case-insensitive name match of existing root nodes.
    """
    if not trees_api:
        # User is not logged in or this is a unit test. We must create a new tree.
        return None
    name_pattern = re.compile('(?i)^' + re.escape(name) + '$')
    matching_root_nodes = list()

    offset = 0
    limit = _config.options.search_page_size
    kwargs = dict()
    # Can't use get_tree_root_nodes()'s `properties` filter for scoped_to because the endpoint is case-sensitive and
    # we want both global and scoped nodes.
    if workbook_id and workbook_id is not _common.EMPTY_GUID:
        kwargs['scoped_to'] = workbook_id

    status.update('Finding best root.', _common.Status.RUNNING)
    keep_going = True
    while keep_going:
        kwargs['offset'] = offset
        kwargs['limit'] = limit
        root_nodes = trees_api.get_tree_root_nodes(**kwargs)  # type: AssetTreeOutputV1
        for root_node in root_nodes.children:  # type: TreeItemOutputV1
            if name_pattern.match(root_node.name):
                # A root node matching the name was already found. Choose a best_root_node based on this priority:
                # Workbook-scoped SPy assets > workbook-scoped assets > global SPy assets > global assets
                has_scope = hasattr(root_node, 'scoped_to') and _common.is_guid(root_node.scoped_to)
                workbook_scoped_score = 2 if has_scope else 0
                spy_created_score = 0
                if hasattr(root_node, 'properties'):
                    for prop in root_node.properties:  # type: PropertyOutputV1
                        if prop.name == 'Datasource Class' and prop.value == 'Seeq Data Lab':
                            spy_created_score = 1
                            break
                matching_root_nodes.append({'id': root_node.id, 'score': workbook_scoped_score + spy_created_score})

        status.update(f'Finding best root. {len(matching_root_nodes)} matches out of {offset + limit} roots requested.',
                      _common.Status.RUNNING)
        keep_going = root_nodes.next is not None
        offset = offset + limit
    if len(matching_root_nodes) == 0:
        status.update(f"No existing root items were found matching '{name}'.", _common.Status.RUNNING)
        return None
    best_score = max([n['score'] for n in matching_root_nodes])
    best_root_nodes = list(filter(lambda n: n['score'] == best_score, matching_root_nodes))
    if len(best_root_nodes) > 1:
        e = SPyValueError(
            f"More than one existing tree was found with name '{name}'. Please use an ID to prevent ambiguities.")
        status.exception(e, throw=True)
    best_id = best_root_nodes[0]['id']
    if len(matching_root_nodes) > 1:
        status.update(f"{len(matching_root_nodes)} root items were found matching '{name}'. Selecting {best_id}.",
                      _common.Status.RUNNING)
    return best_id


def _add_tree_property(properties, key, value):
    """
    If the property is one which is used by SPy Trees, adds the key+value pair to the dict.
    """
    if key in _dataframe_columns:
        value = _common.none_to_nan(value)
        if isinstance(value, str) and key in ['Cache Enabled', 'Archived', 'Enabled', 'Unsearchable']:
            # Ensure that these are booleans. Otherwise Seeq Server will silently ignore them.
            value = (value.lower() == 'true')
        if key not in properties or not pd.isnull(value):
            properties[key] = value
    return properties


def _node_sort_key(node):
    out = []
    if _common.present(node, 'Path') and isinstance(node['Path'], str) and node['Path'] != '':
        out += _common.path_string_to_list(node['Path'])
    if _common.present(node, 'Asset') and isinstance(node['Asset'], str) and node['Asset'] != '':
        out.append(node['Asset'].strip())
    if _common.present(node, 'Name'):
        out.append(node['Name'].strip())
    return out


def _pull_node_as_tree_dict(items_api, formulas_api, workbook_id, node_id, path, status):
    """
    Given the ID of an Item, pulls that node and places it into the tree at the specified path.
    """
    if not items_api or not formulas_api:
        e = SPyRuntimeError('Not logged in. Execute spy.login() before calling this function.')
        status.exception(e, throw=True)

    node = items_api.get_item_and_all_properties(id=node_id)  # type: ItemOutputV1
    node_dict = dict()

    # Extract only the properties we use
    node_dict['Name'] = node.name
    node_dict['Type'] = node.type
    node_dict['ID'] = node.id  # If this should be a copy, it'll be converted to 'Referenced ID' later
    for prop in node.properties:  # type: PropertyOutputV1
        _add_tree_property(node_dict, prop.name, prop.value)

    # Figure out the path-related columns
    node_dict['Path'] = path if path else ''
    if node_dict['Path'] is '':
        node_dict['Depth'] = 1
    else:
        node_dict['Depth'] = node_dict['Path'].count('>>') + 2

    # If this is a referenced item, push() should make a copy instead of updating the original
    is_pulled_node_from_spy = node.scoped_to and node.scoped_to.lower() == workbook_id.lower()

    if node.type in _data_types and not is_pulled_node_from_spy:
        # Data items will be made into Reference Formulas (unless this already was a SPy-made Tree)
        _metadata._build_reference(node_dict)
    elif node.type in _calculated_types:
        # Calculated items from an existing SPy Tree will be pulled in as direct Formulas.
        formula_output = formulas_api.get_item(id=node.id)  # type: FormulaItemOutputV1
        node_dict['Formula Parameters'] = [
            '%s=%s' % (p.name, p.item.id if p.item else p.formula) for p in formula_output.parameters
        ]
    elif node.type not in _supported_input_types:
        # TODO CRAB-24637: Allow Threshold Metrics to be pulled in too.
        raise SPyValueError(
            f"Attempted to pull {node.type} '{node.name}' ({node.id}), but {node.type}s are not supported")
    if not is_pulled_node_from_spy:
        node_dict['ID'] = np.nan
        node_dict['Referenced ID'] = node.id
    return node_dict


def _convert_dataframe_row_to_tree_dict(row, input_columns, full_parent_path, is_pulled_tree_from_spy,
                                        items_api=None, formulas_api=None, workbook_id=None):
    """
    Converts a dataframe row to a dict compatible with the Tree data.
    :param row: The row from any dataframe. Must include at least the minimum require properties for the given type.
    :param input_columns: The column names from the dataframe.
    :param full_parent_path: The full path to the parent in the Tree that this row should be inserted below.
    E.G. 'Area A' in Example Data would be 'Example >> Cooling Tower 2 >> Area A'.
    :param is_pulled_tree_from_spy: True if this is getting pulled from a SPy Trees-created tree.
    :param items_api: Optional, used to look up the properties for an existing item if this is set.
    :param formulas_api: Optional, used to look up the properties for an existing item if this is set.
    :param workbook_id: Optional, used to look up the properties for an existing item if this is set.
    :return:
    """
    node_dict = dict()
    if 'ID' in input_columns and not pd.isna(row['ID']) and items_api and formulas_api:
        # If an ID has been passed in, pull the properties (but any input rows will override it later)
        node_dict = _pull_node_as_tree_dict(items_api, formulas_api, workbook_id, row['ID'], None,
                                            _common.Status(quiet=True))

    # Extract only the properties we use
    for column in input_columns:
        _add_tree_property(node_dict, column, row[column])
    if 'Type' in input_columns and not pd.isna(node_dict['Type']) and node_dict['Type'] not in _supported_input_types:
        # TODO CRAB-24637: Allow Threshold Metrics to be pulled in too.
        raise SPyValueError(
            f"Type {node_dict['Type']} is not supported. Please only use types: {_supported_input_types}")

    if 'Friendly Name' in input_columns and isinstance(row['Friendly Name'], str):
        node_dict['Name'] = row['Friendly Name']

    relative_path = _get_relative_path_from_dataframe_row(row)
    # Figure out the path of this node relative to the parent. The Path from the input row may not be the same
    # path that aligns to where this node will actually be in the Tree. Once we know the path relative to the parent,
    # we can combine it with the parent's path in the Tree to get this node's actual path.
    full_parent_path_list = _common.path_string_to_list(full_parent_path)
    parent_name = full_parent_path_list.pop()  # The name of the requested parent or empty str
    parent_path = _common.path_list_to_string(full_parent_path_list)  # The path to the requested parent or empty str
    if parent_name and (parent_name + ' >> ') in relative_path:
        relative_path = parent_name + ' >> ' + relative_path.split(parent_name + ' >> ', 1)[1]
    elif parent_name and relative_path.endswith(parent_name):
        relative_path = parent_name
    node_dict['Path'] = parent_path + (' >> ' if parent_path else '') + relative_path
    node_dict['Depth'] = node_dict['Path'].count('>>') + 2 if node_dict['Path'] else 1

    if 'Type' not in input_columns or not node_dict['Type'] or not isinstance(node_dict['Type'], str):
        if 'Formula' not in input_columns or pd.isna(node_dict['Formula']):
            node_dict['Type'] = 'Asset'
        else:
            node_dict['Type'] = np.nan

    if is_pulled_tree_from_spy:
        if 'ID' in input_columns:
            node_dict['ID'] = row['ID']
        else:
            node_dict['ID'] = np.nan
    else:
        # If we are pulling a tree that was not made by SPy, push() should make a copy instead of updating the original
        is_already_reference = 'Referenced ID' in input_columns and not pd.isna(row['Referenced ID']) and \
                               'Formula' in input_columns and not pd.isna(row['Formula']) and \
                               'Formula Parameters' in input_columns and not pd.isna(row['Formula Parameters'])
        if node_dict['Type'] in _data_types and not is_already_reference:
            _metadata._build_reference(node_dict)
        node_dict['ID'] = np.nan

        if 'ID' in input_columns and not pd.isna(row['ID']):
            node_dict['Referenced ID'] = row['ID']
    return node_dict


def _get_relative_path_from_dataframe_row(row):
    """
    Gets the path from the
    :param row: The row from any dataframe.
    """
    # Null out the values if they're not valid
    if 'Path' in row and not isinstance(row['Path'], str):
        row['Path'] = None
    if 'Asset' in row and not isinstance(row['Asset'], str):
        row['Asset'] = None
    # Combine 'Asset' and 'Path' columns if necessary.
    relative_path = ''
    if 'Path' in row and 'Asset' in row and row['Path'] and row['Asset']:
        relative_path = ' >> '.join([row['Path'], row['Asset']])
    elif 'Asset' in row and row['Asset']:
        relative_path = row['Asset']
    elif 'Path' in row and row['Path']:
        # This isn't a SPy.search dataframe
        relative_path = row['Path']
    return relative_path
