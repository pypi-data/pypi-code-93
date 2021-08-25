from plone.app.content.interfaces import INameFromTitle
from zope.interface import implementer
from zope.component import adapter
from collective.symlink.content.symlink import ISymlink


@implementer(INameFromTitle)
@adapter(ISymlink)
class NameFromSymLink(object):
    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return self.context.symbolic_link.to_object.title
