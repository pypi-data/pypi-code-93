from typing import Dict, Text, Any


def entity_dictionary_schema() -> Dict[Text, Any]:
    """Returns: schema for defining entities in Markdown format."""
    return {
        "type": "object",
        "properties": common_entity_props(),
        "required": ["entity"],
    }


def common_entity_props() -> Dict[Text, Any]:
    return {
        "entity": {"type": "string"},
        "role": {"type": "string"},
        "group": {"type": "string"},
        "value": {"type": "string"},
    }


def nlu_data_schema() -> Dict[Text, Any]:
    """Returns: schema of the Convo NLU data format (json format)."""
    entity_props = common_entity_props()
    entity_props["start"] = {"type": "number"}
    entity_props["end"] = {"type": "number"}

    training_exp_schema = {
        "type": "object",
        "properties": {
            "intent": {"type": "string"},
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": entity_props,
                    "required": ["start", "end", "entity"],
                },
            },
        },
    }

    regular_expression_feature_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "pattern": {"type": "string"}},
    }

    look_up_table_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "elements": {
                "oneOf": [
                    {"type": "array", "items": {"type": "string"}},
                    {"type": "string"},
                ]
            },
        },
    }

    return {
        "type": "object",
        "properties": {
            "convo_nlu_data": {
                "type": "object",
                "properties": {
                    "regex_features": {"type": "array", "items": regular_expression_feature_schema},
                    "common_examples": {
                        "type": "array",
                        "items": training_exp_schema,
                    },
                    "intent_exp": {
                        "type": "array",
                        "items": training_exp_schema,
                    },
                    "entity_examples": {
                        "type": "array",
                        "items": training_exp_schema,
                    },
                    "lookup_tables": {"type": "array", "items": look_up_table_schema},
                },
            }
        },
        "additionalProperties": False,
    }
