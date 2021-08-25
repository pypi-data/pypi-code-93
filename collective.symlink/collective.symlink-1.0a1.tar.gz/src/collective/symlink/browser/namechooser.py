from plone.app.content.interfaces import INameFromTitle
from plone.app.content.namechooser import NormalizingNameChooser
from zope.component import queryAdapter


class NormalizingNameChooserSymlink(NormalizingNameChooser):
    def chooseName(self, name, object):
        adapter = queryAdapter(object, INameFromTitle)
        if adapter:
            name = adapter.title
        return super(NormalizingNameChooserSymlink, self).chooseName(name, object)
