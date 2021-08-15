# ButtonWidget: <button> tag
# LabelWidget: <p> tag
import bs4 
try: from _utils import *
except ImportError: from ._utils import *

Widget2Tag = {"Label":"p", 
              "Button":"button",
              "Video":"video",
              "Image":"img",}
LEFT = "left"
CENTER = "center"
RIGHT = "right"

class BImage:
    '''Class to represent the image tag'''
    def __init__(self, source, parent=None, **attrs):
        '''source url of the image is needed'''
        self.cage = None
        self.type = "Image"
        self._secret = rand_str()
        self.source = self.loadStatic(source)
        self.tag = Widget2Tag.get(self.type, "span")
        for attr,value in attrs.items():
            setattr(self, attr, value) # each attrinute of tag is attribute of the object now.
        self.attrs = attrs # dictionary of attributes.
        self.parent = parent
        self.is_packed = False
        self.align = LEFT
        if parent is not None: self.parent.children.append(self) # add current widget as a child for the parent.
        self._bindings = []

    def loadStatic(self, path):
        import os, shutil, pathlib
        filename = pathlib.Path(path).name
        os.makedirs("static", exist_ok=True)
        filepath = os.path.join("./static", filename)
        shutil.copyfile(path, filepath)
        
        return filepath # filename

    def encage(self, cage):
        '''Link a reference to the BoaCage instance for the widget'''
        self.cage = cage

    def setStyle(self, **attrs):
        jscode = f'''element = document.getElementById("{self._secret}");\n'''
        for attr, value in attrs.items():
            jscode += f'''element.setAttribute("style", "{attr.replace('_','-')}: {value};");\n'''
        if self.cage: self.cage.execJS(jscode)

    def _compile(self, src, **attrs):
        attr_str = " ".join([f"{attr}='{value}'" for attr,value in self.attrs.items()]) 
        # return f'''\n<{self.tag} src='''+'''{{'''+f''' url_for('static', filename='{src}') '''+'''}}'''+f''' {attr_str}>\n'''
        return f'''\n<{self.tag} src="{self.source}" {attr_str}>\n'''

    def __str__(self):
        '''get the html of current widget including all children'''
        attrs = self.attrs
        attrs["id"] = self._secret
        # attrs["src"] = self.source
        return self._compile(src=self.source, **attrs)

    def pack(self, **kwargs):
        self.align = kwargs.get("align", LEFT)
        self.is_packed = True

    def pack_forget(self, **kwargs):
        self.is_packed = False
        
    def bind(self, event, callback):
        callback_name = f"{event}_{self._secret}"
        js_callback = "function () {"+f"window.{callback_name}();"+"}"
        binding = f'''document.getElementById("{self._secret}").addEventListener('{event}', {js_callback} )
console.log('{callback_name} bound to {event} event of id={self._secret}');'''
        self._bindings.append({"name" : callback_name,
                               "callback": callback,
                               "jscode" : binding})

    def _get_bindings(self):
        return self._bindings


class BAudio:
    def __init__(self,):
        pass


class Widget:
    def __init__(self, parent=None, text="", **attrs):
        self._secret = rand_str()
        self.innerText = "" # innerText attribute of Node/Widget
        self.innerHTML = "" # innerHtml attribute of Node/Widget (including html of child)
        self.type = ""
        self.text = text
        self.cage = None
        self.tag = Widget2Tag.get(self.type, "span")
        self.soup = bs4.BeautifulSoup(self.innerHTML, features="html.parser")
        for attr,value in attrs.items():
            setattr(self, attr, value) # each attrinute of tag is attribute of the object now.
        self.attrs = attrs # dictionary of attributes.
        self.parent = parent
        self.children = []
        self.is_packed = False
        self.align = LEFT
        if parent is not None:
            self.parent.children.append(self) # add current widget as a child for the parent.
        self._bindings = []

    def encage(self, cage):
        '''
        Link a reference to the BoaCage instance for the widget and all of it's children
        '''
        self.cage = cage
        for child in self.children:
            child.encage(cage)

    def setStyle(self, **attrs):
        jscode = f'''element = document.getElementById("{self._secret}");\n'''
        for attr, value in attrs.items():
            jscode += f'''element.setAttribute("style", "{attr.replace('_','-')}: {value};");\n'''
        if self.cage: self.cage.execJS(jscode)

    def _compile(self, **attrs):
        attr_str = " ".join([f"{attr}={value}" for attr,value in self.attrs.items()]) 
        return f"<{self.tag} {attr_str}>{self.text}\n{self.innerHTML}</{self.tag}>"

    def __str__(self):
        '''get the html of current widget including all children'''
        children_html = []
        for child in self.children:
            if child.is_packed: 
                children_html.append(f'''<div style="text-align: {child.align}">{str(child)}</div>''')
        self.innerHTML = "\n".join(children_html)
        self.soup = bs4.BeautifulSoup(self.innerHTML, features="html.parser")
        self.innerHTML = str(self.soup)
        self.innerText = self.soup.text
        attrs = self.attrs
        attrs["id"] = self._secret

        return self._compile(**attrs)

    def pack(self, **kwargs):
        self.align = kwargs.get("align", LEFT)
        self.is_packed = True

    def pack_forget(self, **kwargs):
        self.is_packed = False

    def setHTML(self, html):
        self.innerHTML = html
        self.soup = bs4.BeautifulSoup(self.innerHTML, features="html.parser")
        self.innerHTML = str(self.soup)
        self.innerText = self.soup.text

    def setText(self, text):
        '''Need to decide whether to set innerText or text'''
        self.innerHTML = text
        self.innerText = text
        self.soup = bs4.BeautifulSoup(self.innerHTML, features="html.parser")
        self.innerHTML = str(self.soup)

    def bind(self, event, callback):
        # print(event, callback)
        callback_name = f"{event}_{self._secret}"
        # setattr(self, callback_name, callback)
        js_callback = "function () {"+f"window.{callback_name}();"+"}"
        binding = f'''document.getElementById("{self._secret}").addEventListener('{event}', {js_callback} )
console.log('{callback_name} bound to {event} event of id={self._secret}');'''
        self._bindings.append({"name" : callback_name,
                               "callback": callback,# getattr(self, callback_name),
                               "jscode" : binding})

    def _get_bindings(self):
        rec_bindings = []
        for child in self.children:
            rec_bindings += child._get_bindings() 
        rec_bindings += self._bindings
        
        return rec_bindings


class LabelWidget(Widget):
    def __init__(self, parent=None, **attrs):
        super(LabelWidget, self).__init__(parent, **attrs)
        self.type = "Label"
        self.tag = Widget2Tag.get(self.type, "span")


class ButtonWidget(Widget):
    def __init__(self, parent=None, **attrs):
        super(ButtonWidget, self).__init__(parent, **attrs)
        self.type = "Button"
        self.tag = Widget2Tag.get(self.type, "span")

    def _compile(self, **attrs):
        attr_str = " ".join([f"{attr}={value}" for attr,value in self.attrs.items()]) 
        return f"<{self.tag} {attr_str}>{self.text}</{self.tag}>\n{self.innerHTML}"        


if __name__ == "__main__":
    LabelWidget(text="This is a label")
    print(str(LabelWidget))