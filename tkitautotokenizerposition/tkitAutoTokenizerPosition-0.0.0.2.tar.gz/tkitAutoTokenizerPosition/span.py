import numpy as np
from tqdm.auto import tqdm


class autoSpan:
    """[summary]
用于处理生成span模型训练格式


    
    
    """
    def  __init__(self,labelsList=[]) :
        """[summary]
        
        >labelsList=['疾病', '检查', '部位', '社会学', '关系', '流行病学', '其他', '药物', '其他治疗', '症状', '手术治疗', '预后']

        Args:
            labelsList (list, optional): [description]. Defaults to [].
        """
        
        self.labelsList=labelsList
        pass
    
    def bulidSpanMatrix(self,data,maxLen=128):
        """[summary]
        
        构建span数据
        
        > data=[{'start': 65, 'end': 70, 'type': '疾病'}]

        Args:
            data ([type]): [description]
            maxLen (int, optional): [description]. Defaults to 128.

        Returns:
            [type]: [description]
        """

        #     maxLen=128
        span_label = [0 for i in range(maxLen)]
        span_label = [span_label for i in range(maxLen)]
        span_label = np.array(span_label)
        #     start = [1, 3, 7]
        #     end  = [ 2,9, 9]
        #     label2id = [1,2,4]
        start = []
        end  = []
        label2id = []
        
        for it in data:
            start.append(it['start'])
            end.append(it['end'])
            label2id.append(self.labelsList.index(it['type']))
        for i in range(len(label2id)):
            span_label[start[i], end[i]] = label2id[i]  
        return span_label.tolist()
    
    
    
    def autoSpan(self,datas,maxLen=128):
        """[summary]
        自动构建Span数据集
        
        输入格式如下

        Args:
            datas ([type]): [description]
            
        >  datas=[{'text': '骨性关节炎@在其他关节（如踝关节和腕关节），骨性关节炎比较少见，并且一般有潜在的病因（如结晶性关节病、创伤）。', 'wordList': ['骨', '性', '关', '节', '炎', '@', '在', '其', '他', '关', '节', '（', '如', '踝', '关', '节', '和', '腕', '关', '节', '）', '，', '骨', '性', '关', '节', '炎', '比', '较', '少', '见', '，', '并', '且', '一', '般', '有', '潜', '在', '的', '病', '因', '（', '如', '结', '晶', '性', '关', '节', '病', '、', '创', '伤', '）', '。'], 'tag': [{'start': 0, 'end': 5, 'type': '疾病'}, {'start': 22, 'end': 27, 'type': '疾病'}, {'start': 2, 'end': 4, 'type': '部位'}, {'start': 9, 'end': 11, 'type': '部位'}, {'start': 14, 'end': 16, 'type': '部位'}, {'start': 18, 'end': 20, 'type': '部位'}, {'start': 24, 'end': 26, 'type': '部位'}, {'start': 47, 'end': 49, 'type': '部位'}, {'start': 0, 'end': 5, 'type': '疾病'}, {'start': 22, 'end': 27, 'type': '疾病'}, {'start': 13, 'end': 16, 'type': '部位'}, {'start': 0, 'end': 5, 'type': '疾病'}, {'start': 22, 'end': 27, 'type': '疾病'}, {'start': 17, 'end': 20, 'type': '部位'}, {'start': 0, 'end': 5, 'type': '疾病'}, {'start': 22, 'end': 27, 'type': '疾病'}, {'start': 44, 'end': 50, 'type': '社会学'}, {'start': 40, 'end': 42, 'type': '关系'}, {'start': 0, 'end': 5, 'type': '疾病'}, {'start': 22, 'end': 27, 'type': '疾病'}, {'start': 51, 'end': 53, 'type': '社会学'}, {'start': 40, 'end': 42, 'type': '关系'}]}]
            
            
            
            
            maxLen (int, optional): [description]. Defaults to 128.

        Returns:
            [type]: [description]
        """
        texts=[]
        for i,it in tqdm(enumerate(datas)):
        #     print(it)
            try:
                out=self.bulidSpanMatrix(it['tag'],self.labelsList,maxLen=maxLen)
                if i==0:

                    myDatas=[out]
                else:
                    myDatas.append(out) 
                texts.append(it['wordList'])
            except:
                pass
        return  texts,myDatas
    