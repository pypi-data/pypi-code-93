import re


class Patterns:
    opening = r'(<text ?((\w+)="([^"]*)" *)*>)'
    closing = r'(<\/text ?((\w+)="([^"]*)" *)*>)'
    attr = r'(\w+)="([^"]*)"'


def parse(string):
    matches = re.findall(Patterns.opening, string) + re.findall(Patterns.closing, string)
    coloring_tree = {}
    for match in matches:
        target, *_ = match
        attrs = re.findall(Patterns.attr, target)
        coloring_tree[target] = dict(attrs)
    return coloring_tree



