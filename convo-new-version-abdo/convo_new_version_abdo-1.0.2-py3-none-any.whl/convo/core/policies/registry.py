# Import all policies at one place to be able to to resolve them via a common module
# path. Don't do this in `__init__.py` to avoid importing them without need.

# noinspection PyUnresolvedReferences
from convo.core.policies.ted_policy import TEDPolicy

# noinspection PyUnresolvedReferences
from convo.core.policies.fallback import PolicyFallback

# noinspection PyUnresolvedReferences
from convo.core.policies.memoization import MemoizationPolicy, AugmentedMemoizationPolicy

# noinspection PyUnresolvedReferences
from convo.core.policies.sklearn_policy import PolicySkLearn

# noinspection PyUnresolvedReferences
from convo.core.policies.form_policy import FormPolicy

# noinspection PyUnresolvedReferences
from convo.core.policies.two_stage_fallback import TwoStageFallbackPolicy

# noinspection PyUnresolvedReferences
from convo.core.policies.mapping_policy import MappingPolicy

# noinspection PyUnresolvedReferences
from convo.core.policies.rule_policy import RulePolicy
