# -*- coding: utf-8 -*-

class AutoTokenizerPosition:
    """
    用来处理只有关键词的ner数据
    
    起始位置
    tokenizer = BertTokenizer.from_pretrained("clue/albert_chinese_tiny")
    tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
    使用这个可以减少不必要的麻烦
    
    
    
    """
    def __init__(self,tokenizer):
        self.tokenizer=tokenizer
        pass
    def getWordList(self,text):
        """分词列表"""
        text=text.lower()
        text=text.replace(" ",self.tokenizer.pad_token)
        # print(text)
#         word=word.lower()
        return self.tokenizer.tokenize(text)
    def autoLen(self,text):
        """获取文本分词后位置"""
        text=text.lower()
#         word=word.lower()
        realLen=len(self.getWordList(text))
        return realLen
    
    
    def findAll(self,text, word):
        """
        获取词语在文字中的所有开始位置
        """
        text=text.lower()
        word=word.lower()
        idx = text.find(word)
        while idx != -1:
            yield idx
            idx = text.find(word, idx + 1)
    def fixPosition(self,text,word,startList=[]):
        """自动获取分词后起始位置
        自动匹配所有存在的位置
        
        传入位置可以限制查找的位置
        """
#         print(text,word)
        text=text.lower()
        word=word.lower()
        if len(startList) ==0:
            startList=self.findAll(text, word)
        for start in startList:
            s_start=self.autoLen(text[:start])
        #     print("s_start",s_start)
            startLen=self.autoLen(word)
            # print("s_end", s_start,s_start+startLen)  
            yield s_start,s_start+startLen
    def autoTypeWord(self,text,word,wType=None,startList=[]):
        for s_start,s_end in self.fixPosition(text,word,startList=[]):
#             print(s_start,s_end)
#             WordList=self.getWordList(it['text'])
            yield s_start,s_end,wType
