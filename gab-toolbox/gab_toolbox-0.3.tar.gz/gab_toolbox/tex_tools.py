# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 20:47:13 2020

@author: gabri
"""



#--------------------------- Bib tools ---------------------------------------
"""
Functions to manipulate, filter and order .bib files. There is one main function
that extracts and puts the key used to classify the bib entries(date, ref, 
title etc..) and the corrisponding entry in a 2D array [key,[entry]].
Only with this format you can use the order_bib and filter_bib. I you don't 
want to use bib_entries you can set the [form] option to 1 and choose the 
criterion and it will run bib_entries before performing the choosen action. I 
suggest to use bib_entries and then apply the action so that you have more 
control. bib_entries returns the criterion as a string and the corresponding
entry.

If your list follows a different syntax you can customize the script
by changing the list_crit arguments. The first argument finds the symbol or 
string that identifies the line that contains the key. The second and third 
arguments are used to find and isolate the value of the key. For e.g. the
'date' key is located in the line that starts with '\tyear' and the value
is delimited by { }: '\tyear={2005}'
 
"""

from gab_toolbox import format_tools


def bib_entries(bib_array,crit):
    
        list_crit = {
        
        'by_ref': ['@','{',',','by reference'],
        'by_date': ['\tyear','{','}','by date'],
        'by_title': ['\ttitle','{','}','by title'],
        'by_author':['\tauthor','{','}','by author']
        
        }
        criterion = list_crit[crit]
        key_bibarr = []   
    
        for c,n in enumerate(bib_array):
        
            if n.startswith(criterion[0]): #I need to find the identifying symbol or string at the start.
                limit_inf = n.index(criterion[1])+1 #limits index
                limit_sup = n.index(criterion[2])
                key = n[limit_inf:limit_sup].lower() #key word            
            
            if n.startswith('@'):
                start = c          #start of the bib entry     
            elif n.startswith('}'):
                end = c+1          #end of the bib entry
                value = bib_array[start:end]
                key_bibarr.append([key,value])
         
        return key_bibarr
    
def sort_bib(bib_array,order=0,form=0,crit=''):
    
    bib_array = bib_entries(bib_array,crit) if form else bib_array
    
    key_bibarr_sort = sorted(bib_array,reverse=order)
    new_bibarr_text =  [n for i in key_bibarr_sort for n in i[1]]
    return new_bibarr_text,key_bibarr_sort


def filter_bib(bib_array,key_word,limit=0.5,form=0,crit=''):
    
    bib_filtered = []
    bib_array = bib_entries(bib_array,crit) if form else bib_array #use function bib_entries 
    values = [[index,string[0].split(' ')] for index,string in enumerate(bib_array)] # take key index and value
    
    for i in values:
        bib_match = format_tools.word_match(key_word,i[1],limit)[0] #match the key word with the possible combinations
        if bib_match: #if there are any matches it appends it 
            bib_filtered.append(bib_array[i[0]])
            
    key_bibarr_filt = [i for i in bib_filtered]
    new_bibarr_text = [n for i in bib_filtered for n in i[1]]
    return new_bibarr_text,key_bibarr_filt





#------------------------ Formatting tools ----------------------------------
    
def ttt(file_array,sep='\t'):
    new_file = []
    for c,i in enumerate(file_array):
        
        line_split = list(i.replace(sep,'&'))
        line_split.append('\\\\')
        new_file.append(''.join(line_split))
    new_file.insert(1,'\hline')
    
    return new_file







