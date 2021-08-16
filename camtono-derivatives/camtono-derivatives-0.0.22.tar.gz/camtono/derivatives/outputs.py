def generate_output_queries(definition_outputs, definition_features, default_inputs, feature_map, input_features, feature_inputs,
                            table_prefix, dialect_name):
    from camtono.derivatives.features import inject_feature_variables
    from camtono.derivatives.combine import combine_query_lists
    output_queries = []
    column_features = set([i['feature_id'] for i in definition_outputs if 'feature_id' in i.keys()])
    output_features = {k: feature_map[k] for k in definition_features if k not in input_features.keys() or k in column_features}
    sub_queries = list()
    for feature_id, feature in output_features.items():
        ast, dependent_queries = inject_feature_variables(
            feature=feature, filter_set_inputs=dict(), feature_map=feature_map, table_prefix=table_prefix,
            default_inputs=default_inputs, feature_input=feature_inputs.get(feature_id, dict()), dialect_name=dialect_name
        )
        # feature_id to ast map
        output_queries.append({"feature_id": feature_id, "ast": ast})
        sub_queries = combine_query_lists(existing_query_lists=sub_queries, new_query_lists=dependent_queries,
                                          start_index=0)
    return output_queries, sub_queries
