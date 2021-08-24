import re
from typing import List, Tuple
from io import StringIO

import pandas as pd


def find_index_start_and_length_objective_table(output_lines: List[str], table_keyword: str) -> Tuple[int, int]:
    index_objective_table = None
    n_objectives = None
    for index_line, output_line in enumerate(output_lines):
        if 'OBJECTIVE' in output_line and 'S1' in output_line:
            index_objective_table = index_line

        if table_keyword in output_line:
            matches = re.findall(r"\d+", output_line)
            if matches:
                n_objectives = int(matches[0])

    return index_objective_table, n_objectives


def extract_objective_table(output_lines: List[str],
                            index_start_objective_table: int,
                            n_objectives: int
                            ) -> pd.DataFrame:
    objectives_table = output_lines[index_start_objective_table: index_start_objective_table + n_objectives + 1]
    objectives_table_lines = ["\t".join(objective_table.split()) for objective_table in objectives_table]

    TESTDATA = StringIO("\n".join(objectives_table_lines))
    objective_table_df = pd.read_csv(TESTDATA, sep="\t", index_col=0)
    objective_table_df.rename(columns={'WEIGHTED': 'WEIGHTED OBJ'}, inplace=True)
    objective_table_df.drop(columns='OBJ', inplace=True)
    return objective_table_df


def convert_bottom_header_table_to_str(block_df: pd.DataFrame, keyword: str, suffix='') -> str:
    keyword_and_length_str = "%s %d" % (keyword, len(block_df))
    if block_df.empty:
        return keyword_and_length_str
    else:
        block_str = block_df.to_string(index=False)
        block_str_lines = block_str.split('\n')
        block_str_lines = block_str_lines[1:] + [block_str_lines[0]]
        block_str = (suffix + '\n').join(block_str_lines)
        block_str = "%s\n%s" % (keyword_and_length_str, block_str)
        return block_str


def read_bottom_header_table(cadata_file_path: str, keyword='CABLE'):
    text_file = open(cadata_file_path, 'r')
    text_file_lines = text_file.read().split('\n')
    text_file.close()
    index_start, n_lines = find_index_start_and_length_bottom_header_table(text_file_lines, keyword)
    return extract_bottom_header_table(text_file_lines, index_start, n_lines)


def find_index_start_and_length_bottom_header_table(output_lines, table_keyword):
    len_keyword = len(table_keyword)
    for index_line, output_line in enumerate(output_lines):

        if (len(output_line) >= len_keyword) and (output_line[0:len_keyword] == table_keyword):
            index_objective_table = index_line
            matches = re.findall(r"\d+", output_line)
            if matches:
                n_objectives = int(matches[0])
                return index_objective_table, n_objectives

    raise IndexError('Not found start index and length for keyword %s' % table_keyword)


def extract_bottom_header_table(text_file_lines, index_start, n_lines):
    value_rows = text_file_lines[index_start + 1:index_start + n_lines + 1]
    header = text_file_lines[index_start + n_lines + 1]
    if 'Comment' in header:
        columns = ','.join(header.split()[:-1])
    else:
        columns = ','.join(header.split())

    # Replace comment
    values_comma_separated = []
    comments = []
    for value_row in value_rows:
        if '\'' in value_row:
            quotation_split = value_row.split('\'')
            values_without_comment = ','.join(quotation_split[0].split())
            values_comma_separated.append(values_without_comment)
            comments.append(quotation_split[1])
        else:
            values_comma_separated.append(','.join(value_row.split()))

    TESTDATA = StringIO("\n".join([columns] + values_comma_separated))
    objective_table_df = pd.read_csv(TESTDATA, sep=",")
    if comments:
        objective_table_df['Comment'] = comments
    return objective_table_df
