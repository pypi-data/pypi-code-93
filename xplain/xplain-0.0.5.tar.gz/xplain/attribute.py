import xplain

class Attribute():
    def __init__(self, object_name, dimension_name, attribute_name,
                 ref_session):
        self.object_name = object_name
        self.dimension_name = dimension_name
        self.attriubte_name = attribute_name
        self._ref_session = ref_session

    def get_name(self):
        return self.attriubte_name

    def get_levels(self):
        """
        returns the level names of this attribute
        :return: levels as array of string
        """
        json_details = xplain.get_tree_details(object_name=self.object_name,
                                               dimension_name=self.dimension_name,
                                               attribute_name=self.attriubte_name)
        return json_details["hierarchyLevelNames"]

    def get_state_hierarchy(self):
        """
        state hierarchy of this attribute
        :return: hierarcy as JSON
        """
        return xplain.get_state_hierarchy(self.object_name,self.dimension_name,self.attriubte_name)

    def get_root_state(self):
        """
        returns the root state of this attribute
        :return: string
        """
        return self.get_state_hierarchy()["stateName"]
