# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern.wrapt import ObjectProxy

import contrast
from contrast.agent import scope
from contrast.agent.policy import patch_manager
from contrast.agent.assess.policy.utils import build_method_name, logger
from contrast.agent.assess.policy.analysis import analyze
from contrast.utils.patch_utils import add_watermark


def build_assess_method(original_method, patch_policy):
    """
    Creates method to replace old method and call our assess code with the original method

    :param original_method: method to call for result
    :param patch_policy: PatchLocationPolicy containing all policy nodes for this patch
    :return: Newly created patch function
    """

    def assess_method(*args, **kwargs):
        context = contrast.CS__CONTEXT_TRACKER.current()

        try:
            result = original_method(*args, **kwargs)
        except Exception:
            result = None
            raise
        finally:
            analyze(context, patch_policy, result, args, kwargs)

        return result

    return add_watermark(assess_method)


def build_assess_classmethod(original_method, patch_policy):
    """
    Creates method to replace old method and call our assess code with the original method

    :param original_method: method to call for result
    :param patch_policy: PatchLocationPolicy containing all policy nodes for this patch
    :return: Newly created patch function

    A separate method was required for classmethod patch because we need to remove
    argument 1. arg 1 is the class. This is something that is automatically passed to
    the function so passing it again will cause a TypeError.
    """
    original_method = patch_manager.as_func(original_method)

    def assess_classmethod(*args, **kwargs):
        context = contrast.CS__CONTEXT_TRACKER.current()

        try:
            result = original_method(*args, **kwargs)
        except Exception:
            result = None
            raise
        finally:
            analyze(context, patch_policy, result, args, kwargs)

        return result

    return add_watermark(assess_classmethod)


def build_assess_deadzone(original_method, patch_policy):
    """
    Creates patch method that calls original method in contrast scope

    This prevents any analysis down the stack.

    :param original_method: method to call for result
    :param patch_policy: PatchLocationPolicy containing all policy nodes for this patch
    :return: Newly created patch function
    """

    def assess_deadzone(*args, **kwargs):
        with scope.contrast_scope():
            return original_method(*args, **kwargs)

    return add_watermark(assess_deadzone)


def build_assess_property_fget(original_property_name, patch_policy):
    """
    Creates property getter to replace old property and call assess code for analysis

    The new property calls the original property by looking for it in in the
    cs_assess_{property} location to return the property value, and run assess
    analysis.
    """
    cs_method_name = build_method_name(original_property_name)

    def assess_property(*args, **kwargs):
        context = contrast.CS__CONTEXT_TRACKER.current()
        try:
            cls_instance = args[0]
            result = getattr(cls_instance, cs_method_name)
        except Exception:
            result = None
            raise
        finally:
            analyze(context, patch_policy, result, args, kwargs)

        return result

    return add_watermark(assess_property)


def apply_cached_property(cls_or_module, patch_policy, property_name, orig_property):
    """
    Older werkzeug versions implement cached_property that does not inherit from property.
    This causes us to have to use a workaround for patching to avoid errors.

    Instead of replacing the cached_property with a new property, we replace it with
    and object proxy with a custom __get__ method.
    """
    proxied_property = CachedPropertyProxy(orig_property, property_name, patch_policy)

    try:
        setattr(cls_or_module, property_name, proxied_property)
    except Exception:
        logger.exception("Failed to apply patch to cached_property: %s", property_name)

    return True


class CachedPropertyProxy(ObjectProxy):
    cs__attr_name = None
    cs__patch_policy = None

    def __init__(self, wrapped, attr_name, patch_policy):
        super(CachedPropertyProxy, self).__init__(wrapped)
        self.cs__patch_policy = patch_policy
        self.cs__attr_name = attr_name

    def __get__(self, *args, **kwargs):
        context = contrast.CS__CONTEXT_TRACKER.current()
        result = self.__wrapped__.__get__(*args, **kwargs)

        try:
            # Self is the only arg that seems to be relevant for policy/reporting
            args = (self.__wrapped__,)
            analyze(context, self.cs__patch_policy, result, args, {})
        except Exception:
            logger.exception("Failed to apply policy for %s", self.cs__attr_name)

        return result
