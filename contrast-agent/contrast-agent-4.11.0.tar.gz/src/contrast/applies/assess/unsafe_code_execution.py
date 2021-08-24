# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern.six import string_types, binary_type

from contrast.agent import scope
from contrast.agent.policy.loader import Policy
from contrast.agent.assess.policy import trigger_policy
from contrast.utils.decorators import fail_safely


@fail_safely("Error running unsafe code execution assess rule")
def apply_rule(module_name, method_name, result, args, kwargs):
    if len(args) < 1:
        return

    if not isinstance(args[0], string_types + (binary_type, bytearray)):
        return

    policy = Policy()
    trigger_rule = policy.triggers["unsafe-code-execution"]

    trigger_nodes = trigger_rule.find_trigger_nodes(module_name, method_name)

    with scope.trigger_scope():
        trigger_policy.apply(trigger_rule, trigger_nodes, result, args, kwargs)
