from w.serializers import serializer


class SimpleSerializer(serializer.SerpySerializer):
    integer = serializer.IntField()
    string = serializer.StrField()
    date = serializer.DateField()


class InternalDependencyOneSerializer(serializer.SerpySerializer):
    id = serializer.Field()
    name = serializer.Field()


class InternalDependencyTwoSerializer(serializer.SerpySerializer):
    id = serializer.Field()
    name = serializer.Field()


class ExampleSerializer(serializer.SerpySerializer):
    id = serializer.Field()
    name = serializer.Field()
    internal_one = InternalDependencyOneSerializer()
    internal_two = InternalDependencyTwoSerializer()
