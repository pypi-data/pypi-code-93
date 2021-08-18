# -*- coding: utf-8 -*-
"""
    binalyzer_core.utils
    ~~~~~~~~~~~~~~~~~~~~

    This module implements helper and utility functions.

    :copyright: 2021 Denis Vasilík
    :license: MIT
"""
from anytree import NodeMixin
from anytree.util import leftsibling, rightsibling


def siblings(node: NodeMixin):
    siblings = []
    siblings.extend(leftsiblings(node))
    siblings.extend(rightsiblings(node))
    return siblings


def leftsiblings(node: NodeMixin):
    siblings = []
    sibling = leftsibling(node)
    while sibling:
        siblings.append(sibling)
        sibling = leftsibling(sibling)
    siblings.reverse()
    return siblings


def rightsiblings(node: NodeMixin):
    siblings = []
    sibling = rightsibling(node)
    while sibling:
        siblings.append(sibling)
        sibling = rightsibling(sibling)
    return siblings
