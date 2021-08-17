import xplain

class XObject():
    _ref_session = None
    object_name = None

    def __init__(self, object_name, ref_session ):
        self.object_name = object_name
        self._ref_session = ref_session

    def get_name(self):
        return self.object_name

    def get_child_objects(self):
        """
        get the children Xobjects of current Xobject

        :return: list of Xobject
        :rtype string[]
        """
        list_children = []
        json_details = self._ref_session.get_tree_details(object_name=self.object_name)
        if json_details.get("childObjects") is not None:
            for childObj in json_details["childObjects"]:
                list_children.append(XObject(object_name=childObj[
                    "objectName"], ref_session=self._ref_session))
        return list_children        

    

    def get_dimensions(self):
        """
        get the list of dimensions attached to the current Xobject

        :return: list of dimension names
        """
        list_dimensions = []
        json_details = self._ref_session.get_tree_details(
            object_name=self.object_name)
        if json_details.get("dimensions") is not None:
            for dimension_obj in json_details["dimensions"]:
                dim = xplain.Dimension(object_name=self.object_name,
                                       dimension_name=dimension_obj[
                                           "dimensionName"],
                                       ref_session=self._ref_session)
                list_dimensions.append(dim)
        return list_dimensions

    def get_dimension(self, dimension_name):
        dimension_found = None
        json_details = self._ref_session.get_tree_details(
            object_name=self.object_name)
        if json_details.get("dimensions") is not None:
            for dimension_obj in json_details["dimensions"]:
                if dimension_obj["dimensionName"] == dimension_name:
                    dimension_found = xplain.Dimension(object_name=self.object_name,
                                       dimension_name=dimension_obj[
                                           "dimensionName"],
                                       ref_session=self._ref_session)

        return dimension_found

    def add_aggregation_dimension(self, dimension_name,
                                  aggregation,
                                  selections=[], floating_semantics=False):
        """
        adds an aggregation dimension to the given target dimension. The
        aggregation dimension aggregates data from a child object (or any
        deeper descendant objects) according to the given aggregation
        definition.

        :param dimension_name: the name of new dimension
        :type dimension_name: string
        :param aggregation: aggregation of the new dimension
        :type aggregation: json or aggregation object
        :param selections: the selections shall be considered
        :type selections: array of json or selection object
        :param floating_semantics: If set to true the resulting dimension will
        have a floating semantics.
        :type floating_semantics: boolean

        Example:
            >>> xobject = session.get_object("Krankengeld")
            >>> xobject.add_aggregation_dimension(
                                             dimension_name="newDim",
                                             aggregation={
                                                     "object": "Krankengeld",
                                                     "dimension":"Anzahl_Tage",
                                                     "type": "AVG"
                                                    }
                                            )




        """
        method_call = {
            "method": "addAggregationDimension",
            "targetObject": self.object_name,
            "dimensionName": dimension_name,
            "aggregation": aggregation,
            "selections": selections,
            "floatingSemantics": floating_semantics
        }
        return self._ref_session.run(method_call)

