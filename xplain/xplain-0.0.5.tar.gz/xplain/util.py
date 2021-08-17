import json
import pandas as pd
import uuid


def __buildTree__(new_tree, jsonObject, parent_id):
    objectRoot = jsonObject['objectName']
    rootid = uuid.uuid4()
    if parent_id == None:
        new_tree.create_node('(( ' + objectRoot + ' ))', rootid)
    else:
        new_tree.create_node('(( ' + objectRoot + ' ))', rootid, parent=parent_id)

    for dimension in jsonObject['dimensions']:
        dimension_id = uuid.uuid4()
        new_tree.create_node(dimension['dimensionName'], dimension_id, parent=rootid)
        if dimension.get('attributes') != None:
            for attribute in dimension['attributes']:
                attribute_id = uuid.uuid4()
                new_tree.create_node(attribute['attributeName'], attribute_id, parent=dimension_id)
    if jsonObject.get('childObjects') != None:
        for childObject in jsonObject['childObjects']:
            __buildTree__(new_tree, childObject, rootid)

    return new_tree


def build_groupby(object_name=None, dimension_name=None, attribute_name = None, groupby_level=None, groupby_level_number=None):
    groupby = {
        "attribute": {
            "object": object_name,
            "dimension": dimension_name,
            "attribute": attribute_name
        }
    }
    if groupby_level is not None:
        groupby["groupByLevel"] = groupby_level

    if groupby_level_number is not None:
        groupby["groupByLevelNumber"] = groupby_level_number
    return groupby


def build_selection(attribute_name, object_name=None, dimension_name=None, selected_states=None):
    selection = {
        "attribute": {
            "object": object_name,
            "dimension": dimension_name,
            "attribute": attribute_name
        },
        "selectedStates": selected_states
    }
    return selection


def get_result(query_name, data_frame=True):
    """
    et the result of a certain request id

    :param query_name:  the query name or id
    :param data_frame: if result shall be returned as pandas data frame
    :return: the result of specified query
    :rtype: json
    """
    global __xplain_session__
    if __xplain_session__.get('requests') != None:
        for xrequest in __xplain_session__["requests"]:
            if xrequest["requestName"] == query_name:
                if data_frame:
                    return convert_to_dataframe(xrequest["results"][0])
                else:
                    return xrequest["results"][0]


def convert_to_dataframe(data):
    """
    convert result JSON to DataFrame format

    :param data: data in JSON format
    :return: data in pandas data frame format
    """

    if data.get("fields") is not  None:
        data_fields = data['fields']
    else:
        data_fields = []


    if data.get("children") is not None:
        children = data["children"]
    else:
        children = []

    dataSet = {}
    for field in data_fields:
        dataSet[field] = []

    for child in children:
        for field in data_fields:
            for rec in child['data']:
                if isinstance(rec[field], str):
                    dataSet[field].append(rec[field])
                else:
                    if rec[field].get('value') != None:
                        dataSet[field].append(rec[field]['value'])
                    else:
                        dataSet[field].append(None)

    df = pd.DataFrame(dataSet)
    return df
