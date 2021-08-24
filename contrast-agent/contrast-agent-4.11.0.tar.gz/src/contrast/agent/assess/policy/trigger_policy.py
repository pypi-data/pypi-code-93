# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern.six import iteritems

import contrast
from contrast.agent.assess.apply_trigger import cs__apply_trigger
from contrast.utils.decorators import log_time


@log_time("applying trigger policy")
def apply(
    rule, trigger_nodes, ret, args, kwargs=None
):  # pylint: disable=redefined-builtin
    """
    Iterates over all given trigger policy nodes and applies the given rule

    This method gets called from within a patched trigger function in order
    to determine whether the given rule has been violated.

    @param rule: `TriggerRule` instance representing rule to be evaluated
    @param trigger_nodes: List of `TriggerNode` instances
    @param ret: Result returned by the trigger function
    @param args: Tuple containing args passed to trigger function
    @param kwargs: Dict containing kwargs passed to trigger function
    """
    kwargs = kwargs or {}

    context = contrast.CS__CONTEXT_TRACKER.current()
    if context is None:
        return

    for node in trigger_nodes:
        if node.instance_method:
            self_obj = args[0]
            args = args[1:]  # args[0] is `self` for instance methods
        else:
            self_obj = None  # module-level functions do not have a self
            args = args

        possible_sources = node.get_matching_sources(self_obj, ret, args, kwargs)

        for source in possible_sources:
            if isinstance(source, dict):
                for key, value in iteritems(source):
                    cs__apply_trigger(
                        context, rule, node, key, self_obj, ret, None, args, kwargs
                    )
                    # pass in the key here for building_finding
                    cs__apply_trigger(
                        context, rule, node, value, self_obj, ret, key, args, kwargs
                    )
            elif isinstance(source, (tuple, list)):
                for item in source:
                    cs__apply_trigger(
                        context, rule, node, item, self_obj, ret, None, args, kwargs
                    )
            else:
                cs__apply_trigger(
                    context, rule, node, source, self_obj, ret, None, args, kwargs
                )
        else:
            if not rule.dataflow:
                cs__apply_trigger(
                    context, rule, node, None, self_obj, ret, None, args, kwargs
                )
