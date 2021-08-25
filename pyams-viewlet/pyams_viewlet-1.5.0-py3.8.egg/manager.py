#
# Copyright (c) 2008-2015 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_viewlet.manager module

This module defines the viewlet manager, as weel as a "viewletmanager_config" decorator
which can be used instead of ZCML to declare a viewlets manager.
"""

import logging

import venusian
from pyramid.exceptions import ConfigurationError
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.interfaces import IRequest, IView
from pyramid.threadlocal import get_current_registry
from zope.contentprovider.interfaces import BeforeUpdateEvent
from zope.interface import Interface, classImplements, implementer
from zope.interface.interfaces import ComponentLookupError
from zope.location.interfaces import ILocation
from zope.schema.fieldproperty import FieldProperty

from pyams_template.template import get_view_template
from pyams_utils.request import check_request
from pyams_viewlet.interfaces import IViewlet, IViewletManager


__docformat__ = 'restructuredtext'

from pyams_viewlet.viewlet import register_viewlet


LOGGER = logging.getLogger('PyAMS (viewlet)')


@implementer(IViewletManager)
class ViewletManager:
    """The Viewlet Manager base

    A generic manager class which can be instantiated.

    A viewlet manager can be used as mapping and can get to a given viewlet by it's name.
    """

    permission = None
    template = None

    viewlets = None

    render_empty = FieldProperty(IViewletManager['render_empty'])

    def __init__(self, context, request, view, manager=None):
        self.context = context
        self.request = request
        self.view = self.__parent__ = view
        self.manager = manager
        self.__updated = False

    def __getitem__(self, name):
        """See zope.interface.common.mapping.IReadMapping"""
        # Find the viewlet
        registry = get_current_registry()
        viewlet = registry.queryMultiAdapter((self.context, self.request, self.__parent__, self),
                                             IViewlet, name=name)

        # If the viewlet was not found, then raise a lookup error
        if viewlet is None:
            raise ComponentLookupError('No provider with name `%s` found.' % name)

        # If the viewlet cannot be accessed, then raise an
        # unauthorized error
        if viewlet.permission and not self.request.has_permission(viewlet.permission,
                                                                  context=self.context):
            raise HTTPUnauthorized('You are not authorized to access the '
                                   'provider called `%s`.' % name)

        # Return the viewlet.
        return viewlet

    def get(self, name, default=None):
        """See zope.interface.common.mapping.IReadMapping"""
        try:
            return self[name]
        except (ComponentLookupError, HTTPUnauthorized):
            return default

    def __contains__(self, name):
        """See zope.interface.common.mapping.IReadMapping"""
        return bool(self.get(name, False))

    def filter(self, viewlets):
        """Filter out all content providers

        :param viewlets: list of viewlets, each element being a tuple of (name, viewlet) form

        Default implementation is filtering out viewlets for which a permission which is not
        granted to the current principal is defined.
        """
        request = self.request

        def _filter(viewlet):
            """Filter viewlet based on permission"""
            _, viewlet = viewlet
            return (not viewlet.permission) or request.has_permission(viewlet.permission,
                                                                      context=self.context)

        return filter(_filter, viewlets)

    def sort(self, viewlets):  # pylint: disable=no-self-use
        """Sort the viewlets.

        :param viewlets: list of viewlets, each element being a tuple of (name, viewlet) form

        Default implementation is sorting viewlets by name
        """
        return sorted(viewlets, key=lambda x: x[0])

    def _get_viewlets(self):
        """Find all content providers for the region"""
        registry = self.request.registry
        viewlets = registry.getAdapters((self.context, self.request, self.__parent__, self),
                                        IViewlet)
        viewlets = self.filter(viewlets)
        viewlets = self.sort(viewlets)
        return viewlets

    def _update_viewlets(self):
        """Calls update on all viewlets and fires events"""
        registry = self.request.registry
        for viewlet in self.viewlets:
            registry.notify(BeforeUpdateEvent(viewlet, self.request))
            viewlet.update()

    def update(self):
        """See :py:class:`zope.contentprovider.interfaces.IContentProvider`"""
        registry = self.request.registry
        registry.notify(BeforeUpdateEvent(self, self.request))
        # check permission
        if self.permission and not self.request.has_permission(self.permission,
                                                               context=self.context):
            return
        # get the viewlets from now on
        self.viewlets = []
        append = self.viewlets.append
        for name, viewlet in self._get_viewlets():
            if ILocation.providedBy(viewlet):
                viewlet.__name__ = name
            append(viewlet)
        # and update them...
        self._update_viewlets()
        self.__updated = True

    def render(self):
        """See :py:class:`zope.contentprovider.interfaces.IContentProvider`"""
        # Check for previous update
        if not self.__updated:
            return ''
        # Check for empty viewlet manager
        if (not self.viewlets) and (not self.render_empty):
            return ''
        # Now render the view
        if self.template:
            return self.template(viewlets=self.viewlets)  # pylint: disable=not-callable
        return '\n'.join([viewlet.render() for viewlet in self.viewlets])

    def reset(self):
        """Reset viewlet manager status"""
        self.viewlets = None
        self.__updated = False


def ViewletManagerFactory(name, interface, bases=(), cdict=None):  # pylint: disable=invalid-name
    """Viewlet manager factory"""

    attr_dict = {'__name__': name}
    attr_dict.update(cdict or {})

    if ViewletManager not in bases:
        # Make sure that we do not get a default viewlet manager mixin, if the
        # provided base is already a full viewlet manager implementation.
        # pylint: disable=no-value-for-parameter
        if not (len(bases) == 1 and IViewletManager.implementedBy(bases[0])):
            bases = bases + (ViewletManager,)

    viewlet_manager_class = type('<ViewletManager providing %s>' % interface.getName(),
                                 bases, attr_dict)
    classImplements(viewlet_manager_class, interface)
    return viewlet_manager_class


def get_weight(item):
    """Get sort weight of a given viewlet"""
    _, viewlet = item
    try:
        return int(viewlet.weight)
    except (TypeError, AttributeError):
        return 0


def get_label(item, request=None):
    """Get sort label of a given viewlet"""
    _, viewlet = item
    try:
        label = getattr(viewlet, 'label', None)
        if not label:
            return '--'
        if request is None:
            request = check_request()
        return request.localizer.translate(label)
    except AttributeError:
        return '--'


def get_weight_and_label(item, request=None):
    """Get sort weight and label of a given viewlet"""
    return get_weight(item), get_label(item, request)


class WeightOrderedViewletManager(ViewletManager):
    """Weight ordered viewlet managers.

    Viewlets with the same weight are sorted by label
    """

    def sort(self, viewlets):
        return sorted(viewlets, key=lambda x: get_weight_and_label(x, request=self.request))


class ConditionalViewletManager(WeightOrderedViewletManager):
    """Conditional weight ordered viewlet managers"""

    def filter(self, viewlets):
        """Sort out all viewlets which are explicitly not available

        Viewlets shoud have a boolean "available" attribute to specify if they are available
        or not.
        """

        def is_available(viewlet):
            _, viewlet = viewlet
            try:
                return ((not viewlet.permission) or
                        viewlet.request.has_permission(viewlet.permission,
                                                       context=viewlet.context)) and \
                       viewlet.available
            except AttributeError:
                return True

        return filter(is_available, viewlets)


class TemplateBasedViewletManager:
    """Template based viewlet manager mixin class"""

    template = get_view_template()


class viewletmanager_config:  # pylint: disable=invalid-name
    """Class or interface decorator used to declare a viewlet manager

    You can provide same arguments as in 'viewletManager' ZCML directive:
    :param name: name of the viewlet; may be unique for a given viewlet manager
    :param view: the view class or interface for which viewlet is displayed
    :param for_: the context class or interface for which viewlet is displayed
    :param permission: name of a permission required to display the viewlet
    :param layer: request interface required to display the viewlet
    :param class_: the class handling the viewlet manager; if the decorator is applied
        on an interface and if this argument is not provided, the viewlet manager
        will be handled by a default ViewletManager class
    :param provides: an interface the viewlet manager provides; if the decorator is
        applied on an Interface, this will be the decorated interface; if the
        decorated is applied on a class and if this argument is not specified,
        the manager will provide IViewletManager interface.
    :param manager: if a manager interface or class is provided, the viewlet manager
        will be also registered as a viewlet for the given manager
    :param weight: if provided, this will be the weight of the viewlet
    """

    venusian = venusian  # for testing injection

    def __init__(self, **settings):
        if not settings.get('name'):
            raise ConfigurationError("You must provide a name for a ViewletManager")
        if 'for_' in settings:
            if settings.get('context') is None:
                settings['context'] = settings['for_']
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()

        def callback(context, name, obj):  # pylint: disable=unused-argument
            cdict = {'__name__': settings.get('name')}
            if 'permission' in settings:
                cdict['permission'] = settings.get('permission')

            if issubclass(obj, Interface):
                class_ = settings.get('class_', ViewletManager)
                provides = obj
            else:
                class_ = obj
                provides = settings.get('provides', IViewletManager)
            new_class = ViewletManagerFactory(settings.get('name'), provides, (class_,), cdict)

            LOGGER.debug("Registering viewlet manager {0} ({1})".format(settings.get('name'),
                                                                        str(new_class)))
            registry = settings.get('registry')
            if registry is None:
                config = context.config.with_package(info.module)  # pylint: disable=no-member
                registry = config.registry
            registry.registerAdapter(new_class,
                                     (settings.get('context', Interface),
                                      settings.get('layer', IRequest),
                                      settings.get('view', IView)),
                                     provides, settings.get('name'))
            if settings.get('manager') is not None:
                if settings.get('weight') is not None:
                    new_class.weight = settings.get('weight')
                register_viewlet(registry, new_class, settings, IViewlet)

        info = self.venusian.attach(wrapped, callback, category='pyams_viewlet')

        if info.scope == 'class':  # pylint: disable=no-member
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings.get('attr') is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo  # pylint: disable=no-member
        return wrapped
