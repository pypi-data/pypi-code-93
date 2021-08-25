# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase


class EditLinkViewlet(ViewletBase):
    """ A viewlet which renders the popup """

    index = ViewPageTemplateFile("templates/editlinkviewlet.pt")

    def edit_link(self):
        return "{0}/edit".format(self.context.symbolic_link.to_object.absolute_url())
