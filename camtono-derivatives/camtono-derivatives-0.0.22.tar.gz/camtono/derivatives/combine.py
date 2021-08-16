def generate_derivative(definition: dict, feature_map: dict, desired_dialect, single_query: bool = False,
                        new_table_prefix: str = None):
    """Create a derived query ast based on a definition and map of all used features

    :param definition: camtono derivative definition
    :param feature_map: dictionary of feature_id: feature details that are referenced in the defintion
    :param single_query: generate a single query_ast or an ordered list of arrays that
    :param new_table_prefix: string used when referencing new tables in multiple
    :return:
    """
    from camtono.derivatives.filters import flatten_filters, generate_filters_query_sets
    from camtono.derivatives.generate import generate_multi_query_skeleton
    from camtono.derivatives.selects import generate_select_mapping
    from camtono.derivatives.outputs import generate_output_queries
    filters, default_inputs, feature_inputs = standardize_input_attributes(definition=definition)
    flattened_filters = flatten_filters(filters=filters)
    input_query_sets, input_features, dependent_queries = generate_filters_query_sets(
        flattened_filters=flattened_filters, features=feature_map,
        default_inputs=default_inputs, feature_inputs=feature_inputs, table_prefix=new_table_prefix,
        feature_map=feature_map, dialect_name=desired_dialect
    )
    definition_outputs = definition.get('outputs', definition.get('output'))
    if not definition_outputs:
        definition_outputs = [dict(column_name=definition['grain'])]
    output_queries, output_dependencies = generate_output_queries(definition_outputs=definition_outputs,
                                                                  default_inputs=default_inputs,
                                                                  feature_map=feature_map,
                                                                  input_features=input_features,
                                                                  feature_inputs=feature_inputs,
                                                                  definition_features = [i['feature_id'] for i in definition['features']],
                                                                  table_prefix=new_table_prefix, dialect_name=desired_dialect)
    dependent_queries = combine_query_lists(existing_query_lists=dependent_queries, new_query_lists=output_dependencies,
                                            start_index=0)
    selects, group_by = generate_select_mapping(
        input_features=input_features,
        default_inputs=default_inputs,
        definition_outputs=definition_outputs,
        input_query_sets=input_query_sets,
        feature_map=feature_map,
        grain=definition['grain'],
        output_queries=output_queries, definition_groupings=definition.get('group_by', [])
    )
    queries = generate_multi_query_skeleton(
        input_query_sets=input_query_sets, grain=definition['grain'],
        output_queries=output_queries, selects=selects,
        table_prefix=new_table_prefix, group_by=group_by, dialect_name=desired_dialect
    )
    return [list(i.values()) for i in combine_query_lists(existing_query_lists=dependent_queries, new_query_lists=queries,
                               start_index=len(dependent_queries))]


def standardize_input_attributes(definition):
    inputs = definition['filters'] if 'filters' in definition.keys() else definition.get('inputs', dict())
    default_inputs = dict()
    if 'default_filters' in definition.keys():
        default_inputs = {i['attribute']: i['value'] for i in definition.get('default_filters', [])}
    elif 'default_inputs' in definition.keys():
        default_inputs = {i['attribute']: i['value'] for i in definition.get('default_inputs', [])}
    if 'grain' not in default_inputs.keys():
        default_inputs['grain'] = definition['grain']
    feature_inputs = {i['feature_id']: i.get('inputs', i.get('input', {})) for i in definition['features']}
    return inputs, default_inputs, feature_inputs


def combine_query_lists(existing_query_lists, new_query_lists, start_index):
    for sub_query_idx, queries in enumerate(new_query_lists):
        if len(existing_query_lists[start_index:]) < sub_query_idx + 1:
            existing_query_lists.append(dict())
        existing_query_lists[sub_query_idx + start_index].update(queries)
    return existing_query_lists
