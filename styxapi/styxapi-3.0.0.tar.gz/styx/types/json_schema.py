
def json_schema(type_):
    return type_.visit(JsonSchemaVisitor())


class JsonSchemaVisitor:

    def visit_any(self, node):
        return {}

    def visit_null(self, node):
        return {
            "type": "null"
        }

    def visit_string(self, node):
        return {
            "type": "string"
        }

    def visit_integer(self, node):
        return {
            "type": "integer"
        }

    def visit_boolean(self, node):
        return {
            "type": "boolean"
        }

    def visit_object(self, node):
        return {
            "type": "object",
            "properties": {name: field.visit(self)
                    for name, field in node.fields.items()},
            "required": list(node.fields.keys()),
            "additionalProperties": False,
        }

    def visit_list(self, node):
        return {
            "type": "array",
            "items": node.type.visit(self)
        }

    def visit_const(self, node):
        return {
            "enum": [node.value]
        }

    def visit_unset(self, node):
        return {"not": {}}

    def visit_reference(self, node):
        return {"$ref": f"#/components/schemas/{ node.name }"}
