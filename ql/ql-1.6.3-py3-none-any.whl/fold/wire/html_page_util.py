from pathlib import Path
from bs4 import BeautifulSoup, Tag
from collections.abc import Sequence
from .html_elem_util import MetaTag
from .transforms import HtmlBlock

class HtmlPage:
    def __init__(self, content, depth_from_root, head_params={}):
        self.preamble = "<!doctype html>\n"
        self.content = content
        self.depth = depth_from_root # this is duplicated in BaseIndexPage, oops...
        self.head = self.make_head(**head_params)

    def as_str(self):
        soup = BeautifulSoup(features="html5lib")
        html = Tag(soup, name="html", attrs={"lang": "en"})
        html.append(self.head)
        body = Tag(name="body")
        c_tags = self.content if isinstance(self.content, Sequence) else [self.content]
        for c in c_tags:
            body.append(c)
        html.append(body)
        return self.preamble + str(html)#.prettify()

    @property
    def _default_css_param(self):
        return ["styles"]

    def make_head(self, css=None, desc=None, og_img=None, tw_card=True):
        head = Tag(name="head")
        ct_a = {"http-equiv": "Content-Type", "content": "text/html; charset=utf-8"}
        head.append(MetaTag(ct_a))
        head.append(MetaTag({"charset": "UTF-8"}))
        vp_a = {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        head.append(MetaTag(vp_a))
        if desc:
            head.append(MetaTag({"description": desc}))
        if og_img:
            head.append(MetaTag({"og:image": og_img}))
        if tw_card:
            tw_card_attrs = {"name": "twitter:card", "content": "summary"}
            head.append(MetaTag(tw_card_attrs))
        if css is None:
            css = self._default_css_param
        for s in css:
            # all stylesheets live in the css directory under the site root
            css_href = str(Path(*[".."] * self.depth) / "css" / f"{s}.css")
            css_attrs = {"rel": "stylesheet", "href": css_href}
            style = Tag(name="link", attrs=css_attrs, can_be_empty_element=True)
            head.append(style)
        return head

class HtmlDoc(HtmlPage):
    def __init__(self, doc, depth_from_root, qa_pair=False, nested_qa_summary=False):
        self.preamble = "<!doctype html>\n"
        self.doc = doc
        self.depth = depth_from_root
        self.qa_pair = qa_pair
        self.nested_qa_summary = nested_qa_summary
        self.head = self.make_head()

    def as_str(self):
        soup = BeautifulSoup(features="html5lib")
        html = Tag(soup, name="html")
        html.append(self.head)
        body = Tag(name="body")
        article = self.process_article()
        body.append(article)
        html.append(body)
        return self.preamble + str(html)#.prettify()

    def process_article(self):
        article = Tag(name="article")
        unassigned_lists = self.doc.lists.copy()
        for b in self.doc.blocks:
            assignable_lists = []
            for l in unassigned_lists:
                first_list_line = l.all_nodes[0].line_no
                last_block_line = b.end_line
                if first_list_line < last_block_line:
                    # the list is in this block
                    assignable_lists.append(l)
                # do stuff with the assignable lists in this block
            block_html = HtmlBlock(
                b, assignable_lists, self.qa_pair, self.nested_qa_summary
            ).as_soup()
            article.append(block_html)
            for l in assignable_lists:
                unassigned_lists.pop(0) # pop only after iterating over
        return article
