import xplain


class Dimension():
    object_name = None
    dimension_name = None
    _ref_session = None

    def __init__(self, object_name, dimension_name, ref_session):
        self.object_name = object_name
        self.dimension_name = dimension_name
        self._ref_session = ref_session

    def get_name(self):
        return self.dimension_name

    def get_attributes(self):
        """
        get the list of attributes attached to this dimension

        :returns: list of instances
        """
        list_attributes = []
        json_details = self._ref_session.get_tree_details(
            object_name=self.object_name,
            dimension_name=self.dimension_name)

        if (json_details.get("attributes") is not None):
            for attribute_obj in json_details["attributes"]:
                attr = xplain.Attribute(object_name=self.object_name,
                                        dimension_name=self.dimension_name,
                                        attribute_name=attribute_obj[
                                            "attributeName"],
                                        ref_session=self._ref_session)
                list_attributes.append(attr)
        return list_attributes

    def get_attribute(self, attribute_name):
        """
        get the attribute instance of the given name

        :param attribute_name: the name of attribute
        :return: an instance of attribute object
        """
        attribute_found = None
        json_details = self._ref_session.get_tree_details(
            object_name=self.object_name,
            dimension_name=self.dimension_name)

        if json_details.get("attributes") is not None:
            for attribute_obj in json_details["attributes"]:
                if attribute_obj["attributeName"] == attribute_name:
                    attribute_found = xplain.Attribute(
                        object_name=self.object_name,
                        dimension_name=self.dimension_name,
                        attribute_name=attribute_obj["attributeName"],
                    ref_session=self._ref_session)
        return attribute_found
