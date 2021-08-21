class RenameFieldsSerializerMixin:
    def to_internal_value(self, data):
        mapped_data = data.__class__()
        for external, internal in self.field_name_map.items():
            if external in data:
                mapped_data[internal] = data[external]

        return super().to_internal_value(mapped_data)
