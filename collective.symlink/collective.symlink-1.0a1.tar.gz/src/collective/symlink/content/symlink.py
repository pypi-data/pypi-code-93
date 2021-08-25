# -*- coding: utf-8 -*-

from Acquisition import aq_base, aq_inner, aq_parent
from collective.symlink import _
from plone.app.iterate.interfaces import IIterateAware
from plone.app.layout.globals.context import ContextState
from plone.app.versioningbehavior.behaviors import IVersioningSupport
from plone.dexterity.browser import edit
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.content import Container
from plone.folder.ordered import CMFOrderedBTreeFolderBase
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.supermodel import model
from plone.uuid.interfaces import IAttributeUUID
from plone.uuid.interfaces import IUUIDAware
from plone.uuid.interfaces import IUUIDGenerator
from z3c.relationfield.schema import RelationChoice
from zope.component import ComponentLookupError
from zope.component import queryUtility
from zope.interface import Interface
from zope.interface import implementer
from zope.interface.declarations import ObjectSpecificationDescriptor
from zope.interface.declarations import getObjectSpecification
from zope.interface.declarations import implementedBy
from zope.interface.declarations import providedBy
from zope.intid.interfaces import IIntIds

import types

_marker = object()


class ISymlinkMarker(Interface):
    """ Marker interface for Symlink content types """


class ISymlink(model.Schema):
    symbolic_link = RelationChoice(
        title=_(u"Symbolic link"), source=ObjPathSourceBinder(), required=True
    )


class DelegatingSpecification(ObjectSpecificationDescriptor):
    """
    Get from collective.alias
    A __providedBy__ decorator that returns the interfaces provided by
    the object, plus those of the cached object.
    """

    def __get__(self, inst, cls=None):
        # We're looking at a class - fall back on default
        if inst is None:
            return getObjectSpecification(cls)

        # Find the cached value.
        cache = getattr(inst, "_v__providedBy__", None)

        # Find the data we need to know if our cache needs to be invalidated
        provided = link_provides = getattr(inst, "__provides__", None)

        # See if we have a valid cache, and if so return it
        if cache is not None:
            cached_mtime, cached_provides, cached_provided = cache

            if inst._p_mtime == cached_mtime and link_provides is cached_provides:
                return cached_provided

        # If the instance doesn't have a __provides__ attribute, get the
        # interfaces implied by the class as a starting point.
        if provided is None:
            provided = implementedBy(cls)

        # Add the interfaces provided by the target
        link = aq_base(inst._link)
        if link is None:
            return provided - IIterateAware - IVersioningSupport  # don't cache yet!

        # Add the interfaces provided by the target, but ensure that some problematic
        # interfaces are removed
        provided += providedBy(link) - IIterateAware - IVersioningSupport
        provided += ISymlinkMarker

        inst._v__providedBy__ = inst._p_mtime, link_provides, provided
        return provided


class SubItemDelegatingSpecification(ObjectSpecificationDescriptor):
    """
    Get from collective.alias
    A __providedBy__ decorator that returns the interfaces provided by
    the object, plus those of the cached object.
    """

    def __get__(self, inst, cls=None):
        # We're looking at a class - fall back on default
        if inst is None:
            return getObjectSpecification(cls)

        # Find the cached value.
        cache = getattr(inst, "_v__providedBy__", None)

        # Find the data we need to know if our cache needs to be invalidated
        provided = link_provides = getattr(inst._context, "__provides__", None)

        # See if we have a valid cache, and if so return it
        if cache is not None:
            cached_mtime, cached_provides, cached_provided = cache

            if inst._p_mtime == cached_mtime and link_provides is cached_provides:
                return cached_provided

        # If the instance doesn't have a __provides__ attribute, get the
        # interfaces implied by the class as a starting point.
        if provided is None:
            provided = implementedBy(cls)

        # Add the interfaces provided by the target, but ensure that some problematic
        # interfaces are removed
        provided += providedBy(inst._context) - IIterateAware - IVersioningSupport
        provided += ISymlinkMarker

        inst._v__providedBy__ = inst._p_mtime, link_provides, provided
        return provided


@implementer(ISymlinkMarker)
class SymlinkSubItem(Container):

    cmf_uid = None
    __providedBy__ = SubItemDelegatingSpecification()

    def __init__(self, context):
        self._context = context

    @property
    def id(self):
        return self._context.getId()

    def Title(self):
        return aq_inner(self._context).Title()

    def Description(self):
        return aq_inner(self._context).Description()

    @property
    def title(self):
        # we have to define a property because self.title always works for a dexterity object and returns '',
        # even if there is no title attribute. => self.title don't pass in __getattr__
        return aq_inner(self._context).title

    @title.setter
    def title(self, value):
        # title attribute is set to '' in Products/CMFCore/PortalFolder.py __init__
        # a set attribute is not gotten from the linked object (don't pass in __getattr__) !
        # => we don't set the title
        pass

    @property
    def description(self):
        # we have to define a property because self.description always works for a dexterity object and returns '',
        # even if there is no title attribute. => self.description don't pass in __getattr__
        return aq_inner(self._context).description

    @description.setter
    def description(self, value):
        # description attribute is set to '' in Products/CMFCore/PortalFolder.py __init__
        # a set attribute is not gotten from the linked object (don't pass in __getattr__) !
        # => we don't set the description
        pass

    @property
    def workflow_history(self):
        return aq_inner(self._context).workflow_history

    @workflow_history.setter
    def workflow_history(self, value):
        return

    @workflow_history.deleter
    def workflow_history(self):
        return

    def allowedContentTypes(self):
        return []

    def __contains__(self, key):
        return self._context.__contains__(key)

    @property
    def portal_type(self):
        return self._context.portal_type

    def __get_uid(self):
        link = aq_inner(self._context).aq_parent
        while not ISymlink.providedBy(link):
            link = aq_inner(link).aq_parent
        uuids = getattr(link, "_link.uuids", None)
        path = self._context.getPhysicalPath()
        if uuids is None:
            uuids = {}
            setattr(link, "_link.uuids", uuids)
        if path not in uuids:
            uuids[path] = queryUtility(IUUIDGenerator)()
        return uuids[path]

    def UID(self):
        return self.__get_uid()

    def __getattr__(self, key):
        """ Pass only here if key attribute is not set on symlink ! """
        # Inspired by collective.alias
        if (
            key.startswith("_v_")
            or key.startswith("_p_")
            or key.endswith("_Permission")
        ):
            raise AttributeError(key)

        if key == "_plone.uuid":
            return self.__get_uid()

        context = aq_inner(self._context)

        if not hasattr(aq_base(context), key):
            return super(SymlinkSubItem, self).__getattr__(key)

        context_attr = getattr(context, key, _marker)

        if context_attr is _marker:
            return super(SymlinkSubItem, self).__getattr__(key)

        # if this is an acquisition wrapped object, re-wrap it in the alias
        if aq_parent(context_attr) is context:
            # Try to access to subitem
            if key in context.keys():
                context_attr = SymlinkSubItem(context_attr).__of__(self)
            else:
                context_attr = aq_base(context_attr).__of__(self)

        # if it is a bound method, re-bind it so that im_self is the alias
        if isinstance(context_attr, types.MethodType):
            return types.MethodType(context_attr.im_func, self, type(self))

        return context_attr

    def objectIds(self, spec=None, ordered=True):
        return self._context.objectIds(spec)

    def __getitem__(self, key):
        return SymlinkSubItem(self._context.__getitem__(key)).__of__(self)

    def _getOb(self, id, default=_marker):
        obj = self._context._getOb(id, default)
        if obj is default:
            if default is _marker:
                raise KeyError(id)
            return default
        return SymlinkSubItem(aq_base(obj).__of__(self)).__of__(self)


@implementer(ISymlink, IUUIDAware, IAttributeUUID)
class Symlink(Container):

    cmf_uid = None
    cb_dataValid = lambda s: False  # This hide the paste button
    _link_portal_type = None
    __providedBy__ = DelegatingSpecification()

    def __call__(self):
        template = self._link.unrestrictedTraverse(self._link.getLayout())
        template.context = self
        return template()

    def Title(self):
        link = self._link
        if link is not None:
            return aq_inner(link).Title()

    def Description(self):
        link = self._link
        if link is not None:
            return aq_inner(link).Description()

    @property
    def title(self):
        # we have to define a property because self.title always works for a dexterity object and returns '',
        # even if there is no title attribute. => self.title don't pass in __getattr__
        if self._link is None:
            return u""
        return aq_inner(self._link).title

    @title.setter
    def title(self, value):
        # title attribute is set to '' in Products/CMFCore/PortalFolder.py __init__
        # a set attribute is not gotten from the linked object (don't pass in __getattr__) !
        # => we don't set the title
        pass

    @property
    def description(self):
        # we have to define a property because self.description always works for a dexterity object and returns '',
        # even if there is no title attribute. => self.description don't pass in __getattr__
        if self._link is None:
            return u""
        return aq_inner(self._link).description

    @description.setter
    def description(self, value):
        # description attribute is set to '' in Products/CMFCore/PortalFolder.py __init__
        # a set attribute is not gotten from the linked object (don't pass in __getattr__) !
        # => we don't set the description
        pass

    @property
    def portal_type(self):
        link = self._link
        if self._link is None:
            return self.__getattribute__("_link_portal_type")
        return aq_inner(link).portal_type

    @portal_type.setter
    def portal_type(self, value):
        self._link_portal_type = value

    @property
    def workflow_history(self):
        link = self._link
        if self._link is None:
            return None
        return aq_inner(link).workflow_history

    @workflow_history.setter
    def workflow_history(self, value):
        return

    @workflow_history.deleter
    def workflow_history(self):
        return

    def allowedContentTypes(self):
        return []

    def __contains__(self, key):
        return self._link.__contains__(key)

    @property
    def _link(self):
        if "symbolic_link" not in self.__dict__:
            return None
        try:
            return self.__getattribute__("symbolic_link").to_object
        except ComponentLookupError as e:
            if getattr(e, "args", [""])[0] == IIntIds:
                return  # This happen when we try to remove the Plone object
            raise e

    def __getattr__(self, key):
        """ Pass only here if key attribute is not set on symlink ! """
        # Inspired by collective.alias
        if (
            key.startswith("_v_")
            or key.startswith("_p_")
            or key.endswith("_Permission")
        ):
            raise AttributeError(key)

        if key == "_plone.uuid":
            return super(Symlink, self).__getattr__(key)

        link = self._link
        if link is None:
            return super(Symlink, self).__getattr__(key)

        link = aq_inner(link)

        if not hasattr(aq_base(link), key):
            return super(Symlink, self).__getattr__(key)

        link_attr = getattr(link, key, _marker)

        if link_attr is _marker:
            return super(Symlink, self).__getattr__(key)

        # if this is an acquisition wrapped object, re-wrap it in the alias
        if aq_parent(link_attr) is link:
            link_attr = aq_base(link_attr).__of__(self)
            # Try to access to subitem
            if key in link.keys():
                link_attr = SymlinkSubItem(link_attr).__of__(self)

        # if it is a bound method, re-bind it so that im_self is the alias
        if isinstance(link_attr, types.MethodType):
            return types.MethodType(link_attr.im_func, self, type(self))

        return link_attr

    # Inspired by collective.alias
    def _getOb(self, id, default=_marker):
        link = self._link
        if link is not None:
            obj = link._getOb(id, default)
            if obj is default:
                if default is _marker:
                    raise KeyError(id)
                return default
            return SymlinkSubItem(aq_base(obj).__of__(self)).__of__(self)
        return CMFOrderedBTreeFolderBase._getOb(self, id, default)

    def objectIds(self, spec=None, ordered=True):
        link = self._link
        if link is not None:
            return link.objectIds(spec)
        return CMFOrderedBTreeFolderBase.objectIds(self, spec, ordered)

    def __getitem__(self, key):
        link = self._link
        if link is not None:
            return SymlinkSubItem(link.__getitem__(key)).__of__(self)
        return CMFOrderedBTreeFolderBase.__getitem__(self, key)


class SymlinkView(DefaultView):
    def __call__(self):
        return self.context()


class EditForm(edit.DefaultEditForm):
    @property
    def portal_type(self):
        return self.context._link_portal_type

    @portal_type.setter
    def portal_type(self, value):
        return  # Avoid override during update in plone.dexterity.browser.edit

    @property
    def additionalSchemata(self):
        return []


class SymlinkContextState(ContextState):
    def workflow_state(self):
        return None
