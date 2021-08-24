import json

def test():
    print("Package is Linked & Working")

#Root Level
def doc(content, cfw=None):
    print("Parsing Doc: " + json.dumps(content))
    txt=""
    for c in content:
        txt += parse(c)
        pass
    return txt

#Top Level
def blockquote(content, cfw=None):
    print("Parsing BlockQuote: " + json.dumps(content))
    txt=""
    for c in content:
        txt += parse(c)
    return txt

def paragraph(content, cfw=None):
    print("Parsing Paragraph: " + json.dumps(content))
    txt=""
    for c in content:
        txt += parse(c)
    return txt

def bulletList(content, cfw=None):    
    print("Parsing Bulletlist: " + json.dumps(content))
    txt=""
    cfw=1
    for c in content:
        txt += parse(c, cfw)
        cfw += 1
    return txt

def orderedList(content, cfw=None):
    print("Parsing OrderedList: " + json.dumps(content))
    txt=""
    cfw=1
    for c in content:
        txt += parse(c, cfw)
        cfw += 1
    return txt

def codeBlock(content, cfw=None):
    print("Parsing CodeBlock: " + json.dumps(content))
    txt=""
    for c in content:
        txt += parse(c)
    return txt

def heading(content, cfw=None):
    print("Parsing Heading: " + json.dumps(content))
    txt=""
    for c in content:
        txt += parse(c)
    return txt

#Child Level
def listItem(content, cfw):
    print("Parsing ListItem: " + json.dumps(content))
    txt=""
    for c in content:
        txt += str(cfw)+". "+parse(c)+'\n'
    return txt


#Inline Level
def text(obj, cfw=None):
    print("Parsing Text: " + json.dumps(obj))
    txt=obj['text']
    if obj.get('marks'):
        #Search for Marks
        for m in obj.get("marks"):
            txt += parse(m)
    return txt

def link(attrs, cfw=None):
    print("Parsing Link")
    return "("+attrs.get("href")+")"

def hardBreak(data=None, cfw=None):
    print("Parsing HardBreak")
    return '\n'


def parse(adf, cfw=None):
    switcher = {
        "doc": (doc, 'content'),
        "blockquote": (blockquote, 'content'),
        "paragraph": (paragraph, 'content'),
        "text": (text, 'self'),
        "hardBreak": (hardBreak, ''),
        "bulletList": (bulletList, 'content'),
        "orderedList": (orderedList, 'content'),
        "listItem": (listItem, 'content'),
        "codeBlock": (codeBlock, 'content'),
        "heading": (heading, 'content'),
        "link": (link, 'attrs')                                 #Available only with type="text"

    }
    type=switcher.get(adf['type'])                              #Ex: "paragraph"
    fn=type[0]                                                  #Ex: paragraph()
    data=adf if type[1]=="self" else adf.get(type[1], None)     #Ex: "content"
    try: return fn(data, cfw)                                   #Ex: listItem(adf["content"], 1)
    except: return ''
