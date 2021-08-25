from bs4 import Tag
from .html_util import CustomHtmlTag

__all__ = ["NavLinkList", "UlLinkList", "MetaTag"]

###### Utility classes for specific tags

class NavLinkList(CustomHtmlTag):
    def __init__(self, titles, links, nav_params={}, ul_params={}, link_params={}):
        super().__init__(name="nav", **nav_params)
        ul = UlLinkList(titles, links, ul_params=ul_params, link_params=link_params)
        self.append(ul)

class UlLinkList(CustomHtmlTag):
    def __init__(self, titles, links, ul_params={}, link_params={}):
        self.titles = titles
        self.links = links
        super().__init__(name="ul", **ul_params)
        li_tags = []
        if "attrs" in link_params:
            extra_attrs = link_params.pop("attrs")
        else:
            extra_attrs = {}
        for t,l in zip(self.titles, self.links):
            li_tag = Tag(name="li")
            # note that here the href link is coerced to string automatically
            link_attrs = {"href": l, **extra_attrs}
            a_tag = Tag(name="a", attrs=link_attrs, **link_params)
            a_tag.append(t) # the contents here can be string or a nested tag passed in
            li_tag.append(a_tag)
            self.append(li_tag)

class MetaTag(Tag):
    def __init__(self, attrs):
        super().__init__(name="meta", attrs=attrs, can_be_empty_element=True)

class NavHeader(CustomHtmlTag):
    def __init__(self, size=1, breadcrumbs=None, nh_params={}):
        default_nh_params = {"id": "nav_header"}
        #nh_params = {**nh_params, **self.nav_header_attrs} # merge with args if provided
        super().__init__(name=f"h{size}", **nh_params)
        if breadcrumbs:
            # construct it with the sep
            self.append(breadcrumbs)

class BreadCrumb(CustomHtmlTag):
    def __init__(self, text, link=None, tagname="a", link_params={}):
        link_attrs = {"class": "crumb"}
        if link:
            if "attrs" in link_params:
                extra_attrs = link_params.pop("attrs")
                link_attrs = {**link_attrs, **extra_attrs}
            link_attrs.update({"href": link})
        super().__init__(name=tagname, attrs=link_attrs, **link_params)
        self.append(text)
