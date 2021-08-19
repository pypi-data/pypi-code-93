from pythainlp import word_tokenize
from pythainlp import Tokenizer as TokenizerNLP
from pythainlp.util import dict_trie
from pythainlp.corpus.common import thai_words

import pandas as pd
import numpy as np
import re

import json 

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM,Dense, Dropout
from tensorflow.keras.layers import SpatialDropout1D
from tensorflow.keras.layers import Embedding

from tensorflow.keras.models import load_model

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

tokenizer = 0

embedding_vector_length = 60
vocab_size = 2300
maxlen = 60

def trans_result(r):
    r = int(r.round().item())
    if(r==0):
        return "บวก"
    else:
        return "ลบ"

def setTokenizer(s):
    global tokenizer
    tokenizer = s

def process_txt_init():
    words = ["ไทยออยล์","โควิด","โควิด19","โควิด-19","โคโรนา","D/E","P/E","P/BV","ออน์ไลน์","set50","set100",
             "เต็มมูลค่า","เทรดวอร์","เพิ่มทุน","มากกว่าคาด","Q1","Q2","Q3","Q4","B1","B2","B3",
             "มค","กพ","มีค","เมย","พค","มิย","กค","สค","กย","ตค","พย","ธค",
             "น้อยกว่าคาด","ตามคาด","ดีกว่าคาด","สูงกว่าคาด","ต่ำกว่าคาด","ผิดคาด","แย่กว่าคาด",
             "รีโนเวท","ศูนย์วิจัยกสิกร","กสิกรไทย","ผู้บริโภค","บริษัท","ทริส","ทริสเรทติ้ง","ซื้อหุ้นคืน",
             "กำไรพิเศษ","รีบาวด์","รีบาวนด์","รีบาวน์","สว่างหลังฝน","ฟ้าหลังฝน","ซีซั่น","ซีซัน","นกสกู๊ต",
             "วอลลุ่ม","ไตรมาส","ไตรมาศ","เชงเก้น","อีอีซี","ททท","ซินฟาตี้",
             "กองทุนการเงินระหว่างประเทศ","เวอร์จิน","อิควิตี้","รมต","แม็คโคร","ซีฟู้ด","ปปช","สคร","สตง","กสทช",
             "อีเมอร์จิ้ง","5G","ถุงมือยาง","ไฟเซอร์อิงค์","ดินถล่ม","อิจิฟุสะ","หนี้ครัวเรือน",
             "บาทแข็ง","บาทอ่อน","จิ้นผิง","สีจิ้นผิง","กิจการ","ไบออนเทค","เรมเดซิเวียร์","ออมนิแชแนล",
             "M&A","m&a","ควบรวมกิจการ","เหรินหมิน","อู่ฮั่น","ฮิวสตัน"]
    custom_words_list = set(thai_words())
    ## add multiple words
    custom_words_list.update(words)

    trie = dict_trie(dict_source=custom_words_list)
    custom_tokenizer = TokenizerNLP(custom_dict=trie, engine='newmm')
    return custom_tokenizer

def process_txt_split(txt):
    token = process_txt_init()
    k = token.word_tokenize(txt)
    k = [i for i in k if(i.replace(" ",""))]
    k = " ".join(k)
    return k

def process_txt_remove_float(txt):
    return re.sub("^\d+\s|\s\d+\s|\s\d+$|(\s\d+.\d+)+", " ", txt)

def process_txt_remove(txt):
    txt = txt.replace("TFRS 9","TFRS9")
    txt = txt.replace("“","")
    txt = txt.replace("“","")
    txt = txt.replace("”","")
    txt = txt.replace("”","")
    txt = txt.replace("‘","")
    txt = txt.replace("’","")
    txt = txt.replace("–","")
    txt = txt.replace("P/E","PE")
    txt = txt.replace("D/E","DE")
    txt = txt.replace("P/BV","PBV")
    txt = txt.replace("/"," ")
    txt = txt.replace("\"","")
    txt = txt.replace("\"","")
    txt = txt.replace("-","")
    txt = txt.replace(":","")
    txt = txt.replace("ฯ","")
    txt = txt.replace("(","")
    txt = txt.replace(")","")
    txt = txt.replace("'","")
    txt = txt.replace("%","")
    txt = txt.replace("m&a","ควบรวมกิจการ")
    txt = txt.replace("M&A","ควบรวมกิจการ")
    txt = txt.replace("โคโรน่า","โคโรนา")
    txt = txt.replace("วิตก","วิตกกังวล")
    txt = txt.replace("ล.","ล้าน")
    txt = txt.replace(".com","")
    txt = txt.replace(".net","")
    txt = txt.replace(".co.th","")
    txt = txt.replace(".","")
    txt = txt.replace("\xa0","")
    txt = process_txt_remove_float(txt)
    return txt

def pre_process_txt(txt):
    txt = process_txt_remove(txt) 
    txt = process_txt_split(txt)
    
    tw = tokenizer.texts_to_sequences([txt])
    tw = pad_sequences(tw,maxlen=maxlen)
    #prediction = int(model.predict(tw).round().item())
    #print(model.predict(tw),prediction)
    #print(prediction)
    return tw

def create_model():

 model = Sequential()
 model.add(Embedding(vocab_size, embedding_vector_length,     
                                     input_length=maxlen) )
 model.add(SpatialDropout1D(0.25))
 model.add(LSTM(128, dropout=0.5, recurrent_dropout=0.5))
 model.add(Dropout(0.2))
 model.add(Dense(512, activation='relu'))
 model.add(Dropout(0.2))
 model.add(Dense(1024, activation='relu'))
 model.add(Dropout(0.2))
 model.add(Dense(512, activation='relu'))
 model.add(Dropout(0.2))
 model.add(Dense(128, activation='relu'))
 model.add(Dropout(0.20))
 model.add(Dense(1, activation='relu'))

 model.compile(loss='binary_crossentropy',optimizer='adam', 
                           metrics=['accuracy'])
 #print(model.summary())
 return model