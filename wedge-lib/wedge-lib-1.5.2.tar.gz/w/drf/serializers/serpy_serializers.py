from w.serializers import serializer


class ReferenceSerializer(serializer.SerpySerializer):
    code = serializer.StrField()
    label = serializer.StrField()


class I18nReferenceSerializer(ReferenceSerializer):
    label = serializer.TranslateField()


class UserSerializer(serializer.SerpySerializer):
    id = serializer.IntField()
    username = serializer.Field()
    first_name = serializer.Field()
    last_name = serializer.Field()
    email = serializer.Field()
    is_active = serializer.BoolField()


class UserWithDateSerializer(UserSerializer):
    date_joined = serializer.DateField()
