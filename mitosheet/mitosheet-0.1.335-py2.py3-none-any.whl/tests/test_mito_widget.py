#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.
import os
import pandas as pd
import pytest

from mitosheet.mito_widget import MitoWidget, sheet
from mitosheet.utils import get_invalid_headers
from mitosheet.transpiler.transpile import transpile


def test_example_creation_blank():
    df = pd.DataFrame()
    w = MitoWidget(df, tutorial_mode=False)

VALID_DATAFRAMES = [
    (pd.DataFrame()),
    (pd.DataFrame(data={'A': [1, 2, 3]})),
    (pd.DataFrame(data={'A0123': [1, 2, 3]})),
]
@pytest.mark.parametrize("df", VALID_DATAFRAMES)
def test_sheet_creates_valid_dataframe(df):
    mito = sheet(df)
    assert mito is not None

NON_VALID_HEADER_DATAFRAMES = [
    (pd.DataFrame(data={0: [1, 2, 3]}), ['0_']),
    (pd.DataFrame(data={0.1: [1, 2, 3]}), ['0_1_']),
    (pd.DataFrame(data={'A': [1, 2, 3], 0: [1, 2, 3]}), ['A', '0_']),
    (pd.DataFrame(data={'A': [1, 2, 3], '000': [1, 2, 3]}), ['A', '000_']),
    (pd.DataFrame(data={'A': [1, 2, 3], 'abc-123': [1, 2, 3]}), ['A', 'abc_123']),
    (pd.DataFrame(data={'A': [1, 2, 3], '-123': [1, 2, 3]}), ['A', '_123']),
    (pd.DataFrame(data={'A': [1, 2, 3], '-123_': [1, 2, 3]}), ['A', '_123_']),
    (pd.DataFrame(data={'A': [1, 2, 3], '-abc_': [1, 2, 3]}), ['A', '_abc_']),
    (pd.DataFrame(data={'123': [1, 2, 3], '-abc_': [1, 2, 3]}), ['123_', '_abc_']),
    (pd.DataFrame(data={'ABC!DEF': [1, 2, 3], '123': [1, 2, 3]}), ['ABC_DEF', '123_']),
    (pd.DataFrame(data={'ABC?DEF': [1, 2, 3], '123': [1, 2, 3]}), ['ABC_DEF', '123_']),
    (pd.DataFrame(data={' ': [1, 2, 3], '123': [1, 2, 3]}), ['_', '123_']),
    (pd.DataFrame(data={'-': [1, 2, 3], ' !': [1, 2, 3]}), ['_', '__']),
    (pd.DataFrame(data={'##': [1, 2, 3], ' !': [1, 2, 3]}), ['numnum', '__']),
    (pd.DataFrame(data={'#!?5': [1, 2, 3], '#123': [1, 2, 3]}), ['num__5', 'num123']),
    (pd.DataFrame(data={'()': [1, 2, 3], '.,,': [1, 2, 3]}), ['__', '___']),
    (pd.DataFrame(data={'nate': [1, 2, 3], '.,,': [1, 2, 3]}), ['nate', '___']),
    (pd.DataFrame(data={'//': [1, 2, 3], '-': [1, 2, 3]}), ['__', '_']),
]

@pytest.mark.parametrize("df, new_keys", NON_VALID_HEADER_DATAFRAMES)
def test_sheet_errors_during_non_string_headers(df, new_keys):
    assert len(get_invalid_headers(df)) != 0
    mito = sheet(df)
    assert list(mito.steps_manager.curr_step.dfs[0].keys()) == new_keys

def test_create_with_multiple_dataframes():
    mito = sheet(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(data={'A': [1, 2, 3]}))
    assert mito is not None

def test_errors_on_non_existing_analysis():
    with pytest.raises(ValueError):
        mito = sheet(saved_analysis_name='bork a dork')


def test_can_call_sheet_with_just_filename():
    df = pd.DataFrame(data={'A': [1, 2, 3], 'B': [2, 3, 4]})
    df.to_csv('../1.csv', index=False)

    mito = sheet('../1.csv')

    assert len(mito.steps_manager.dfs) == 1
    assert mito.steps_manager.dfs[0].equals(df)

    # Remove the test file
    os.remove('../1.csv')


def test_can_call_sheet_with_filename_mulitiple_times():
    df = pd.DataFrame(data={'A': [1, 2, 3], 'B': [2, 3, 4]})
    df.to_csv('../1.csv', index=False)

    mito = sheet('../1.csv', '../1.csv')

    assert len(mito.steps_manager.dfs) == 2
    assert mito.steps_manager.dfs[0].equals(df)
    assert mito.steps_manager.dfs[1].equals(df)
    assert mito.steps_manager.curr_step.df_names[0] != mito.steps_manager.curr_step.df_names[1]

    # Remove the test file
    os.remove('../1.csv')


def test_can_call_sheet_with_df_and_filename():
    df = pd.DataFrame(data={'A': [1, 2, 3], 'B': [2, 3, 4]})
    df.to_csv('../1.csv', index=False)

    mito = sheet(df, '../1.csv')

    assert len(mito.steps_manager.dfs) == 2
    assert mito.steps_manager.dfs[0].equals(mito.steps_manager.dfs[1])

    # Remove the test file
    os.remove('../1.csv')

    code_container = transpile(mito.steps_manager)

    assert code_container['code'] == [
        '# Read in filepaths as dataframes',
        'df_1_csv = pd.read_csv(r\'../1.csv\')',
    ]


def test_call_makes_copies():
    df = pd.DataFrame(data={'A A': [1, 2, 3]})
    sheet(df)

    # Test we don't change the headers!
    assert df.columns.tolist() == ['A A']

def test_can_call_with_indexes():
    df = pd.DataFrame(data={'A': [1, 2, 3], 'B': ['A', 'B', 'C'], 'D': ['E', 'F', 'G']})

    string_index = df.set_index('B')
    sheet(string_index)

    multi_index = df.set_index(['B', 'D'])
    sheet(multi_index)