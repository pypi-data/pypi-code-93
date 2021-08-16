def generate_table_name(data, prefix=None):
    import json
    import uuid
    import hashlib
    if prefix is None:
        prefix = ""
    hash_id = hashlib.md5(
        str(json.dumps(data, sort_keys=True)).encode('utf-8')
    ).hexdigest()
    return prefix + str(hash_id)


def generate_table_query(select, ast, table_prefix, dialect_name):
    from camtono.derivatives.selects import extract_select_schema
    from camtono.parser.clean import prune_ast
    ast = prune_ast(json=ast)
    if table_prefix is None:
        table_prefix = 'camtono_'
    table_name = generate_table_name(data=ast, prefix=table_prefix)
    body = dict(query_ast=ast, table_name=table_name,
                schema=extract_select_schema(select=select, dialect_name=dialect_name))
    return table_name, body


def generate_multi_query_skeleton(input_query_sets, output_queries, grain, selects, group_by, table_prefix,
                                  dialect_name):
    from camtono.derivatives.selects import extract_select_output
    queries = generate_filters(input_query_sets=input_query_sets,
                               grain=grain, selects=selects,
                               group_by=group_by, table_prefix=table_prefix, dialect_name=dialect_name)

    output_queries = generate_output_column_queries(output_queries=output_queries, selects=selects,
                                                    table_prefix=table_prefix, dialect_name=dialect_name)
    if not queries:
        queries = [output_queries]
    base_table_name = list(queries[-1].keys())[0]
    queries[0].update(output_queries)

    final_query = {
        'select': extract_select_output(select=selects['final']),
        'from': [
            dict(value=base_table_name, name='base'),
            *[
                dict(
                    join=dict(
                        value=i['table_name'], name='sub_feature_{}'.format(idx)
                    ),
                    on={"eq": ["base.{}".format(grain), "sub_feature_{idx}.{grain}".format(idx=idx, grain=grain)]}
                ) for idx, i in enumerate(output_queries.values()) if i['table_name'] != base_table_name
            ]
        ],
        'groupby': group_by.get('final')
    }
    table_name, query_body = generate_table_query(select=selects['final'], table_prefix=table_prefix, ast=final_query,
                                                  dialect_name=dialect_name)
    queries.append({table_name: query_body})
    return queries


def generate_filters(input_query_sets, grain, selects: dict, group_by, table_prefix, dialect_name):
    from camtono.derivatives.selects import extract_select_output
    queries = [dict(), dict()]

    for idx, query_set in enumerate(input_query_sets):
        root_queries, translated_queries, combination_queries = generate_filter(
            input_idx=idx, input_query_set=query_set, grain=grain,
            table_prefix=table_prefix, selects=selects, group_by=group_by, dialect_name=dialect_name)
        queries[0].update(root_queries)
        if translated_queries:
            if len(queries) == 2:
                queries.append(dict())
                queries[2] = queries[1]
                queries[1] = dict()
            queries[1].update(translated_queries)

        queries[-1].update(combination_queries)
    if len(queries[-1]) > 1:
        base_query = dict(
            union_all=[
                {
                    "select": extract_select_output(select=selects['filter']),
                    'from': dict(value=i['table_name'], name='t0')
                }
                for i in queries[-1].values()
            ]
        )
        base_table_name, table_body = generate_table_query(
            select=selects['filter'], ast=base_query,
            table_prefix=table_prefix, dialect_name=dialect_name
        )
        queries.append({base_table_name: table_body})
    return [i for i in queries if i]


def generate_output_column_queries(output_queries, selects, table_prefix, dialect_name):
    queries = dict()
    for query in output_queries:
        table_name, query_body = generate_table_query(
            select=selects[query['feature_id']],
            ast=query['ast'],
            table_prefix=table_prefix,
            dialect_name=dialect_name
        )
        queries[table_name] = query_body
    return queries


def generate_translated_select(grain, query, query_idx, selects):
    """
    generate selects for translated table, should include all selects from original feature plus the final grain
    :param grain: final grain
    :param query: query item in input query set
    :param query_idx:
    :param selects: selects for input/root queries
    :return:
    """
    from copy import deepcopy
    translated_selects = deepcopy(selects[query['feature_id']])
    for select_element in translated_selects:
        select_element['value'] = "root_feature_{idx}.{column_name}".format(
            idx=query_idx, column_name=select_element['name'])
    grain_data_type = None
    for select_element in selects['final']:
        if select_element['name'] == grain:
            grain_data_type = select_element['type']
    translated_selects.append(dict(value='mapping_table.{}'.format(grain), name=grain,
                                   type=grain_data_type))
    return translated_selects


def multi_grain_validation_check(is_multi_grain, mapping_feature_table_name, root_queries):
    from stratus_api.core.exceptions import ApiError
    if is_multi_grain and len(root_queries) <= 1:
        raise ApiError('Multi grain definition must have at least 2 input features including one mapping feature')
    if is_multi_grain and not mapping_feature_table_name:
        raise ApiError('Multi grain definition must have one mapping feature as input')


def generate_filter(input_idx, input_query_set, grain, table_prefix, selects, group_by, dialect_name):
    from camtono.derivatives.selects import extract_select_output
    from copy import deepcopy
    translated_queries = None
    is_multi_grain = False
    mapping_feature_table_name = None
    root_index_to_table_name_map = dict()

    root_queries = dict()
    sub_ast = {'from': [], 'select': extract_select_output(select=selects['f{}'.format(input_idx)]),
               "groupby": group_by['f{}'.format(input_idx)]}
    for query_idx, query in enumerate(input_query_set):
        table_name, body = generate_table_query(ast=query['ast'], table_prefix=table_prefix,
                                                select=selects[query['feature_id']], dialect_name=dialect_name)
        root_queries[table_name] = body
        root_index_to_table_name_map[query_idx] = table_name
        if grain == query.get('grain') and not query.get('is_mapping_feature'):
            from_ = dict(
                value=table_name,
                name='t{}'.format(query_idx)
            )
            if sub_ast['from']:
                sub_ast['from'].append(dict(join=from_, on={
                    'eq': ['t0.{}'.format(grain), 't{table_number}.{grain}'.format(table_number=query_idx, grain=grain)]}))
            else:
                sub_ast['from'].append(from_)
        elif grain not in query['ast']['select']:
            is_multi_grain = True
        elif query.get('is_mapping_feature'):
            mapping_feature_table_name = table_name

    multi_grain_validation_check(is_multi_grain, mapping_feature_table_name, root_queries)
    if is_multi_grain:
        translated_queries = dict()
        for query_idx, query in enumerate(input_query_set):
            root_feature_grain = query.get('grain')
            if grain != root_feature_grain:
                root_table_name = root_index_to_table_name_map[query_idx]
                translated_selects = generate_translated_select(grain, query, query_idx, selects)

                ast = {
                    'select': translated_selects,
                    'from': [
                        dict(value=mapping_feature_table_name, name='mapping_table'),
                        dict(join=dict(value=root_table_name, name='root_feature_{}'.format(query_idx)),
                             on={'eq': ['mapping_table.{}'.format(root_feature_grain),
                                        'root_feature_{idx}.{grain}'.format(idx=query_idx, grain=root_feature_grain)]})
                    ]
                }
                translated_table_name, translated_body = generate_table_query(
                    select=translated_selects,
                    ast=ast,
                    table_prefix=table_prefix,
                    dialect_name=dialect_name)
                translated_queries[translated_table_name] = translated_body
                from_ = dict(value=translated_table_name, name='t{}'.format(query_idx))
                if sub_ast['from']:
                    sub_ast['from'].append(dict(join=from_, on={
                        'eq': ['t0.{}'.format(grain),
                               't{table_number}.{grain}'.format(table_number=query_idx, grain=grain)]}))
                else:
                    sub_ast['from'].append(from_)

    if len(root_queries) > 1:
        combination_table_name, combination_table_body = generate_table_query(
            select=selects['f{}'.format(input_idx)],
            ast=sub_ast,
            table_prefix=table_prefix,
            dialect_name=dialect_name
        )
        combination_tables = {combination_table_name: combination_table_body}
    else:
        combination_tables = root_queries
        root_queries = dict()

    return root_queries, translated_queries, combination_tables
