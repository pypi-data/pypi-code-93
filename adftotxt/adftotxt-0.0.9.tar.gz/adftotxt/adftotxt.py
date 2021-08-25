import json

def test():
    print("Package is Linked & Working")

#Root Level
def doc(content, carryForward=None):
    print("Parsing Doc: " + json.dumps(content))
    text=""
    for c in content:
        text += parse(c)
        pass
    return text

#Top Level
def blockquote(content, carryForward=None):
    print("Parsing BlockQuote: " + json.dumps(content))
    text=""
    for c in content:
        text += parse(c)
    return text

def paragraph(content, carryForward=None):
    print("Parsing Paragraph: " + json.dumps(content))
    text=""
    for c in content:
        text += parse(c)
    return text

def bulletList(content, carryForward=None):    
    print("Parsing Bulletlist: " + json.dumps(content))
    text=""
    carryForward=1
    for c in content:
        text += parse(c, carryForward)
        carryForward += 1
    return text

def orderedList(content, carryForward=None):
    print("Parsing OrderedList: " + json.dumps(content))
    text=""
    carryForward=1
    for c in content:
        text += parse(c, carryForward)
        carryForward += 1
    return text

def codeBlock(content, carryForward=None):
    print("Parsing CodeBlock: " + json.dumps(content))
    text=""
    for c in content:
        text += parse(c)
    return text

def heading(content, carryForward=None):
    print("Parsing Heading: " + json.dumps(content))
    text=""
    for c in content:
        text += parse(c)
    return text

#Child Level
def listItem(content, carryForward):
    print("Parsing ListItem: " + json.dumps(content))
    text=""
    for c in content:
        #text += str(carryForward)+". "+parse(c)+'\n'
        text += "* "+parse(c)+', '
    return text


#Inline Level
def text(obj, carryForward=None):
    print("Parsing Text: " + json.dumps(obj))
    text=obj['text']
    if obj.get('marks'):
        #Search for Marks
        for m in obj.get("marks"):
            text += parse(m)
    return text

def link(attrs, carryForward=None):
    print("Parsing Link")
    return "("+attrs.get("href")+")"

def hardBreak(data=None, carryForward=None):
    print("Parsing HardBreak")
    return '\n'


def parse(adf, carryForward=None):
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
    try: return fn(data, carryForward)                                   #Ex: listItem(adf["content"], 1)
    except: return ''
