# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.common import GlobalSectionsViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api

try:
    from html import escape
except ImportError:
    from cgi import escape


class DSGovSectionsViewlet(GlobalSectionsViewlet):
    index = ViewPageTemplateFile("./sections.pt")

    _opener_markup_template = (
        u'<input id="navitem-{uid}" type="checkbox" class="opener" />'
        u'<label for="navitem-{uid}" role="button" aria-label="{title}"></label>'  # noqa: E 501
    )
    _item_markup_template = (
        u'<li class="side-menu {id}{has_sub_class}">'
        u'<a href="{url}" class="menu-item state-{review_state}"{aria_haspopup}>'
        u'<span class="content">{title}</span>'
        u'</a>{opener}'  # noqa: E 501
        u"{sub}"
        u"</li>"
    )

    _subchildre_item_markup_template = (
        u'<li>'
        u'<a href="javascript: void(0)" class="menu-item">'
        u'<span class="content">{title}</span>'
        u'</a>'  # noqa: E 501
        u"{sub}"
        u"</li>"
    )

    _subtree_markup_wrapper = (
        u'<ul>'
        u'{out}'
        u'</ul>'
    )

    _first_item_markup_template = (
        u'<div class="menu-folder drop-menu">'
        u'<a class="menu-item" href="javascript: void(0)"><span class="content">{title}</span></a>'
        u'<ul>'
        u'<li class="{id}{has_sub_class}">'
        u'<a href="{url}" class="menu-item state-{review_state}"{aria_haspopup}>'
        u'<span class="content">{title}</span>'
        u'</a>{opener}'  # noqa: E 501
        u"{sub}"
        u"</li>"
        u'</ul></div>'
    )

    def render_item(self, item, path):

        sub = self.build_tree(item["path"], first_run=False)

        if sub:
            item.update(
                {
                    "sub": sub,
                    "opener": self._opener_markup_template.format(**item),
                    "aria_haspopup": ' aria-haspopup="true"',
                    "has_sub_class": " has_subtree",
                }
            )
        else:
            item.update(
                {"sub": sub, "opener": "", "aria_haspopup": "", "has_sub_class": "", }
            )
        if "title" in item and item["title"]:
            item["title"] = escape(item["title"])
        if "name" in item and item["name"]:
            item["name"] = escape(item["name"])

        portal = api.portal.get()
        if path == '/' + portal.id and sub:
            return self._first_item_markup_template.format(**item)
        elif path != '/' + portal.id and sub:
            return self._subchildre_item_markup_template.format(**item)

        return self._item_markup_template.format(**item)

    def build_tree(self, path, first_run=True):
        """Non-template based recursive tree building.
        3-4 times faster than template based.
        """
        out = u""
        for item in self.navtree.get(path, []):
            out += self.render_item(item, path)
        if not first_run and out:
            out = self._subtree_markup_wrapper.format(out=out)
        return out

    def render_globalnav(self):
        return self.build_tree(self.navtree_path)
