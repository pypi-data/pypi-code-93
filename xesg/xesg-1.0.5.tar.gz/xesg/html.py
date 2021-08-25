class Html(object):
    def __init__(self):
        self.code = ""

    def doctype(self):
        self.code = self.code + "<!doctype html>"

    def start(self, label, **attribute):
        self.code = self.code + "<" + label
        for k, v in attribute.items():
            if k == "class__":
                k = "class"
            self.code = self.code + " " + k + "=\"" + v + "\""
        self.code = self.code + ">"

    def end(self, label):
        self.code = self.code + "</" + label + ">"

    def one(self, label, **attribute):
        self.code = self.code + "<" + label
        for k, v in attribute.items():
            if k == "class__":
                k = "class"
            self.code = self.code + " " + k + "=\"" + v + "\""
        self.code = self.code + ">"

    def write(self, text):
        self.code = self.code + text

    def note(self, text):
        self.code = self.code + "<!--" + text + "-->"

    def show(self, fileName):
        with open(fileName, "w", encoding="utf-8") as f:
            f.write(self.code)
#可以编辑html