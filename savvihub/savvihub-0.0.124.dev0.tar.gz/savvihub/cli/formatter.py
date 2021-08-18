class TreeFormatter:
    def __init__(self, text=None):
        self.children = []
        self.text = text
        self.root = self.text is None

    def add_child(self, *children):
        for child in children:
            if isinstance(child, str):
                self.children.append(TreeFormatter(child))
            else:
                self.children.append(child)

    def format(self, to_str=True):
        lines = [] if self.root else [self.text]
        if self.root:
            for child in self.children:
                lines.extend(child.format(False))
        else:
            for child in self.children:
                for line in child.format(False):
                    lines.append('  ' + line)

        if to_str:
            return '\n'.join(lines)

        return lines
