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

"""PyAMS_viewlet.viewlet module

This module provides base content providers and viewlets classes, as well as a decorators
which can be used instead of ZCML declarations to register content providers and viewlets.
"""

import logging

import venusian
from pyramid.exceptions import ConfigurationError
from pyramid.interfaces import IRequest, IView
from zope.component import ComponentLookupError
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import Interface, implementer

from pyams_template.template import get_view_template
from pyams_viewlet.interfaces import IViewlet, IViewletManager

__docformat__ = 'restructuredtext'


LOGGER = logging.getLogger('PyAMS (viewlet)')


@implementer(IContentProvider)
class EmptyContentProvider:
    """Empty content provider base class"""

    permission = None

    def __init__(self, context, request, view=None):
        self.context = context
        self.request = request
        self.view = self.__parent__ = view

    def __call__(self, template_name=''):
        if self.permission and not self.request.has_permission(self.permission,
                                                               context=self.context):
            return ''
        self.update()
        return self.render(template_name)

    def update(self):
        """See `IContentProvider` interface"""

    def render(self, template_name=''):  # pylint: disable=no-self-use
        """See `IContentProvider` interface"""
        return ''


class BaseContentProvider(EmptyContentProvider):
    """Base template based content provider"""

    resources = ()

    def update(self):
        for resource in self.resources:
            resource.need()

    def render(self, template_name=''):
        template = get_view_template(name=template_name)
        try:
            return template(self)
        except ComponentLookupError:
            template = get_view_template()
            return template(self)


class ViewContentProvider(BaseContentProvider):
    """Template based content provider"""


class contentprovider_config:  # pylint: disable=invalid-name
    """Class decorator used to declare a content provider

    You can provide same arguments as in 'viewlet' ZCML directive:
    @name = name of the viewlet; may be unique for a given viewlet manager
    @view = the view class or interface for which viewlet is displayed
    @for = the context class or interface for which viewlet is displayed
    @permission = name of a permission required to display the viewlet
    @layer = request interface required to display the viewlet
    """

    venusian = venusian  # for testing injection

    def __init__(self, **settings):
        if not settings.get('name'):
            raise ConfigurationError("You must provide a name for a content provider")
        if 'for_' in settings:
            if settings.get('context') is None:
                settings['context'] = settings['for_']
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()

        def callback(context, name, obj):  # pylint: disable=unused-argument
            cdict = {
                '__name__': settings.get('name'),
                '__module__': obj.__module__
            }
            if 'permission' in settings:
                settings['permission'] = settings.get('permission')

            bases = (obj,)
            if not IContentProvider.implementedBy(obj):  # pylint: disable=no-value-for-parameter
                bases = bases + (ViewContentProvider,)
            new_class = type('<ViewContentProvider %s>' % settings.get('name'), bases, cdict)

            LOGGER.debug("Registering content provider {0} ({1})".format(settings.get('name'),
                                                                         str(new_class)))
            registry = settings.get('registry')
            if registry is None:
                config = context.config.with_package(info.module)  # pylint: disable=no-member
                registry = config.registry
            registry.registerAdapter(new_class,
                                     (settings.get('context', Interface),
                                      settings.get('layer', IRequest),
                                      settings.get('view', IView)),
                                     IContentProvider, settings.get('name'))

        info = self.venusian.attach(wrapped, callback, category='pyams_viewlet')

        if info.scope == 'class':  # pylint: disable=no-member
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings.get('attr') is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo  # pylint: disable=no-member
        return wrapped


@implementer(IViewlet)
class EmptyViewlet:
    """Empty viewlet base class"""

    permission = None

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = self.__parent__ = view
        self.manager = manager

    def update(self):
        """See `IContentProvider` interface"""

    def render(self):  # pylint: disable=no-self-use
        """See `IContentProvider` interface"""
        return ''


class Viewlet(EmptyViewlet):
    """Viewlet adapter class used in meta directive as a mixin class."""

    render = get_view_template()


def register_viewlet(registry, klass, settings, provides=IViewlet):
    """Common viewlet registration"""
    registry.registerAdapter(klass,
                             (settings.get('context', Interface),
                              settings.get('layer', IRequest),
                              settings.get('view', IView),
                              settings.get('manager', IViewletManager)),
                             provides, settings.get('name'))


class viewlet_config:  # pylint: disable=invalid-name
    """Class decorator used to declare a viewlet

    You can provide same arguments as in 'viewlet' ZCML directive:
    @name = name of the viewlet; may be unique for a given viewlet manager
    @manager = manager class or interface holding the viewlet
    @view = the view class or interface for which viewlet is displayed
    @for = the context class or interface for which viewlet is displayed
    @permission = name of a permission required to display the viewlet
    @layer = request interface required to display the viewlet
    @weight = weight of the viewlet when using a weight ordered viewlet manager
    """

    venusian = venusian  # for testing injection

    def __init__(self, **settings):
        if not settings.get('name'):
            raise ConfigurationError("You must provide a name for a viewlet")
        if 'for_' in settings:
            if settings.get('context') is None:
                settings['context'] = settings['for_']
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()

        def callback(context, name, obj):  # pylint: disable=unused-argument
            cdict = {
                '__name__': settings.get('name'),
                '__module__': obj.__module__
            }
            if 'permission' in settings:
                cdict['permission'] = settings.get('permission')
            if 'weight' in settings:
                cdict['weight'] = settings.get('weight')

            bases = (obj,)
            if not IViewlet.implementedBy(obj):  # pylint: disable=no-value-for-parameter
                bases = bases + (Viewlet,)
            new_class = type('<Viewlet %s>' % settings.get('name'), bases, cdict)

            LOGGER.debug("Registering viewlet {0} ({1})".format(settings.get('name'),
                                                                str(new_class)))
            registry = settings.get('registry')
            if registry is None:
                config = context.config.with_package(info.module)  # pylint: disable=no-member
                registry = config.registry
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
