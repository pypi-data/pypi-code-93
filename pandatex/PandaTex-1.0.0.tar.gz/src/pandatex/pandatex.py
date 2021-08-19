import pandas as pd
import numpy as np
from utils._texbasics import *
from utils._validate import _validate_options

def _begin_tabular(N_columns, atom, coltype, header, indexed, align,hlines):
    if indexed:
        N_columns = N_columns+1

    if coltype == 'grid':
        content = _begin("tabular")+"{*{"+str(N_columns)+"}{"+atom.replace('c',align)+"}|}" +_br()
    if coltype == 'nogrid':
        atom = 'c '.replace('c',align)
        content = _begin("tabular")+"{*{"+str(N_columns)+"}{"+atom+"}}" +_br()
        hlines = False
    if coltype == 'indexed':
        atom = 'c|'.replace('c',align)
        content = _begin("tabular")+"{|c||*{"+str(N_columns-1)+"}{"+atom+"}}" +_br()
        
    if (header and hlines):
        content += "\\hline" + _br()
        
    return content
    
def _end_tabular(): return _end("tabular") +_br()

#Functions to entire table
def _begin_entire_table(indexed,align,hlines,N_columns,caption="", label="",atom = '|c',coltype='grid', header = True): 
    return _begin("table")+_keepinplace() + _br() + _slashcommand("centering")+_br()+_begin("small")+_br()+_add_caption_and_label(caption, label) + _begin_tabular(N_columns,atom,coltype, header,indexed, align,hlines) 
    
def _end_entire_table(): return _end_tabular() + _end("small") + _end("table")

"""
captionize and label
"""

def _add_caption_and_label(caption, label):
    return _caption(caption) +_label(label)+_br()

def _encoded_header(DataFrame, indexed,hlines,coltype):
    joiner = ' & '
    n_columns = len(DataFrame.columns)
    if coltype == 'nogrid':
        hlines = False

    if hlines:
        hline = "\\hline"
    else:
        hline = " "
    if indexed:
        final_string = ' '
        for i in range(n_columns):
            final_string = final_string + joiner + DataFrame.columns[i]
    else:
        final_string = DataFrame.columns[0]
        for i in range(1,n_columns):
            final_string = final_string + joiner + DataFrame.columns[i]
    final_string = final_string + ' \\\\ '+hline
    return final_string + _br()

def _table_single_line(Series, line_name,indexed,hlines,coltype):
    joiner = ' & '
    if coltype == 'nogrid':
        hlines = False

    if hlines:
        hline = "\\hline"
    else:
        hline = " "

    if indexed:
        final_string = str(line_name).replace('$','\$')
        for i in Series:
            final_string = final_string + joiner + str(i)
    else:
        final_string = str(Series[0])
        for i in range(1,len(Series)):
            final_string = final_string + joiner + str(Series[i])
    final_string = final_string + ' \\\\ '+hline
    return final_string + _br()
    
class TexTable:
    """
    Anotation
    """
    def __init__(self,name= "", filename="Default",label = " ", caption = " ", dataframe = None):
        self.name = name
        self.filename = filename+".tex"
        self.label = label
        self.caption = caption
        self.dataframe = dataframe
        self.textable = None
        return

    #Setting functions   
    def __str__(self):
        return "Table " + self.name
        
    def setdataframe(self, dataframe):
        self.dataframe = dataframe
        return
    
    def setlabel(self, label):
        self.label = label
        return
    
    def setcaption(self, caption):
        self.caption = caption
        return
    
    def setfilename(self, filename):
        self.filename = filename + ".tex"
        return
    
    def setname(self, name):
        self.name = name
        return
    
    #Functions for printing           
    def printtextable(self,**kwargs):
        options = {
            "coltype":"grid",
            "overfill":"scale",
            "align":"c",
            "indexed":True,
            "hlines":True,
        }
        options.update(kwargs)
        if _validate_options(options):
            self._generate_textable(options)
            print(self.textable)
        return 
    def writetextable(self, **kwargs):
        options = {
            "coltype":"grid",
            "overfill":"scale",
            "align":"c",
            "indexed":True,
            "hlines":True
        }
        options.update(kwargs)
        if _validate_options(options):
            self._generate_textable(options)
            print("\\include{"+self.filename[:-4]+"}")
            f = open(self.filename,'w')
            f.write(self.textable)
            f.close()
        return

    def _generate_textable(self, options):
        self.textable = _begin_entire_table(N_columns=len(self.dataframe.columns), caption = self.caption, label = self.label, coltype = options["coltype"], indexed = options["indexed"], align = options["align"],hlines = options["hlines"])
        self.textable += _encoded_header(self.dataframe,indexed = options["indexed"],hlines = options["hlines"],coltype = options["coltype"])
        for i in range(len(self.dataframe.index)):
            self.textable += _table_single_line(self.dataframe.values[i], self.dataframe.index[i], indexed = options["indexed"],coltype = options["coltype"],hlines = options["hlines"])
        self.textable += _end_entire_table()
        return
