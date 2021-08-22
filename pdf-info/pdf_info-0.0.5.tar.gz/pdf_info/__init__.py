import PyPDF2
from pathlib import Path
from os import read
import fitz
from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter,TextConverter,XMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io
import sys


from pdfminer.converter import HTMLConverter, TextConverter, XMLConverter
from nltk.tokenize import word_tokenize
import pandas
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer, word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import math
from operator import itemgetter
from nltk import tokenize
import string
import nltk
import re
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from pathlib import Path
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('wordnet')
nltk.download('stopwords')


class pdf_info_class:
    def extract_header_para_keywords(file_path):
        import fitz
        from operator import itemgetter
        doc = fitz.open(file_path)

        def fonts(doc):

            styles = {}
            font_counts = {}
            idx = 0
            for page in doc:
                blocks = page.getText("dict")["blocks"]
                idx += 1
                for b in blocks:  # iterate through the text blocks
                    if b['type'] == 0:  # block contains text
                        for l in b["lines"]:  # iterate through the text lines
                            for s in l["spans"]:  # iterate through the text span
                                identifier = "{0}".format(s['size'])
                                styles[identifier] = {'size': s['size'], 'font': s['font']}
                                font_counts[identifier] = font_counts.get(identifier, 0) + 1  
                
            font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)

            if len(font_counts) < 1:
                raise ValueError("Zero discriminating fonts found!")

            return font_counts, styles


        # if granularity = False, then headers will be extracted on the basis of font and size
        font_counts, styles = fonts(doc)

        def font_tags(font_counts, styles):

            p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
            p_size = p_style['size']  # get the paragraph's size
            
            # sorting the font sizes high to low, so that we can append the right integer to each tag 
            font_sizes = []
            for (font_size, count) in font_counts:
                font_sizes.append(float(font_size))
            font_sizes.sort(reverse=True)

            # aggregating the tags for each font size
            size_tag = {}
            for size in font_sizes:
                if size == p_size:
                    size_tag[size] = '<p>'
                if size > p_size:
                    size_tag[size] = '<h>'
                elif size < p_size:
                    size_tag[size] = '<s>'

            return size_tag




        size_tag = font_tags(font_counts, styles)
        #print(size_tag)


        # Extracting headers, paragraphs and subscripts 



        def headers_para(doc, size_tag):
            first = True  # boolean operator for first header
            previous_s = {}  # previous span
            res = {}
            k = 1
            for page in doc:
                header_para = []  # list with headers and paragraphs
                blocks = page.getText("dict")["blocks"]
                #print(blocks)
                for b in blocks:  # iterate through the text blocks
                    if b['type'] == 0:  # this block contains text

                        # REMEMBER: multiple fonts and sizes are possible IN one block

                        block_string = ""  # text found in block
                        for l in b["lines"]:  # iterate through the text lines
                            #print(l)
                            for s in l["spans"]:  # iterate through the text spans
                                #print(s)
                                if s['text'].strip():  # removing whitespaces:
                                    #print(s['text'])
                                    if s['font'].find('Bold') != -1 and s['font'].find('Italic') == -1:
                                        previous_s = s
                                        block_string = "<h>" + s['text']    
                                    elif first:
                                        previous_s = s
                                        first = False
                                        block_string = size_tag[s['size']] + s['text']
                                    else:
                                        if s['size'] == previous_s['size'] and s['font'] == previous_s['font']:

                                            if block_string and all((c == "|") for c in block_string):
                                                # block_string only contains pipes
                                                block_string = size_tag[s['size']] + s['text']
                                            if block_string == "":
                                                # new block has started, so append size tag
                                                block_string = size_tag[s['size']] + s['text']
                                            else:  # in the same block, so concatenate strings
                                                block_string += " " + s['text']

                                        else:
                                            header_para.append(block_string)
                                            block_string = size_tag[s['size']] + s['text']

                                        previous_s = s

                            # new block started, indicating with a pipe
                        # block_string += "|"
                        header_para.append(block_string)
                key = []
                value = []
                for i in header_para:
                    if i == '':
                        continue
                    else:
                        flag = 1
                        s=""
                        t=""
                        for j in i:
                            if flag:
                                s = s + j
                            else:
                                t = t + j
                            if j == '>':
                                flag=0
                        key.append(s)
                        value.append(t)
                class Dictlist(dict):
                    def __setitem__(self, key, value):
                        try:
                            self[key]
                        except KeyError:
                            super(Dictlist, self).__setitem__(key, [])
                        self[key].append(value)
                d = Dictlist()
                i = 0
                while i < len(key):

                    d[key[i]]=value[i]
                    i+=1
                res[k] = d
                k = k+1  
            return res



        header_para = headers_para(doc, size_tag)
        #print(header_para)


        # Keywords from paragraphs and subscripts


        import re
        import nltk
        import string
        #nltk.download('stopwords')
        from nltk.corpus import stopwords
        from nltk.stem.porter import PorterStemmer
        from nltk.tokenize import RegexpTokenizer, word_tokenize
        #nltk.download('wordnet') 
        #nltk.download('punkt')
        from nltk.stem.wordnet import WordNetLemmatizer
        from nltk import tokenize
        import math



        def clean_text(sentence, stopwords_list, punct):
            corpus=list()
            # remove punctuations
            sentence = re.sub('[^a-zA-Z]', ' ', sentence)
            
            # convert to lower case
            sentence = str(sentence).lower()
            
            # remove tags
            sentence = re.sub("&lt;/?.*?&gt;"," &lt;&gt; ",sentence)
            
            #remove special characters
            sentence = re.sub("(\\d|\\W)+"," ",sentence)

            # remove urls
            sentence = re.sub(r"http\S+", "", sentence)
            sentence = re.sub(r"www\S+", "", sentence)
            # stop words
            #stopwords_list = set(stopwords.words('english'))
            
            # convert from string to list
            #sentence = sentence.split()
            word_list = word_tokenize(sentence)
            # remove stop words
            word_list = [word for word in word_list if word not in stopwords_list]
            # remove very small words, length < 3 as they don't contribute any useful information
            word_list = [word for word in word_list if len(word) > 2]
            # remove punctuation
            word_list = [word for word in word_list if word not in punct]
            
            #stemming
            ps  = PorterStemmer()
            #word_list = [ps.stem(word) for word in word_list]
            
            # lemmatize
            lemma = WordNetLemmatizer()
            sentence = [lemma.lemmatize(word) for word in word_list if not word in stopwords_list]
            sentence = " ".join(word_list)
            corpus.append(sentence)
            return sentence
        # this function is returing list  



        #Most frequently occuring words
        def get_top_ngrams(corpus, n=None, N=1):
            vec = CountVectorizer(ngram_range=(N,N), max_features=500).fit(corpus)
            bag_of_words = vec.transform(corpus)
            sum_words = bag_of_words.sum(axis=0) 
            words_freq = [(word, sum_words[0, idx]) for word, idx in      
                        vec.vocabulary_.items()]
            words_freq =sorted(words_freq, key = lambda x: x[1], 
                            reverse=True)
            return words_freq[:n]




        from sklearn.feature_extraction.text import CountVectorizer
        import re




        def check_sent(word, sentences):
            final = [all([w in x for w in word]) for x in sentences]
            sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
            return int(len(sent_len))

        def get_top_n(dict_elem, n):
                result = dict(sorted(dict_elem.items(), key = itemgetter(1), reverse = True)[:n]) 
                return result    



        stopwords_list = set(stopwords.words('english'))
        punct = set(string.punctuation)
        d = {}
        text =""
        idx = 0
        for item in header_para:
            text = ""
            idx = idx + 1
            for key in header_para[item]:
                if key == '<p>':    
                    temp = ""
                    for i in header_para[item][key]:
                        temp += i 
                    corpus = clean_text(temp, stopwords_list = stopwords_list, punct = punct)
                    temp = "".join(corpus) 
                    header_para[item][key] = temp     
                    text += temp
                    #print(temp)
                elif key == '<s>':
                    temp = ""
                    for i in header_para[item][key]:
                        temp += i 
                    corpus = clean_text(temp, stopwords_list = stopwords_list, punct = punct)
                    temp = "".join(corpus)
                    header_para[item][key] = temp
                    text += temp
                #print(temp)
            doc = text
                
            total_words = doc.split()
            total_word_length = len(total_words)

            total_sentences = tokenize.sent_tokenize(doc)
            total_sent_len = len(total_sentences)

            tf_score = {}
            for each_word in total_words:
                each_word = each_word.replace('.', '')
                if each_word not in stopwords_list:
                    if each_word in tf_score:
                        tf_score[each_word] += 1
                    else:
                        tf_score[each_word] = 1
            tf_score.update((x, y/int(total_word_length)) for x, y in tf_score.items())

            idf_score = {}
            for each_word in total_words:
                each_word = each_word.replace('.','')
                if each_word not in stopwords_list:
                    if each_word in idf_score:
                        idf_score[each_word] = check_sent(each_word, total_sentences)
                    else:
                        idf_score[each_word] = 1


                # Performing a log and divide
            idf_score.update((x, math.log(int(total_sent_len)/y)) for x, y in idf_score.items())
                
            tf_idf_score = {key: tf_score[key] * idf_score.get(key, 0) for key in tf_score.keys()}   

            lst = []
            for key in get_top_n(tf_idf_score, 10):
                if(len(key)>2):
                    lst.append(key)
                    lst  
            d[idx] = lst

        idx = 1
        temp = {}
        for item in header_para:
            if idx in d:
                temp['keywords'] = d[idx]
                header_para[item].update(temp)
                temp.clear()
            else:
                temp['keywords'] = []  
                header_para[item].update(temp)
                temp.clear()
            idx = idx + 1  
        return header_para


    def convert(file_path,header_para_key,result_list,page_input pages=None):
        # print('hello')
        # db = client[db_name]
        # my_collection = db[collection_name]
        if not pages: pagenums = set()
        else:         pagenums = set(pages)
        manager = PDFResourceManager()
        codec = 'utf-8'
        caching = True

        output = io.StringIO()
        converter = TextConverter(manager, output,  laparams=LAParams())

        interpreter = PDFPageInterpreter(manager, converter)
        infile = open(file_path, 'rb')
        i = 1
        for page in PDFPage.get_pages(infile, pagenums, caching=caching, check_extractable=True):
            
            interpreter.process_page(page)
            text = output.getvalue()

            mydict={}
            temp_dict = header_para_key[i]
            # res="".join(temp_dict['<h>']) #changed
            mydict['headers'] = temp_dict['<h>']   #changed
            mydict['paragraphs'] = temp_dict['<p>'][0:-1]  # changed
            mydict['keywords'] = temp_dict['keywords']
            key = '<s>'
            if key in temp_dict.keys():
                mydict['subscripts'] = temp_dict['<s>']
            else:
                mydict['subscripts'] = []
            
            #print(mydict)
            i += 1
            result_list.append(mydict)
            if(page_input>=i){
                return 0
            }
            return 1;
    def helper(file_path,page_num):
        result_list=[]
        header_para_key = pdf_info_class.extract_header_para_keywords(file_path)
        check = pdf_info_class.convert(file_path,header_para_key,result_list,page_num)
        return result_list,check
    def pdf_info(self,file_path,page_num,tag):
        result_list, check = pdf_info_class.helper(file_path,page_num)
        if(check==0):
            return []
        else:
            return result_list[page_num-1][tag]
                
# ob = pdf_info_class()
# file_path = "C:/Users/hp/Downloads/Harvard_UChicago_JD.pdf"
# res = ob.pdf_info(file_path)
# print(res)