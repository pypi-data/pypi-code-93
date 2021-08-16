# -*- coding: utf-8 -*-
# @Time    : 2021-02-25 11:00
# @Author  : xzr
# @File    : sql
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    :
import copy

import sqlparse
from sqlparse.sql import Identifier, IdentifierList
from sqlparse.tokens import Name


def get_table_name(tokens):
    for token in tokens:
        if token.ttype is None:
            return token.value
    return " "


def get_parent_table_name(tokens):
    for i, token in enumerate(tokens):
        if token.value.lower() == 'like':
            parent_table_name = tokens[i + 1].value
            return parent_table_name
    return ''


def get_table_columns(tokens):
    columns = set()
    for token in tokens:

        if isinstance(token, (IdentifierList, Identifier)):
            columns |= get_table_columns(token.tokens)
        if token.ttype is Name:
            columns.add(token.value.strip('`'))
            break
    return set(columns)


def get_ddl_table_info(sql_texts):
    result = {}

    parse = sqlparse.parse(sql_texts)
    for stmt in parse:
        # Get all the tokens except whitespaces
        tokens = [t for t in sqlparse.sql.TokenList(stmt.tokens) if t.ttype != sqlparse.tokens.Whitespace]
        is_create_stmt = False
        parent_table_name = ''
        table_name = ''
        for i, token in enumerate(tokens):
            # Is it a create statements ?
            if token.match(sqlparse.tokens.DDL, 'CREATE'):
                is_create_stmt = True
                table_name = get_table_name(tokens[i:])
                result.setdefault(table_name, set())
                parent_table_name = get_parent_table_name(tokens)
                if parent_table_name:
                    result[table_name] = copy.copy(result.get(parent_table_name, set()))
                continue

            # If it was a create statement and the current token starts with "("
            if is_create_stmt and token.value.startswith("("):

                columns = get_table_columns(token.tokens)
                result[table_name] |= columns


    return result
