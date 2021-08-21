from rest_framework.fields import ListField


class StringArrayField(ListField):
    def to_representation(self, obj):
        return ",".join(str(element) for element in obj.all())

    def to_internal_value(self, data):
        return super().to_internal_value(data.split(","))
