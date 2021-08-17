import xplain
import uuid

class Query_config:
    """
    factory class to generate the xplain query configuration for
    execute_query method of Xsession
    """
    def __init__(self, name=None):
        if name is None:
            name = str(uuid.uuid4())
        self.request = {
            "requestName": name,
            "aggregations": [],
            "groupBys": [
                {
                    "subGroupings": []
                }
            ],
            "selections": []

        }

    def set_name(self, request_name):
        """
        assign a specific name or id to te query

        :param request_name: the name/id to be assigned
        """
        self.request["requestName"] = request_name

    def add_aggregation(self, object_name, dimension_name, type):
        """
        add an aggregation specification to the query

        :param object_name: the name of xobject
        :param dimension_name: the name of dimension
        :param type: the aggregation type values are SUM, AVG, COUNT, COUNTDISTINCT, MAX, MIN
        """
        self.request["aggregations"].append({
            "object":object_name,
            "dimension": dimension_name,
            "type": type
        })

    def add_groupby(self, attribute_name, object_name=None, dimension_name=None,  groupby_level=None, groupby_level_number=None, groupby_states=None):
        """
        add a group by  specification to the query configuration

        :param attribute_name: the attribute name
        :param object_name: the name of object
        :param dimension_name: the name of dimension
        :param groupby_level: the group by level name
        :param groupby_level_number: the group by leve number, if group by_level name is not specified,
        you can define the level by the number of this level
        :param groupby_states: if the group by stats are maintained, the group by will be only applied to the specified
        group by states
        """
        groupby = xplain.build_groupby(object_name=object_name, dimension_name=dimension_name, attribute_name= attribute_name, groupby_level= groupby_level, groupby_level_number = groupby_level_number)
        self.request.get("groupBys")[0].get("subGroupings").append(groupby)


    def add_selection(self, attribute_name, object_name=None, dimension_name=None, selected_states=None):
        """
        add a group by  specification to the query configuration

        :param attribute_name: the name of attribute
        :param object_name: the name of xobject
        :param dimension_name: the name of dimension
        :param selected_states: the set of selected states
        """

        selection = xplain.build_selection(attribute_name=attribute_name, object_name=object_name, dimension_name=dimension_name, selected_states=selected_states)
        self.request.get("selections").append(selection)

    def to_json(self):
        """
        return the configuration of this query as json

        :return: json
        """

        return self.request