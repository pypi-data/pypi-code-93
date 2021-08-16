class GraphQLProperty:
    def __init__(self, is_required=False):
        self.is_required = is_required

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value


class IntGraphQLProperty(GraphQLProperty):
    pass


class BaseGraphQLType(GraphQLProperty):
    def serialize(self, value):
        pass

    def deserialize(self, value):
        pass
