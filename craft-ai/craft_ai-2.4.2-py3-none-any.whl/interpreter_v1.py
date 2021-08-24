import numbers

from craft_ai.errors import CraftAiDecisionError, CraftAiNullDecisionError
from craft_ai.operators import (
    OPERATORS_V1 as OPERATORS,
    OPERATORS_FUNCTION_V1 as OPERATORS_FUNCTION,
)
from craft_ai.types import TYPES
from craft_ai.timezones import is_timezone

_DECISION_VERSION = "1.1.0"

_VALUE_VALIDATORS = {
    TYPES["continuous"]: lambda value: isinstance(value, numbers.Real),
    TYPES["enum"]: lambda value: isinstance(value, str),
    TYPES["timezone"]: lambda value: is_timezone(value),
    TYPES["time_of_day"]: lambda value: (
        isinstance(value, numbers.Real) and value >= 0 and value < 24
    ),
    TYPES["day_of_week"]: lambda value: (
        isinstance(value, int) and value >= 0 and value <= 6
    ),
    TYPES["day_of_month"]: lambda value: (
        isinstance(value, int) and value >= 1 and value <= 31
    ),
    TYPES["month_of_year"]: lambda value: (
        isinstance(value, int) and value >= 1 and value <= 12
    ),
}

############################
# Interpreter for V1 Trees #
############################


class InterpreterV1(object):
    @staticmethod
    def decide(configuration, bare_tree, context):
        InterpreterV1._check_context(configuration, context)

        decision_result = {}
        decision_result["output"] = {}
        for output in configuration.get("output"):
            root = bare_tree[output]

            if not ("children" in root and len(root.get("children"))):
                predicted_value = root.get("predicted_value")
                if predicted_value is None:
                    raise CraftAiNullDecisionError(
                        """Unable to take decision: the decision tree is not based"""
                        """ on any context operations.""",
                    )

            decision = InterpreterV1._decide_recursion(bare_tree[output], context)
            decision_result["output"][output] = decision

        decision_result["_version"] = _DECISION_VERSION
        return decision_result

    ####################
    # Internal helpers #
    ####################

    @staticmethod
    def _decide_recursion(node, context):
        # If we are on a leaf
        if not ("children" in node and len(node.get("children"))):
            predicted_value = node.get("predicted_value")
            if predicted_value is None:
                raise CraftAiNullDecisionError(
                    """Unable to take decision: the decision tree has no valid"""
                    """ predicted value for the given context.""",
                    {"decision_rules": [node.get("decision_rule")]},
                )

            leaf = {
                "predicted_value": predicted_value,
                "confidence": node.get("confidence") or 0,
                "decision_rules": [],
            }

            if node.get("standard_deviation", None) is not None:
                leaf["standard_deviation"] = node.get("standard_deviation")

            return leaf

        # Finding the first element in this node's childrens matching the
        # operator condition with given context
        matching_child = InterpreterV1._find_matching_child(node, context)

        if not matching_child:
            prop = node.get("children")[0].get("decision_rule").get("property")
            operand_list = [
                child["decision_rule"]["operand"] for child in node["children"]
            ]
            decision_rule = (
                [node["decision_rule"]] if not node.get("decision_rule") is None else []
            )
            raise CraftAiNullDecisionError(
                """Unable to take decision: value '{}' for property '{}' doesn't"""
                """ validate any of the decision rules.""".format(
                    context.get(prop), prop
                ),
                {
                    "decision_rules": decision_rule,
                    "expected_values": operand_list,
                    "property": prop,
                    "value": context.get(prop),
                },
            )

        # If a matching child is found, recurse
        try:
            result = InterpreterV1._decide_recursion(matching_child, context)
        except CraftAiDecisionError as err:
            metadata = err.metadata
            if node.get("decision_rule"):
                metadata["decision_rules"].insert(0, node["decision_rule"])
            raise CraftAiDecisionError(err.message, metadata)

        new_predicates = [
            {
                "property": matching_child["decision_rule"]["property"],
                "operator": matching_child["decision_rule"]["operator"],
                "operand": matching_child["decision_rule"]["operand"],
            }
        ]

        final_result = {
            "predicted_value": result["predicted_value"],
            "confidence": result["confidence"],
            "decision_rules": new_predicates + result["decision_rules"],
        }

        if result.get("standard_deviation", None) is not None:
            final_result["standard_deviation"] = result.get("standard_deviation")

        return final_result

    @staticmethod
    def _find_matching_child(node, context):
        for child in node["children"]:
            property_name = child["decision_rule"]["property"]
            operand = child["decision_rule"]["operand"]
            operator = child["decision_rule"]["operator"]
            context_value = context.get(property_name)
            # If there is no context value:
            if context_value is None:
                raise CraftAiDecisionError(
                    """Unable to take decision, """
                    """property '{}' is missing from the given context.""".format(
                        property_name
                    )
                )
            if not isinstance(operator, str) or operator not in OPERATORS.values():
                raise CraftAiDecisionError(
                    """Invalid decision tree format, {} is not a valid"""
                    """ decision operator.""".format(operator)
                )

            # To be compared, continuous parameters should not be strings
            if TYPES["continuous"] in operator:
                context_value = float(context_value)
                operand = float(operand)

            if OPERATORS_FUNCTION[operator](context_value, operand):
                return child
        return {}

    @staticmethod
    def _check_context(configuration, context):
        # Extract the required properties (i.e. those that are not the output)
        expected_properties = [
            p for p in configuration["context"] if p not in configuration["output"]
        ]

        # Retrieve the missing properties
        missing_properties = [
            p for p in expected_properties if p not in context or context[p] is None
        ]

        # Validate the values
        bad_properties = [
            p
            for p in expected_properties
            if not InterpreterV1.validate_property_value(configuration, context, p)
        ]

        if missing_properties or bad_properties:
            missing_properties = sorted(missing_properties)
            missing_properties_messages = [
                "expected property '{}' is not defined".format(p)
                for p in missing_properties
            ]
            bad_properties = sorted(bad_properties)
            bad_properties_messages = [
                "'{}' is not a valid value for property '{}' of type '{}'".format(
                    context[p], p, configuration["context"][p]["type"]
                )
                for p in bad_properties
            ]

            errors = missing_properties_messages + bad_properties_messages

            # deal with missing properties
            if errors:
                message = (
                    "Unable to take decision, the given context is not valid: "
                    + errors.pop(0)
                )

                for error in errors:
                    message = "".join((message, ", ", error))

                message = message + "."

                metadata = {}
                if bad_properties:
                    metadata["badProperties"] = [
                        {
                            "property": p,
                            "type": configuration["context"][p]["type"],
                            "value": context[p],
                        }
                        for p in bad_properties
                    ]
                if missing_properties:
                    metadata["missingProperties"] = missing_properties

                raise CraftAiDecisionError(message, metadata)

    @staticmethod
    def validate_property_value(configuration, context, property_name):
        if context.get(property_name) is None:
            return True

        property_type = configuration["context"][property_name]["type"]
        if property_type in _VALUE_VALIDATORS:
            property_value = context[property_name]
            return _VALUE_VALIDATORS[property_type](property_value)
        return True
