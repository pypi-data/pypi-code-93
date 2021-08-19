__all__ = ['_br','_slashcommand','_begin','_end','_caption','_label','_keepinplace']

def _texcomment(comment):
    if type(comment) != "str":
        return "%"+str(comment)
    return "%"+comment

def _br(): return "\n"

def _slashcommand(text):return "\\"+text

def _begin(text): return "\\begin{"+text+"}"

def _end(text): return "\\end{"+text+"}"

def _caption(caption): return "\\caption{"+caption+"}"

def _label(label): return "\\label{"+label+"}"

def _keepinplace(): return "[htb!]"

