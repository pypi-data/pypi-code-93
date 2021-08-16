def generate_select_mapping(default_inputs, definition_outputs, input_query_sets, input_features, grain,
                            feature_map, output_queries, definition_groupings) -> tuple:
    filter_select, filter_group_by = generate_filter_selects(definition_outputs=definition_outputs, grain=grain,
                                                             feature_map=feature_map, input_query_sets=input_query_sets,
                                                             subquery_groupings=[i for i in definition_groupings if
                                                                                 i.get('aggregate_sub_queries')])
    feature_outputs = generate_feature_select(feature_map=feature_map, default_inputs=default_inputs)
    final_select, final_group_by = generate_final_select(filter_select=filter_select['filter'],
                                                         grain=grain,
                                                         feature_outputs=feature_outputs,
                                                         definition_outputs=definition_outputs,
                                                         input_features=input_features,
                                                         output_queries=output_queries,
                                                         definition_groupings=definition_groupings)
    select_mapping = dict(
        final=final_select,
        **filter_select,
        **feature_outputs
    )

    group_by = dict(
        final=final_group_by,
        **filter_group_by
    )
    return select_mapping, group_by


def extract_select_schema(select, dialect_name):
    from camtono.parser.dialects import load_dialect_module
    dialect = load_dialect_module(dialect_name=dialect_name)
    return [dialect.format_schema(column_name=i['name'], data_type=i['type'] if 'type' in i.keys() else i['data_type'])
            for i in select]


def extract_select_output(select):
    return [dict(value=i['value'], name=i['name']) for i in select]


def generate_base_filter_select_mapping(grain, feature_map, definition_outputs, subquery_groupings):
    common_output = identify_common_output(features=list(feature_map.values()), grain=grain)
    shared_output = [i for i in definition_outputs if 'feature_id' not in i.keys()]
    if grain not in [i['column_name'] for i in shared_output]:
        shared_output = [dict(column_name=grain), *shared_output]
    filter_groupings = dict(
        filter=generate_group_by(
            groupings=subquery_groupings,
            base_values={
                i['column_name']: 't0.{column_name}'.format(column_name=i['column_name'])
                for i in shared_output
            }
        )
    )
    filter_select = dict(
        filter=[
            dict(
                name=i['column_name'], value='t0.{column_name}'.format(column_name=i['column_name']),
                type=common_output[i['column_name']]['data_type'],
            )
            for i in shared_output
        ]
    )
    return filter_select, filter_groupings, common_output, shared_output


def generate_filter_selects(definition_outputs, grain, feature_map, input_query_sets, subquery_groupings):
    from camtono.derivatives.transforms import apply_transforms
    filter_select, filter_groupings, common_output, shared_output = generate_base_filter_select_mapping(
        grain=grain,
        feature_map=feature_map,
        definition_outputs=definition_outputs, subquery_groupings=subquery_groupings
    )
    for idx, input_query_set in enumerate(input_query_sets):
        input_select = []
        base_values = dict()
        for output in shared_output:
            if 'value' in output.keys():
                continue
            elif output['column_name'] not in common_output.keys():
                raise ValueError("{} is not shared by all features".format(output['column_name']))
            else:
                name = output['column_name']
                value = 't0.{}'.format(output['column_name'])
                data_type = common_output[output['column_name']]['data_type']
                base_values[name] = value
                if output.get('transform_sub_queries'):
                    value = [
                        't{idx}.{column_name}'.format(idx=i, column_name=output['column_name']) for i in
                        range(len(input_query_set))
                    ]
                    base_values[name] = value
                    value, data_type = apply_transforms(
                        value=value, data_type=data_type,
                        transforms=output['transforms']
                    )
                input_select.append(
                    dict(
                        name=name,
                        value=value,
                        type=data_type,
                    )
                )

        filter_select['f{idx}'.format(idx=idx)] = input_select
        filter_groupings['f{idx}'.format(idx=idx)] = generate_group_by(groupings=subquery_groupings,
                                                                       base_values=base_values)
    return filter_select, filter_groupings


def identify_common_output(features, grain):
    common_output = None
    feature = dict(outputs=[])
    for feature in features:
        if feature.get('is_mapping_feature'):
            continue
        if common_output is None:
            common_output = set([i['display_name'] for i in feature['outputs']])
        common_output.intersection_update(set([i['display_name'] for i in feature['outputs']]))
    common_output_dict = dict()

    for output in feature['outputs']:
        if output['display_name'] in common_output:
            common_output_dict[output['display_name']] = output
        if output['display_name'] == '{grain}':
            common_output_dict[grain] = output
            common_output_dict[grain]['name'] = common_output_dict[grain]['name'].format(grain=grain)
            common_output_dict[grain]['display_name'].format(grain=grain)
    return common_output_dict


def generate_final_select(filter_select, definition_outputs, grain, feature_outputs, input_features, output_queries,
                          definition_groupings):
    from camtono.derivatives.transforms import apply_transforms
    final_select = []
    filter_select_dict = {i['name']: i for i in filter_select}
    base_values = dict()
    for output in definition_outputs:
        base_value, data_type = generate_final_column_value(
            grain=grain,
            output=output, filter_select_dict=filter_select_dict,
            feature_outputs=feature_outputs, input_features=input_features,
            output_queries=output_queries
        )
        name = output['rename_as'] if 'rename_as' in output.keys() else output['column_name']
        original_name = output.get('column_name')
        if original_name is not None:
            base_values[original_name] = base_value
        column_value, data_type = apply_transforms(
            value=base_value, data_type=data_type,
            transforms=output.get('transforms', [])
        )
        final_select.append(
            dict(
                name=name,
                value=column_value,
                type=data_type
            ),
        )
    group_by = generate_group_by(groupings=definition_groupings, base_values=base_values)
    return final_select, group_by


def generate_group_by(groupings, base_values):
    from camtono.derivatives.transforms import apply_transforms
    group_by = list()
    for field in groupings:
        if field.get('output_column_name'):
            value = field['output_column_name']
        else:
            value = base_values[field['column_name']]
        group_by.append(apply_transforms(value=value, data_type='', transforms=field.get('transforms', []))[0])
    return group_by


def generate_final_column_value(grain, output, filter_select_dict, feature_outputs, input_features, output_queries):
    if output['column_name'] in filter_select_dict and output['column_name'] != grain:
        column_value = ['base.{}'.format(output['column_name']),
                        *['sub_feature_{idx}.{column_name}'.format(idx=idx, column_name=output['column_name']) for
                          idx in range(len(output_queries))]]
        data_type = filter_select_dict[output['column_name']]['type']
    elif output['column_name'] in filter_select_dict:
        column_value = 'base.{}'.format(output['column_name'])
        data_type = filter_select_dict[output['column_name']]['type']
    elif 'feature_id' in output.keys():
        output_types = {i['name']: i['type'] for i in feature_outputs[output['feature_id']]}
        table_name = "sub_feature_{idx}".format(idx=list(feature_outputs.keys()).index(output['feature_id']))
        if not input_features and table_name == 'sub_feature_0':
            table_name = 'base'
        column_value = '{table_name}.{column}'.format(
            column=output['column_name'],
            table_name=table_name)
        data_type = output_types[output['column_name']]
    elif 'value' in output.keys():
        column_value = 'sub_feature_{idx}.{column}'.format(
            column=output['column_name'],
            idx=list(feature_outputs.keys()).index(output['feature_id']))
        data_type = type(output['value'])
    else:
        raise ValueError('Output must reference a feature or have a defined value')
    return column_value, data_type


def generate_feature_select(feature_map, default_inputs) -> dict:
    feature_selects = dict()
    for feature_id, feature in feature_map.items():
        feature_selects[feature_id] = [
            dict(
                name=output['display_name'].format(**default_inputs),
                value=output['name'].format(**default_inputs),
                type=output['data_type']
            )
            for output in feature['outputs']
        ]
    return feature_selects
