"""Module containing tools to run result analytics."""
from typing import List

import numpy as np
import pandas as pd

from .db import DB
from .db import DbModel
from .utils import LOGGER
from .utils import SECTION_DATABASE
from .utils import SECTION_PROJECT
from .utils import load_project_config


def _extract_metric_results(outcome, requested_metric):
    return outcome.apply(
        lambda row: row.apply(lambda value: value[requested_metric]))


def get_results_as_dataframe(project_name: str = None,
                             table_name: str = None,
                             filter_git_dirty=True,
                             date_filter: str = None,
                             id_filter: str = None,
                             additional_conditions: List[str] = None,
                             columns: List[str] = None) -> pd.DataFrame:
    r"""Returns the results stored in the database as a pandas dataframe.

    Args:
        project_name (str, optional): the project name to fetch results. It
            defaults to the project name given in the config.
        table_name (str, optional): the name of the result table. It defaults
            to the table name specified in the config.
        filter_git_dirty (bool, optional): defines if dirty commits are
            filtered.
        date_filter (str, optional): filter by date as a string.
            E.g. "> \'2021-01-01\'"
        id_filter (str, optional): filter by id. E.g. "= 42" or a comma
            separated list of ids.
        additional_conditions (List[str], optional): a list of strings that
            gets added to the WHERE clause using AND to combine it with other
            filters.
        columns (List[str], optional): a list of columns that should be
            returned. None equals to all.

    Returns:
        pd.DataFrame: the result as a dataframe.
    """
    if project_name is None or table_name is None:
        config = load_project_config()

    if project_name is None:
        project_name = config[SECTION_PROJECT]['name']

    if table_name is None:
        table_name = config[SECTION_DATABASE]['result_table']

    if columns is None:
        columns = '*'
    else:
        columns = ', '.join(columns)

    sql = 'SELECT %s FROM %s' % (columns, table_name)

    conditions = []
    if project_name:
        conditions.append('project_name LIKE \'%s\'' % project_name)

    if id_filter:
        if ',' in id_filter and 'in' not in id_filter.lower():
            id_filter = 'IN(' + id_filter + ')'
        conditions.append('id %s' % id_filter)
    if filter_git_dirty:
        conditions.append('git_is_dirty = FALSE')
    if date_filter:
        conditions.append('"date" %s' % date_filter)
    if additional_conditions:
        conditions = conditions + additional_conditions

    if len(conditions) > 1:
        where_conditions = ' AND '.join(conditions)
    else:
        where_conditions = conditions[0]

    if len(conditions) > 0:
        sql = sql + ' WHERE ' + where_conditions

    return pd.read_sql_query(sql, con=DB.engine)


def fetch_by_git_commit_id(git_commit_id):
    """Returns a query that is filtered by git commit id.

    Args:
        git_commit_id: the commit id of the returned results.
    """
    session = DB.session()
    return session.query(DbModel).filter(
        DbModel.git_commit_id == git_commit_id)


def fetch_by_row_ids(from_id, to_id=None):
    """Returns a query in the given range of ids.

    Args:
        from_id: the smalles database id included in the results of the query.
        to_id: if specified, this is the biggest database id included in the
            results of the query.
    """
    session = DB.session()
    query = session.query(DbModel).filter(DbModel.id >= from_id)
    if to_id is not None:
        return query.filter(DbModel.id <= to_id)
    return query


def fetch_by_project_name(project=None):
    """Returns a query filtered by project.

    Args:
        project: the name of the project to extract results. If None, the
            project in the dbispipeline.ini is used.
    """
    if project is None:
        project = load_project_config()['project']['name']

    session = DB.session()
    return session.query(DbModel).filter(DbModel.project_name == project)


def get_cv_epoch_evaluator_results(requested_metric=None,
                                   query_function=fetch_by_project_name):
    """Extracts CvEpochEvaluator results from the database.

    Args:
        requested_metric: allows to restrict the results to a single metric.
        query_function: a function returing a SQLAlchemy query when called.

    Returns: A tuple containing the prepared results as first element and the
        whole db entry as the second entry. The prepared results are eighter a
        pandas dataframe if a metric is requested or a dict containing a pandas
        dataframe per metric.
    """
    for run in query_function():
        if run.evaluator['class'] == 'CvEpochEvaluator':
            outcome = pd.DataFrame(run.outcome)

            if requested_metric is None:
                results = {}
                for available_metric in run.evaluator['scoring']:
                    results[available_metric] = _extract_metric_results(
                        outcome,
                        available_metric,
                    )
                yield results, run
            elif requested_metric in run.evaluator['scoring']:
                yield _extract_metric_results(outcome, requested_metric), run


def rows_to_dataframe(rows,
                      allow_git_different_rows=False,
                      allow_git_dirty_rows=False):
    """
    Converts database rows to a pandas DataFrame.

    args:
        rows: some object that iterates over rows. May be a query result or an
            actual list of rows. If this field is None or empty, an empty
            DataFrame will be returned.
        allow_git_dirty_rows: if set to true, allows that rows might have
            different git commit ids. Otherwise, an exception is thrown.
        allow_git_dirty_rows: if set to true, allows that rows have a dirty git
            status. Otherwise, an exception is thrown.

    returns: a pandas DataFrame with all columns of the database as columns.
    """
    # rows might be a query, which is not yet fetched from the database.
    if type(rows) not in [list, np.array]:
        rows = list(rows)

    if rows is None or len(rows) == 0:
        return pd.DataFrame()

    git_ids = set([row.git_commit_id for row in rows])
    if not allow_git_different_rows and len(git_ids) > 1:
        raise ValueError(f'your result contains multiple git ids: {git_ids}')

    # the DbModel objects will have additional columns that are not interesting
    # for the underlying application. In the __table__.columns field, the
    # actual list of "payload"-columns is stored.
    columns = [column.name for column in rows[0].__table__.columns]
    df_rows = []
    for row in rows:

        if not allow_git_dirty_rows and row.git_is_dirty:
            raise ValueError('your result contains dirty git rows')

        row_result = {}
        for column in columns:
            row_result[column] = getattr(row, column)
        df_rows.append(row_result)

    return pd.DataFrame(df_rows)


def _read_parameters(dictionary, prefix='', use_prefix=True):
    """Recursive helper method for extracting GridSearch param information."""
    if len(dictionary) == 0:
        return dictionary
    result = {}
    for k, v in dictionary.items():
        # PipelineHelper is the root of the model
        if k == 'selected_model':
            k = prefix + k if use_prefix else k
            result[k] = str(v[0])
            result.update(_read_parameters(v[1], str(v[0]) + '__'))
        # PipelineHelper is somewhere else
        elif '__selected_model' in k:
            # the [:-16] cuts off the string '__selected_model'
            key_name = prefix + k[:-16] if use_prefix else k[:-16]
            result[key_name] = str(v[0])
            result.update(_read_parameters(v[1], str(v[0]) + '__'))
        # "Regular" GridSearch element
        else:
            key_name = prefix + k if use_prefix else k
            result[key_name] = f'{v}'
    return result


def extract_gridsearch_parameters(
    df,
    score_name,
    drop_outcome=True,
    prefix_parameter_names=True,
):
    """
    Extracts parameters from a grid search result.

    This method creates one DataFrame row for each parameter combination in the
    "outcome -> cv_results" field, and one column of each distinct parameter.
    For example, if your grid search contains a parameter `svm__C: [1, 10]`,
    then this method will add a column `C` to your DataFrame, and replace this
    row with two rows for the values 1 and 10.

    This method will recursively resolve parameters used in PipelineHelpers.

    Depending on your configurations, the output of this method may make the
    row ids no longer unique.

    before:
    row0 = {
        dataloader: XY,
        outcome: {
            cv_results: {
                params: {
                    1: { SVM__C:  1},
                    2: { SVM__C: 10},
                }
            }
        }
    }

    after:
    row0 = {
        dataloader: XY,
        SVM__C: 1,
    }
    row1 = {
        dataloader: XY,
        SVM__C: 10,
    }

    args:
        df: a pandas DataFrame object that has one column 'outcome', which
            contains dictionaries which have a field 'cv_results'. Notably,
            this is the case for the result of the rows_to_dataframe method.
        score_name: name of the field that the score should be extracted from.
            This can be a single string (e.g., 'mean_test_score') or a list of
            strings.
        drop_outcome: if true, the resulting dataframe will no longer have the
            original 'outcome' column.
        prefix_parameter_names: This parameter only affects models which have
            a PipelineHelper. If true, the resulting parameter names are
            returned by their full name. If set to false, only the part within
            the PipelineHelper is returned.
            Note that omitting this prefix may result in multiple parameters
            with the same name, possibly leading to grouping unrelated fields.

    returns: a pandas DataFrame with all possible parameters as columns, and
        all distinct parameter combinations as rows.
    """
    result_rows = []
    for _, row in df.iterrows():
        if 'outcome' not in row or 'cv_results' not in row['outcome']:
            raise ValueError(
                'this result set does not seem to contain grid '
                "search results, missing field: row['outcome']['cv_results']")
        cv = row['outcome']['cv_results']
        for combination_id, combination in cv['params'].items():
            # prevent unnecessary copy of the outcome field, which may be big
            result_row = {k: v for k, v in row.items() if k != 'outcome'}
            if not drop_outcome:
                result_row['outcome'] = row['outcome']

            if type(score_name) == str:
                score_name = [score_name]

            for score in score_name:
                result_row[score] = cv[score][combination_id]
            result_row.update(
                _read_parameters(combination,
                                 use_prefix=prefix_parameter_names))
            result_rows.append(result_row)
    return pd.DataFrame(result_rows)


def load_dataframe(allow_multiple_git_ids=False,
                   allow_dirty_rows=False,
                   **query_filters):
    """
    A flexible wrapper for queries.

    Args:
        allow_multiple_git_ids (bool): If false, raises an error when loading
            results with different git commit ids
        allow_dirty_rows (bool): If false, raises an error when loading rows
            resulting from a dirty git state
        **query_filters: key-value restrictions on the DB query. The values
            can have three different representations:
            - single vaules, then they will be matched with ==
            - comma separated values, then they will be matched with 'in (...)'
            - values separated with ' to ', then they will be matched with >=
                and <= if one of the two borders is an asterisk, only the other
                border will be used. Couldn't use the dash, as it is needed in
                date-based queries.

    Returns:
        A dataframe resulting from the query, and an object containing
        additional information of the git and row ids used in this result, and
        a list of all scores that were found in the result.

    Examples:
        - load a single git commit:
            df, info = load_dataframe(git_commit_id='2aace91d317694a08...')
        - load all results between two row ids
            df, info = load_dataframe(id="1200 to 1300")
        - specifiy multiple query filters
            df, info = load_dataframe(
                git_commit_id="...",
                sourcefile="plan1.py,plan2.py",
            )
    """
    session = DB.session()
    query = session.query(DbModel)
    for field, value in query_filters.items():
        if not value:
            continue

        if ' to ' in value:
            min_val, max_val = value.split(' to ')
            if min_val != '*':
                query = query.filter(getattr(DbModel, field) >= min_val)
            if max_val != '*':
                query = query.filter(getattr(DbModel, field) <= max_val)
        elif ',' in value:
            query = query.filter(getattr(DbModel, field).in_(value.split(',')))
        else:
            query = query.filter(getattr(DbModel, field) == value)

    df = rows_to_dataframe(query, allow_multiple_git_ids, allow_dirty_rows)
    LOGGER.debug('loaded %s raw rows from db', df.shape[0])
    extra_info = {}
    scores = None
    has_cv_results = False
    for _, row in df.iterrows():

        if 'cv_results' in row:
            has_cv_results = True

        row_scores = set([
            k for k in row['outcome']['cv_results'].keys()
            if k.startswith('mean_test_')
        ])
        if scores is None:
            scores = row_scores
        else:
            if scores - row_scores or row_scores - scores:
                raise ValueError(
                    'you have loaded rows that have different scoring fields, '
                    f'which is not supported: {scores} vs. {row_scores}')

    LOGGER.debug('extracted scores: %s', scores)
    extra_info['scores'] = scores
    extra_info['git_ids'] = set(df['git_commit_id'].values)
    extra_info['row_ids'] = set(df['id'].values)
    if has_cv_results:
        df = extract_gridsearch_parameters(df, scores)
    return df, extra_info
