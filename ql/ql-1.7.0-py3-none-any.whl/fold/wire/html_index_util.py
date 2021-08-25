from bs4 import Tag
from pathlib import Path
from .html_page_util import HtmlPage
from .html_util import Attrs, PartialAttrs
from .html_elem_util import NavLinkList, NavHeader, BreadCrumb
from collections.abc import Sequence

__all__ = ["IndexNav", "IndexUl", "EmittedIndex", "IntermedDirIndex", "WireIndex"]

class BaseIndexPage(HtmlPage):
    def __init__(self, nav, head_params={}):
        self._nav_tag = nav
        super().__init__(self._index_content, self.rel_depth, head_params)

    @property
    def _default_css_param(self):
        "Overrides HtmlPage property method of the same name, setting head styles"
        return ["styles", "index"]

    @property
    def rel_depth(self):
        return len(self.rel_dir.parts)

    @property
    def head_params(self):
        return self._head_params

    @head_params.setter
    def head_params(self, params):
        self._head_params = params

    @property
    def _index_content(self):
        nh_sec = Tag(name="section", attrs={"id": "nh"})
        up_a = Tag(name="a", attrs={"href": "..", "id": "up_arr"})
        nh_sec.append(up_a)
        if self.nav_header:
            nh_sec.append(self.nav_header)
        return [nh_sec, self._nav_tag]

    @property
    def nav_header(self):
        if hasattr(self, "_nh"):
            return self._nh
        else:
            return None

    @nav_header.setter
    def nav_header(self, h):
        self._nh = h

    @property
    def nav_header_attrs(self):
        if hasattr(self, "_nh_attrs"):
            return self._nh_attrs
        else:
            return dict()

    @nav_header_attrs.setter
    def nav_header_attrs(self, attrs):
        self._nh_attrs = attrs

    @property
    def breadcrumb_attrs(self):
        if hasattr(self, "_bc_attrs"):
            return self._bc_attrs
        else:
            return dict()

    @breadcrumb_attrs.setter
    def breadcrumb_attrs(self, attrs):
        self._bc_attrs = attrs


class IndexNav(PartialAttrs):
    "Partially set Attrs wrapper class for index page nav elements"
    def __init__(self, attrs):
        self.default_attrs = {"class": "index"}
        super().__init__(attrs)

class IndexUl(PartialAttrs):
    "Gratuitous wrapper class (currently doing nothing but may in future)"
    def __init__(self, attrs):
        #self.default_attrs = {}
        super().__init__(attrs)

class BaseWireIndexPage(BaseIndexPage):
    "Wrapper class to set the nav header text for breadcrumbs"
    def __init__(self, *args):
        self.nav_header_attrs = Attrs({"id": "nav_header", "depth": f"{self.rel_depth}"})
        self.create_header()
        super().__init__(*args)

    def create_header(self):
        if self.nav_header is not None:
            return # forbid overwriting nav header by repeated call to this function
        nh_size = 3
        default_bc_attrs = {"crumb_sep": "⠶", "id": "crumbs"}
        bc_attrs = {**default_bc_attrs, **self.breadcrumb_attrs}
        crumb_sep = bc_attrs.pop("crumb_sep")
        bc = Tag(name="ul", attrs=bc_attrs)
        breadcrumbs = []
        for i, x in enumerate(self.rel_dir.parts):
            if i == len(self.rel_dir.parts) - 1:
                # final tuple: omit link off last crumb (as it is to current page)
                bc_tuple = (x,)
            else:
                bc_tuple = (x, Path(*[".."] * (len(self.rel_dir.parts) - i)) / x)
            breadcrumbs.append(bc_tuple)
        for i,c in enumerate(breadcrumbs):
            t = Tag(name="li")
            if i > 0:
                t.attrs.update({"separator": crumb_sep})
            t.append(BreadCrumb(*c))
            bc.append(t)
        self.nav_header = NavHeader(nh_size, bc, self.nav_header_attrs)

class EmittedIndex(BaseWireIndexPage):
    def __init__(self, files, rel_dir, head_params={}):
        self.rel_dir = Path("wire") / rel_dir
        self.head_params = head_params
        nav_params = IndexNav({"id": "file_index"})
        ul_params = IndexUl({"id": "files"})
        filenames = list(map(self.process_filename, files))
        nav = NavLinkList(filenames, files, nav_params, ul_params)
        super().__init__(nav)

    @staticmethod
    def process_filename(f):
        fstr = str(f)
        if any(fstr.startswith(f"{d}") for d in range(10)):
            pass
        return fstr.replace("_", " ").replace("-", " ")

class IntermedDirIndex(BaseWireIndexPage):
    def __init__(self, subdirs, rel_dir, head_params={}):
        self.rel_dir = Path("wire") / rel_dir
        self.head_params = head_params
        nav_params = IndexNav({"id": "mid_index"})
        ul_params = IndexUl({"id": "index", "class": f"lvl_{self.rel_depth}"})
        dirnames = list(map(self.process_dirname, subdirs))
        nav = NavLinkList(dirnames, subdirs, nav_params, ul_params)
        #self.nav_header_attrs = Attrs({"class": "breadcrumbs bc_intermed"})
        super().__init__(nav)
        #self.nav_header.string = " ⠶ dir_beep_boop" # breadcrumbs go here
        #self.nav_header.append(" ...beep boop?")

    @staticmethod
    def process_dirname(d):
        return str(d)

class WireIndex(BaseWireIndexPage):
    def __init__(self, subdirs, rel_dir, head_params={}):
        self.rel_dir = Path("wire") / rel_dir
        self.head_params = head_params
        nav_params = IndexNav({"id": "wire_index"})
        ul_params = Attrs({"id": "wires"})
        link_params = Attrs({"class": "wirelink"})
        dirnames = list(map(self.process_dirname, subdirs))
        nav = NavLinkList(dirnames, subdirs, nav_params, ul_params, link_params)
        super().__init__(nav)
        #self.nav_header.append(" ...beep boop?")

    @staticmethod
    def process_dirname(d):
        "Prefix the year shortname with 20 to indicate the full year"
        return f"20{d}"
