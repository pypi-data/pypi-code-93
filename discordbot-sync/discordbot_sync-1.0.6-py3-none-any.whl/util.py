from email.utils import parsedate_to_datetime

def parse_date_header(s):
    return parsedate_to_datetime(s).timestamp()

def format_timestamp(t):
    return "<t:%d:D> at <t:%d:T> (<t:%d:R>)" % (t, t, t)

def hyperlink(text, url):
    return "[%s](%s)" % (text, url)

def escape_backticks(txt):
    # a truly terrible solution
    # sorry that Discord-flavored markdown
    # doesn't have a better option (backslash doesn't work)
    return txt.replace("`", "\u200b`\u200b")

def get_inline_code(txt):
    return "``%s``" % escape_backticks(txt)

def get_code_block(txt):
    return "```%s```" % escape_backticks(txt)

def mention_role(role):
    return "<@&%s>" % role

def make_flags(*values):
    x = 0
    for v in values:
        x |= 1 << v
    return x
get_flags = make_flags

def col32(r,g,b):
    return (r % 256) << 16 | (g % 256) << 8 | (b % 256)

def embed(title = None, description=None, color=None, fields = None):
    e = {}
    if title is not None:
        e['title'] = str(title)
    if description is not None:
        e['description'] = str(description)
    if color is not None:
        e['color'] = col32(*color)
    if fields is not None:
        e['fields'] = {}
        for n in fields:
            e['fields'][n] = str(fields[n])
    return e

