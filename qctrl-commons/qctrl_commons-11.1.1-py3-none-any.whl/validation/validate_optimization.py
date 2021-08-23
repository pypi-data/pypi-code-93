"""
Validator for core__calculateOptimization mutation.
"""

from qctrlcommons.exceptions import QctrlFieldError
from qctrlcommons.validation.base import BaseMutationInputValidator
from qctrlcommons.validation.messages import Messages


class CalculateOptimizationValidator(BaseMutationInputValidator):
    """
    Validator for core__calculateOptimization mutation.
    """

    properties = {"optimizationCount": {"type": "number", "exclusiveMinimum": 0}}

    def check_cost_in_graph(self, input_: dict):  # pylint:disable=no-self-use
        """Expect the cost node to be in the graph.

        Parameters
        ----------
        input_ : dict
            the GraphQL input.

        Raises
        ------
        QctrlFieldError
            validation check failed
        """
        if input_["costNodeName"] not in input_["graph"]["operations"]:
            raise QctrlFieldError(
                message="Cost node must be present in graph.",
                fields=["costNodeName", "graph"],
            )

    def check_output_node_names(self, input_: dict):  # pylint:disable=no-self-use
        """
        Checks the following:
        1. At least 1 element in `outputNodeNames`
        2. All elements in `outputNodeNames` correspond to nodes in graph.

        Parameters
        ----------
        input_ : dict
            the GraphQL input.

        Raises
        ------
        QctrlFieldError
            validation check failed
        """
        output_node_names = input_["outputNodeNames"]
        graph_operations = input_["graph"]["operations"]

        if len(output_node_names) < 1:
            raise QctrlFieldError(
                message=Messages(
                    field_name="outputNodeNames", minimum=1, items="node name"
                ).min_items,
                fields=["outputNodeNames"],
            )
        for node_name in output_node_names:
            if node_name not in graph_operations:
                raise QctrlFieldError(
                    message=f"The requested output node name '{node_name}' is not"
                    + " present in the graph.",
                    fields=["outputNodeNames"],
                )
