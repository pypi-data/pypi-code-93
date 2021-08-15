"""
构建BIO结构数据集
"""


class autoBIO:
    """[summary]
    
    用于构建bio结构数据集
    """
    def __init__(self) -> None:
        
        
        
        pass
    def bulid(self,it):
        """[summary]
        
        
        it={'text': '急性胰腺炎@有研究显示，进行早期 ERCP （24 小时内）可以降低梗阻性胆总管结石患者的并发症发生率和死亡率； 但是，对于无胆总管梗阻的胆汁性急性胰腺炎患者，不需要进行早期 ERCP。', 'wordList': ['急', '性', '胰', '腺', '炎', '@', '有', '研', '究', '显', '示', '，', '进', '行', '早', '期', '[PAD]', 'er', '##cp', '[PAD]', '（', '24', '[PAD]', '小', '时', '内', '）', '可', '以', '降', '低', '梗', '阻', '性', '胆', '总', '管', '结', '石', '患', '者', '的', '并', '发', '症', '发', '生', '率', '和', '死', '亡', '率', '；', '[PAD]', '但', '是', '，', '对', '于', '无', '胆', '总', '管', '梗', '阻', '的', '胆', '汁', '性', '急', '性', '胰', '腺', '炎', '患', '者', '，', '不', '需', '要', '进', '行', '早', '期', '[PAD]', 'er', '##cp', '。'], 'tag': [{'start': 0, 'end': 5, 'type': '疾病'}, {'start': 69, 'end': 74, 'type': '疾病'}, {'start': 17, 'end': 19, 'type': '检查'}, {'start': 85, 'end': 87, 'type': '检查'},
        
        
        
        返回格式如下
        
        {'text': '急性胰腺炎@有研究显示，进行早期 ERCP （24 小时内）可以降低梗阻性胆总管结石患者的并发症发生率和死亡率； 但是，对于无胆总管梗阻的胆汁性急性胰腺炎患者，不需要进行早期 ERCP。', 'wordList': ['急', '性', '胰', '腺', '炎', '@', '有', '研', '究', '显', '示', '，', '进', '行', '早', '期', '[PAD]', 'er', '##cp', '[PAD]', '（', '24', '[PAD]', '小', '时', '内', '）', '可', '以', '降', '低', '梗', '阻', '性', '胆', '总', '管', '结', '石', '患', '者', '的', '并', '发', '症', '发', '生', '率', '和', '死', '亡', '率', '；', '[PAD]', '但', '是', '，', '对', '于', '无', '胆', '总', '管', '梗', '阻', '的', '胆', '汁', '性', '急', '性', '胰', '腺', '炎', '患', '者', '，', '不', '需', '要', '进', '行', '早', '期', '[PAD]', 'er', '##cp', '。'], 'tag': [{'start': 0, 'end': 5, 'type': '疾病'}, {'start': 69, 'end': 74, 'type': '疾病'}, {'start': 17, 'end': 19, 'type': '检查'}, {'start': 85, 'end': 87, 'type': '检查'}], 'data': {'text': '急性胰腺炎@有研究显示，进行早期 ERCP （24 小时内）可以降低梗阻性胆总管结石患者的并发症发生率和死亡率； 但是，对于无胆总管梗阻的胆汁性急性胰腺炎患者，不需要进行早期 ERCP。', 'spo_list': [{'Combined': False, 'predicate': '影像学检查', 'subject': '急性胰腺炎', 'subject_type': '疾病', 'object': {'@value': 'ERCP'}, 'object_type': {'@value': '检查'}}]}, 'tagList': ['B-疾病', 'M-疾病', 'M-疾病', 'M-疾病', 'E-疾病', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-检查', 'E-检查', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-疾病', 'M-疾病', 'M-疾病', 'M-疾病', 'E-疾病', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-检查', 'E-检查', 'O']}
        
        """
        # print(it)
        tags=["O"]*len(it["wordList"])
        for w,t in zip(it["wordList"],tags):
            # print(w,t)
            
            for tse in it['tag']:
                # print(tse)
                
                for rid in range(tse['start'],tse['end']):
                    if len(it["wordList"])>tse['start'] and len(it["wordList"])>tse['end']:
                        if rid==tse['start']:
                            tags[rid]="B-"+tse['type']
                        elif rid ==tse['end']-1:
                            try:
                                tags[rid]="E-"+tse['type']
                            except:
                                # print(len(tags),tse['start'],tse['end'])
                                pass
                        else:
                            tags[rid]="M-"+tse['type']
            
            
            # for w,tag in zip(it["wordList"],tags):
            #     print(w,tag)
            
            it['tagList']=tags
            
            return it