# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 22:06:43 2020

@author: gabri
"""


def valid_title(title,char='_'):
    new_title = title
    banned_chars = ["/","*","<",">",":","?","|",'"','\\']
    
    for j in banned_chars:
        new_title = new_title.replace(j,char) 
    return new_title


def import_file(file):
    with open(file,'r') as f:
        txt = [n[:-1] for n in f]
    return txt

def write_file(array,file):
    with open(file,'w') as f:
        for i in array:
            f.writelines(f'{i}\n')
    return None

def dic2arr(dictionary, order=0,sort=0,rev=0):
    if order:
        array = [[dictionary[i],i] for i in dictionary]
    else:
        array = [[i,dictionary[i]] for i in dictionary]
    if sort:
        array = sorted(sort,reverse=rev)
        
    return array


def arr2dic(array, sort=0,rev=0,overwrite=0):
    
    if sort:
        sorted_array = sorted(array,reverse=rev)
        
    if overwrite:
        if sort:
            dic= dict(sorted_array) 
        else:
            dic = dict(array)
    else:
        dic = dict()
        
        def loop(a):
            
            for i in a:
                key = i[0]
                value = i[1]
                if key in dic:
                    dic[key].append(value)
                else:
                    dic[key] = [value]
            return dic
            
        if sort:
           dic = loop(sorted_array)
            
        else:
           dic = loop(array)
		   
    return dic




def word_match(word,words,limit=0.5):
    

    #prep
    word=word.lower()
    word_len = len(word)
    words_array = [valid_title(string,'').lower() for string in words]#filter out all the non valid symbols and lower everything
    new_words=[]
    
    for i in words_array: #words that need to be compared: the ones short of one letter than the input word,the ones longer than the input word and the ones with the same length
        if len(word[:-1])==len(i):
            new_words.append(i+'%')
        elif len(word)<len(i):
            new_words.append(i[:word_len])
        elif len(word) == len(i):
            new_words.append(i)      
    
    #scoring
    final_score=0
    words_match = []
    index_match = []
    score_match = []
    
    #every word is compared letter by letter with the input word and if the letters match it adds 1 to the score. the final score is the total score divided by the input word length
    for b,i in enumerate(new_words):
        score = 0        
        for c,n in enumerate(word):
            if n == i[c]:
                score +=1
            else:
                score +=0
                
        final_score = score/word_len
        if final_score>=limit:
            words_match.append(words[b])
            index_match.append(b)
            score_match.append(final_score)
    return words_match,index_match,score_match
