def generate_filters_query_sets(flattened_filters, features, default_inputs: dict, feature_inputs: dict,
                                table_prefix: str, feature_map, dialect_name):
    """

    :param flattened_filters:
    :param features:
    :return:
    """
    from camtono.derivatives.features import inject_feature_variables
    from camtono.derivatives.combine import combine_query_lists
    query_sets, filter_features = [], dict()
    sub_queries = list()
    for idx, input_set in enumerate(flattened_filters):
        set_features, skip = define_set_features(input_set=input_set)
        filter_features.update(set_features)
        query_set = []
        for feature, filters in set_features.items():
            ast, dependent_queries = inject_feature_variables(
                feature=features[feature], filter_set_inputs=set_features[feature],
                default_inputs=default_inputs, feature_input=feature_inputs, table_prefix=table_prefix,
                feature_map=feature_map, dialect_name=dialect_name
            )
            sub_queries = combine_query_lists(existing_query_lists=sub_queries, new_query_lists=dependent_queries,
                                              start_index=0)
            # feature_id to ast map
            query_set.append({"feature_id": feature, "ast": ast,
                              "is_mapping_feature": features[feature].get("is_mapping_feature"),
                              "grain": features[feature].get("grain")})
        if not skip:
            query_sets.append(query_set)
    return query_sets, filter_features, sub_queries


def flatten_filters(filters: dict) -> tuple:
    """

    :param inputs:
    :return:
    """
    list_string = 'filters'
    if 'inputs' in filters.keys():
        list_string = 'inputs'
    flattened_filters = flatten_filter(filters=filters, list_string=list_string)
    return flattened_filters


def flatten_filter(filters, list_string='filters', operator_string='item'):
    """Flattens nested pyparser syntax into a single layer

    :param inputs:
    :param list_string:
    :param operator_string: string key of the pyparser operator
    :return: flatted list of lists of base operators
    """
    flattened_filters = list()
    if operator_string in filters.keys() and list_string in filters.keys():
        operator = filters[operator_string].lower()
        for idx, i in enumerate(filters[list_string]):
            new_filters = i
            if isinstance(i.get(list_string), list):
                new_filters = flatten_filter(filters=i, list_string=list_string, operator_string=operator_string)
            if len(new_filters) > 0:
                flattened_filters = unify_sets(existing=flattened_filters, new=new_filters, operator=operator)
    return flattened_filters


def unify_sets(existing, new, operator):
    """Join two sets of statements based on boolean operator

    :param existing: List of existing statements
    :param new: New statements to add to the set
    :param operator: boolean operator and, or, not
    :return: combined set of sets based on boolean operation
    """
    import itertools
    unified = []
    if isinstance(new, dict):
        new = [new]
    if not isinstance(new[0], list):
        new = [new]
    if not existing and operator in ['and', 'or']:
        unified = new
    elif operator == 'or':
        unified = existing + new
    elif operator == 'and':
        if existing:
            for a, b in itertools.product(existing, new):
                unified.append([*a, *b])
        else:
            unified.append(new)
    elif operator == 'not':
        for s in new:
            subset = []
            for x in s:
                x['not'] = bool(-x.get('not', False))
                subset = unify_sets(existing=subset, new=x, operator='or')
            unified = unify_sets(existing=unified, new=subset, operator='and')
    return unified


def define_set_features(input_set):
    """Processes flattened filter groups into a set of features

    :param filter_set: flattened list of filters
    :return: tuple of a dict of features and attributes and a flag to skip this particular filter group
    """
    features = dict()
    skip = False
    for f in input_set:
        if skip:
            continue
        if f['feature_id'] not in features.keys():
            features[f['feature_id']] = dict()
        if f['attribute'] not in features[f['feature_id']].keys():
            features[f['feature_id']][f['attribute']] = {'not': f.get('not', False), 'value': f['value']}
    return features, skip
