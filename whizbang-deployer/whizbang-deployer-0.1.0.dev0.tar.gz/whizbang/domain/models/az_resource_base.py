class AzResourceBase:
    def __init__(self, resource_name, resource_group_name, location):
        self.location = location
        self.resource_group_name = resource_group_name
        self.resource_name = resource_name


class AzResourceGroup(AzResourceBase):
    def __init__(self, resource_group_name, location):
        self.resource_name = None
        AzResourceBase.__init__(self, self.resource_name, resource_group_name, location)
