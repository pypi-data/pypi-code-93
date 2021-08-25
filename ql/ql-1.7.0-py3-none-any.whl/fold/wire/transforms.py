from bs4 import Tag

__all__ = ["node_html_tag", "HtmlBlock", "HtmlDoc"]

def node_html_tag(node, line_no=None):
    "Should this be in scan⠶lever"
    pre_name = node.prefix._name_
    pre = node.prefix.str if node.prefix else ""
    con = node.contents if node.contents else ""
    suf = node.suffix.str if node.suffix else ""
    inner = con.strip()
    if suf != "":
        suf_span = Tag(name="span")
        suf_span.append(suf)
    else:
        suf_span = ""
    if pre_name == "SectBreak":
        t = Tag(name="hr")
        # never has inner content
    else:
        # anything with inner content goes here
        if pre_name.startswith("Header"):
            # headers can't go in inline span elements
            html_tag_name = pre_name.replace("Header", "h")
            t = Tag(name=html_tag_name)
        else:
            t = Tag(name="span")
        t.append(inner)
        t.append(suf_span)
    # Then regardless of whether/not the node has inner content:
    cls_list = ["Node", f"pre_{pre_name}"]
    if node.suffix:
        cls_list.append(f"suf_{node.suffix._name_}")
    attrs = {"class": " ".join(cls_list), "prefix": pre, "suffix": suf}
    t.attrs.update(attrs)
    if line_no is not None:
        t.attrs.update({"id": f"L{line_no}"})
    return t

class HtmlBlock:
    def __init__(self, block, lists, qa_pair=False, nested_qa_summary=False):
        self.number = block.number
        self.start_line = block.start_line
        self.end_line = block.end_line
        self.nodes = block.nodes
        self.lists = lists
        self.qa_pair = qa_pair
        self.nested_qa_summary = nested_qa_summary

    def as_soup(self):
        line_range_dict = {"from": f"{self.start_line}", "to": f"{self.end_line}"}
        attrs = {"class": "NodeBlock", "id": f"nb{self.number}", **line_range_dict}
        block_div = Tag(name="div", attrs=attrs)
        # TODO do this properly after rewriting list parsing so end lines are accurate
        #list_starts = [l.all_nodes[0].start_line for l in self.lists]
        #list_ends = [l.all_nodes[-1].end_line for l in self.lists]
        if self.qa_pair:
            self.qa_idx_pairs = {}
        for i, n in enumerate(self.nodes):
            if n.prefix is None:
                raise ValueError(f"Missing prefix for '{n.content}' (tag won't parse)")
            node_line_no = self.start_line + i
            html_node = node_html_tag(n, node_line_no)
            if self.qa_pair:
                if hasattr(n, "paired_to"):
                    paired_block_no, paired_line_no = n.paired_to
                    html_node.attrs.update({"paired_id": f"L{paired_line_no}"})
                    if self.nested_qa_summary:
                        if paired_line_no > node_line_no:
                            # Build the details tag, summary first, but don't finish it
                            html_node.name = "summary"
                            accumulated_det = Tag(name="details")
                            accumulated_det.append(html_node)
                            continue
                        else:
                            # The details can stay as a span tag and finish the summary
                            accumulated_det.append(html_node)
                            # Overwrite html_node variable to append entire summary tag
                            html_node = accumulated_det
            block_div.append(html_node)
        return block_div
