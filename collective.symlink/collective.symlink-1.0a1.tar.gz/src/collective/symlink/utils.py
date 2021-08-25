# -*- coding: utf-8 -*-

from Acquisition import aq_inner  # noqa
from Acquisition import aq_parent  # noqa
from Products.CMFPlone.utils import base_hasattr
from zc.relation.interfaces import ICatalog

from zope.component import getUtility
from zope.intid import IIntIds


def is_linked_object(obj):
    """ Check if the obj is a symlink or is a child of a symlink.
    :param obj: obj to check
    :type obj: object
    :returns: tuple with link, symlink object, original object, relative_path
    """
    ret = ["", None, None, ""]
    parent = obj
    while not parent.portal_type == "Plone Site":
        if base_hasattr(parent, "_link_portal_type"):
            ret = [parent._link_portal_type, parent, parent._link, ""]  # noqa
            if obj != parent:
                ret[3] = "/".join(
                    obj.getPhysicalPath()[len(parent.getPhysicalPath()) :]
                )
            break
        parent = aq_parent(aq_inner(parent))
    return tuple(ret)


def query_links_to_object(obj):
    """query all links pointing to a given object.
    :param obj:
    :return: list of links
    """
    intids = getUtility(IIntIds)
    to_id = intids.queryId(obj)
    links = []
    if to_id:
        catalog = getUtility(ICatalog)
        links = catalog.findRelations(
            {"to_id": to_id, "from_attribute": "symbolic_link"}
        )
    return links
