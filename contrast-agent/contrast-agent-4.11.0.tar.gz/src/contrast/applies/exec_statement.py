# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import contrast
from contrast.agent.assess.apply_trigger import build_finding
from contrast.agent.policy.loader import Policy
from contrast.agent.assess.policy.analysis import skip_analysis


def apply_rule(string, ptr_val):
    """
    Applies unsafe-code-execution rule for exec statement in PY2

    This function is only ever called from extension code. In order to
    determine whether the rule has been violated, we need to do a reverse
    lookup based on the pointer value of the underlying char buffer that
    corresponds to the string object. This is because our hook for the exec
    statement does not see a PyObject but instead is only passed the underlying
    char buffer.
    """
    props = contrast.STRING_TRACKER.lookup_by_pointer(ptr_val)
    if props is None:
        return

    # TODO: PYT-915 handle the unicode case where we need to remove the propagation
    # event that is created when the string is encoded into UTF-8. Since this
    # doesn't happen in user-controlled or library code, it will be confusing
    # when reporting, so we should try to remove it. Ideally we will be able to
    # just grab the properties belonging to the pre-encoded unicode object.

    context = contrast.CS__CONTEXT_TRACKER.current()
    if context is None or skip_analysis(context):
        return

    policy = Policy()
    trigger_rule = policy.triggers["unsafe-code-execution"]
    trigger_nodes = trigger_rule.find_trigger_nodes("BUILTIN", "exec")

    for node in trigger_nodes:
        if trigger_rule.is_violated_properties(node, props):
            args = (string,)
            kwargs = {}

            build_finding(
                context,
                trigger_rule,
                node,
                string,
                None,
                None,
                None,
                args,
                kwargs,
                target_properties=props,
            )
