from rest_framework import serializers


class RenameFieldsSerializerMixin:
    def to_internal_value(self, data):
        mapped_data = data.__class__()
        for external, internal in self.field_name_map.items():
            if external in data:
                mapped_data[internal] = data[external]

        return super().to_internal_value(mapped_data)


class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data
