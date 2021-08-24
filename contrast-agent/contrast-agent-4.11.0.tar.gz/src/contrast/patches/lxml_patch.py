# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys

from contrast.extern.wrapt import CallableObjectProxy, register_post_import_hook

from contrast.agent.assess.policy.preshift import Preshift
from contrast.agent.assess.policy.analysis import _analyze
from contrast.agent.policy import patch_manager
from contrast.agent.policy.loader import Policy
from contrast.utils.decorators import fail_safely
from contrast.utils.patch_utils import build_and_apply_patch


@fail_safely("Failed to apply assess xpath-injection")
def apply_assess(location, self, retval, args, kwargs):
    policy = Policy()
    patch_policy = policy.policy_by_name.get(location)
    if patch_policy is None:
        return

    preshift = Preshift(self, args, kwargs)
    _analyze(patch_policy, preshift, self, retval, (self,) + args, kwargs)


def apply_call(class_name, orig_func, self, args, kwargs):
    result = None
    try:
        result = orig_func(*args, **kwargs)
    finally:
        location = "lxml.etree.{}.__call__".format(class_name)
        apply_assess(location, self, result, args, kwargs)
    return result


class ContrastXPathEvaluatorProxy(CallableObjectProxy):
    """
    Proxy class that wraps instances returned by XPathEvaluator factory

    We instrument the relevant classes directly, but since the factory is implemented
    as a C extension, the instances that it returns are the original type instead of
    our replacement. In order to cover all of our bases, we need both the replacement
    subclass and a proxied class that we return from the instrumented factory.
    """

    def __call__(self, *args, **kwargs):
        self_obj = self.__wrapped__
        orig_func = self.__wrapped__.__call__
        return apply_call(
            self_obj.__class__.__name__, orig_func, self_obj, args, kwargs
        )


def create_instrumented_xpath_element_evaluator(XPathElementEvaluator):
    """
    Generate instrumented subclass of XPathElementEvaluator

    We can't simply declare this at module level since we can't guarantee that lxml
    will be installed. We need to wait until the import hook is fired to know whether
    it's safe to make a reference to the original type.
    """

    class ContrastXPathElementEvaluator(XPathElementEvaluator):
        def __call__(self, *args, **kwargs):
            orig_func = super(ContrastXPathElementEvaluator, self).__call__
            return apply_call(
                XPathElementEvaluator.__name__, orig_func, self, args, kwargs
            )

    return ContrastXPathElementEvaluator


def create_instrumented_xpath_document_evaluator(XPathDocumentEvaluator):
    """
    Generate instrumented subclass of XPathDocumentEvaluator

    See docstring for create_instrumented_xpath_element_evaluator above.
    """

    class ContrastXPathDocumentEvaluator(XPathDocumentEvaluator):
        def __call__(self, *args, **kwargs):
            orig_func = super(ContrastXPathDocumentEvaluator, self).__call__
            return apply_call(
                XPathDocumentEvaluator.__name__, orig_func, self, args, kwargs
            )

    return ContrastXPathDocumentEvaluator


def create_instrumented_xpath(XPath):
    """
    Generate instrumented subclass of XPath

    We can't simply declare this at module level since we can't guarantee that lxml
    will be installed. We need to wait until the import hook is fired to know whether
    it's safe to make a reference to the original type.
    """

    class ContrastXPath(XPath):
        def __init__(self, *args, **kwargs):
            try:
                super(ContrastXPath, self).__init__(*args, **kwargs)
            finally:
                apply_assess("lxml.etree.XPath.__init__", self, None, args, kwargs)

    return ContrastXPath


def build_XPathEvaluator_patch(orig_func, _):
    def XPathEvaluator(*args, **kwargs):
        """
        Instrumented version of XPathEvaluator factory
        """
        evaluator = orig_func(*args, **kwargs)
        return ContrastXPathEvaluatorProxy(evaluator)

    return XPathEvaluator


def patch_etree(etree_module):
    build_and_apply_patch(etree_module, "XPathEvaluator", build_XPathEvaluator_patch)

    new_xpath = create_instrumented_xpath(etree_module.XPath)
    patch_manager.patch(etree_module, "XPath", new_xpath)

    new_element_evaluator = create_instrumented_xpath_element_evaluator(
        etree_module.XPathElementEvaluator
    )
    patch_manager.patch(etree_module, "XPathElementEvaluator", new_element_evaluator)

    new_document_evaluator = create_instrumented_xpath_document_evaluator(
        etree_module.XPathDocumentEvaluator
    )
    patch_manager.patch(etree_module, "XPathDocumentEvaluator", new_document_evaluator)


def register_patches():
    register_post_import_hook(patch_etree, "lxml.etree")


def reverse_patches():
    module = sys.modules.get("lxml.etree")
    if not module:
        return

    patch_manager.reverse_patches_by_owner(module)
