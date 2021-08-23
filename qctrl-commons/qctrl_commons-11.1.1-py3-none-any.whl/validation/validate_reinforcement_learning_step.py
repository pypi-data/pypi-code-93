"""
Validator for core__calculateReinforcementLearningStep mutation.
"""
from qctrlcommons.exceptions import QctrlFieldError
from qctrlcommons.validation.base import BaseMutationInputValidator


def _check_policy_gradient_initializer(input_):
    """
    Checks input parameters for the policy gradient agent.
    """
    initializer = input_["agent"]["policyGradientInitializer"]
    discrete_action_space_size = initializer["discreteActionSpaceSize"]
    discount_factor = initializer["rewardDiscountFactor"]

    # Note: When adding continuous action spaces in the future,
    # this may be allowed to be zero if a continuous space is provided.
    if discrete_action_space_size <= 0:
        raise QctrlFieldError(
            message="The discrete action space size must be a positive integer.",
            fields=["discreteActionSpaceSize"],
        )
    if discount_factor < 0 or discount_factor > 1:
        raise QctrlFieldError(
            message="The reward discount factor must be non-negative and at most 1.",
            fields=["rewardDiscountFactor"],
        )


AVAILABLE_AGENTS = {"policyGradientInitializer": _check_policy_gradient_initializer}


class CalculateReinforcementLearningStepValidator(BaseMutationInputValidator):
    """
    Validator for core__calculateReinforcementLearningStep mutation.
    """

    def check_agent(self, input_):  # pylint:disable=no-self-use
        """
        Check agent.
        1. only one agent initializer is allowed.
        2. exactly one of initializers or state can be set.
        3. check inputs for agent initializer.

        Raises
        ------
        QctrlFieldError
            If one of conditions above fails.
        """

        agent = input_.get("agent")

        if len(agent) != 1:
            raise QctrlFieldError(
                message="Exactly one field in `agent` must be set."
                " One of the agent initializers must be set in the first step and"
                " `state` must be updated for following learning steps.",
                fields=["agent"],
            )

        # agent initializer validation is optional. That is, we might not
        # add validators for optimizers with some simple parameters.
        initializer_key = next(iter(agent))
        if initializer_key in AVAILABLE_AGENTS:
            AVAILABLE_AGENTS[initializer_key](input_)

    def check_environment_feedbacks(self, input_):  # pylint:disable=no-self-use
        """
        Check environment feedbacks are structured properly:
        1. all observations must have the same dimensionality
        2. all observations must be non-empty
        3. if provided, exactly one reward must be given per observation.

        Raises
        ------
        QctrlFieldError
            If one of the above conditions fail.
        """

        feedbacks = input_["environmentFeedbacks"]
        if not all(fb.get("observation") for fb in feedbacks):
            raise QctrlFieldError(
                message="All feedbacks must have non-empty observations.",
                fields=["environmentFeedbacks"],
            )
        if len(set(len(fb["observation"]) for fb in feedbacks)) > 1:
            raise QctrlFieldError(
                message="All observations in a batch should be the same size.",
                fields=["environmentFeedbacks"],
            )
