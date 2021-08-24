class RuleRequiresNameException(Exception):
    """Exception raised if a rule doesn't have a human readable name"""


class RuleRequiresIdException(Exception):
    """Exception raised if rule doesn't have an id"""


class MethodNotAllowedException(Exception):
    """Exception raised if a forbidden RuleauDict method is called"""


class CaseIdRequiredException(Exception):
    """Exception raised if a json path for case identifier is not found"""


class CannotOverrideException(Exception):
    """Exception raised if a API tries to override a rule marked as NO_OVERRIDE"""


class DuplicateRuleNameException(Exception):
    """Exception raised if more than 1 rule has same name"""


class RuleIdIllegalCharacterException(Exception):
    """Exception raise if Rule name contains illegal characters"""


class RuleFunctionNameAttributeCollisionException(Exception):
    """If the provided rule name collides with a rule attribute"""


class DuplicateRuleIdException(Exception):
    """Exception raised if more than 1 rule has same name"""


class APIException(Exception):
    """Generic exception for API request failure"""


class ConditionalDependencyReusedException(Exception):
    """Exception raised if the rule has duplicate dependencies"""


class RuleErrorException(Exception):
    """Exception raised when a rule raises an exception"""

    def __init__(self, rule, rule_exception):
        self.rule = rule
        self.rule_exception = rule_exception


class RunIfRuleHasRunIfException(Exception):
    """Exception raise if a run_if dependency of a rule also has a run_if."""
