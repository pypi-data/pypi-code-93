def inject_feature_variables(feature, filter_set_inputs, default_inputs, feature_input, feature_map, table_prefix,
                             dialect_name):
    feature_ast = trim_feature_input(
        feature, default_inputs=default_inputs, filter_set_inputs=filter_set_inputs, feature_input=feature_input)
    feature_ast, dependent_queries = inject_dependencies(
        feature, ast=feature_ast, default_inputs=default_inputs,
        filter_set_inputs=filter_set_inputs, feature_map=feature_map, feature_input=feature_input,
        table_prefix=table_prefix, dialect_name=dialect_name)
    return feature_ast, dependent_queries


def inject_dependencies(feature, ast, default_inputs, feature_input, feature_map, filter_set_inputs, table_prefix,
                        dialect_name):
    from camtono.derivatives.combine import combine_query_lists
    from camtono.derivatives.generate import generate_table_query
    dependent_queries = list()
    for dependency in feature.get('dependencies', []):
        dependent_feature = feature_map[dependency['feature_id']]
        dependent_ast, sub_queries = inject_feature_variables(
            feature=dependent_feature,
            filter_set_inputs=filter_set_inputs,
            default_inputs=default_inputs, table_prefix=table_prefix,
            feature_map=feature_map, feature_input=feature_input, dialect_name=dialect_name
        )
        select = [dict(name=i['name'].format(**default_inputs, **feature_input), type=i['data_type']) for i in feature['outputs']]
        table_name, table_query = generate_table_query(select=select, ast=dependent_ast,
                                                       table_prefix=table_prefix, dialect_name=dialect_name)
        sub_queries.append({table_name: table_query})
        dependent_queries = combine_query_lists(existing_query_lists=dependent_queries, new_query_lists=sub_queries,
                                                start_index=0)
        value = dict(value=table_name)
        for i in dependency['locations']:
            ast = set_tree_value(
                json=ast, locations=i['location'],
                val=value, target_index=i['level']
            )
    return ast, dependent_queries


def trim_feature_input(feature: dict, filter_set_inputs: dict, default_inputs: dict, feature_input: dict):
    """Remove all unnecessary query input from the query_ast

    :param feature: feature dict
    :param filter_inputs: dict of variables used for string formatting
    :param default_inputs:
    :param feature_input:
    :return: feature dict with cleaned query_ast
    """
    from copy import deepcopy

    ast = deepcopy(feature['query_ast'])
    for query_input in feature['inputs']:
        dependent_input_name = '{feature_id}.{input_name}'.format(
            feature_id=feature['feature_id'],
            input_name=query_input['name'])
        if all(query_input['name'] not in i.keys() for i in
               [filter_set_inputs, default_inputs,
                feature_input.get(feature['feature_id'], dict())]) and not query_input.get(
            'default_value') and dependent_input_name not in filter_set_inputs:
            v = None
        elif dependent_input_name in filter_set_inputs:
            v = filter_set_inputs[dependent_input_name]['value']
        elif query_input['name'] in filter_set_inputs:
            v = filter_set_inputs[query_input['name']]['value']
        elif query_input['name'] in feature_input.get(feature['feature_id'], dict()):
            v = feature_input[feature['feature_id']][query_input['name']]
        elif query_input.get('default_value'):
            v = query_input['default_value']
        else:
            v = default_inputs[query_input['name']]
        ast = update_feature_input(ast=ast, v=v, query_input=query_input)
    return ast


def update_feature_input(ast, v, query_input):
    new_val = v
    if query_input['is_literal']:
        if isinstance(v, str):
            new_val = {'literal': v}
        elif isinstance(v, list):
            new_val = [{'literal': i} for i in v]
    for i in query_input['locations']:
        if not query_input['is_literal'] and v is not None:
            val = get_tree_value(json=ast, locations=i['location']).replace("'{", '{').replace("}'", "}")
            new_val = val.replace('{' + query_input['name'] + '}', v)
        ast = set_tree_value(
            json=ast, locations=i['location'],
            val=new_val, target_index=i['level'] - 1 if i['is_wrapped_literal'] else i['level']
        )
    return ast


def set_value(val, **kwargs):
    """ Convenience function to set value for set_tree_value

    :param val: value to return
    :param kwargs: all other values
    :return: the value provided
    """
    return val


def get_tree_value(json, locations):
    if locations and (isinstance(json, dict) or isinstance(json, list)):
        for k, v in locations.items():
            if k.isdigit():
                k = int(k)
            v = get_tree_value(json=json[k], locations=v)
            return v
    else:
        return json


def set_tree_value(json, locations, target_index, current_index=0, replace_func=set_value, val=None):
    """ Set the

    :param json: dictionary
    :param locations: dictionary of the paths containing the location of a target value
    :param replace_func: function to apply when setting value receives val and json
    :param val: value to set
    :param target_index: location from the start of the tree where the replacement function should be applied
    :param current_index: current location in the tree
    :return: dictionary with the newly assigned values.
    """
    if locations and current_index < target_index and (isinstance(json, dict) or isinstance(json, list)):
        for k, v in locations.items():
            if k.isdigit():
                k = int(k)
            v = set_tree_value(json=json[k], locations=v, val=val, replace_func=replace_func,
                               target_index=target_index, current_index=current_index + 1)
            json[k] = v
        return json
    elif current_index == target_index:
        return val
    else:
        raise Exception("Invalid Location / Index")
