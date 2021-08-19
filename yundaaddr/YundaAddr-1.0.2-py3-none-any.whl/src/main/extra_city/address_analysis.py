import pandas as pd
import numpy as np
import jieba
import re
from yd_addr.src.main.extra_city.load_data import name_code_dict, code_name_dict, stop_word_list
import yd_addr.frozen

BASE_DIR = yd_addr.frozen.app_path() + "/"
jieba.load_userdict(BASE_DIR + r'resources/cutworddict_plus.txt')


def jieba_address_cut(rawtext, flag=0):
    """
    rawtext='重庆市.重庆市.渝北区.双凤桥街道空港大道655号长安锦尚城25栋香花桥街道食品'
    rawtext='西航港新街686号景茂'
    自定义结巴分词,用以分出道路名称 某某路某某号 ，以及一些常见的POI名称
    :param rawtext:
    :param flag: 0 结巴全模式分词，使用自定义地址词典，用于地址标准提取使用 返回一个list
           flag:1 结巴精准模式分词，使用自定义地址词典，用于关键词提取，道路、路号、POI提取
    :return: 返回四个list，finallist ,roadlist ,roadlist_num,pointlist
    """
    if flag == 1:
        rawtext = str(rawtext)
        finallist = []
        roadlist = []  ##########分出来的 某某路
        roadlist_num = []  ########分出来的 某某路某某号
        pointlist = []  ##########分出来的 某某医院 某某大厦
        if rawtext.strip() != '':
            rawtext = rawtext.replace('\n', ' ').replace('\r', ' ')
            segwords = jieba.cut(rawtext)  ##默认精准模式
            filter_list = []
            ###去除标点符号    其他不剔除，停止词里面不能包含 数字1 2 3 4以及 地址敏感词道 路 街 号
            for word in segwords:
                if not word in stop_word_list:
                    filter_list.append(word)
                else:
                    filter_list.append(' ')  # 如果是标点符号 使用 ‘ ’隔开   产生一些空值，避免后面错误的向前合并
            if len(filter_list) > 1:  ###如果分词结果，多个字符串
                if filter_list != []:
                    ###合并词 ###社区小区  进行前项连接
                    mergeWord2 = ['坪', '里', '泾', '浜', '村', '新村', '庄', '山庄', '屯', '镇', '小镇', '乡', '小区', '区', '东区', '西区', '南区',
                                  '北区', '新区', '社区', '园区', '胡同', '百货', '广场', '市场', '大市场', '林场',
                                  '工业区', '基地', '集团', '公司', '分公司', '有限公司', '股份', '股份公司', '股份有限公司', '科技股份有限公司', '投资公司',
                                  '办事处', '分局', '总局', '派出所',
                                  '大楼', '大厦', '商厦', '银行', '支行', '分行', '厂', '店', '商店', '酒店', '专卖店', '门店', '超市', '饭店',
                                  '旗舰店', '官方旗舰店',
                                  '苑', '东苑', '西苑', '南苑', '北苑', '花苑', '佳苑', '家苑', '名苑', '园', '家园', '公园', '花园', '花園',
                                  '佳园', '嘉园', '别墅', '城', '商城', '商贸城', '新城',
                                  '府', '馆', '公馆', '宾馆', '公寓', '院', '大院', '会所',
                                  '小学', '中学', '大学', '大专', '校区', '学院', '学校', '分校', '总部', '分部', '总院', '分院', '卫生院', '医院',
                                  '桥', '大桥', '路', '路口', '公路', '东路', '西路', '南路', '北路', '中路', '大路', '道', '大道', '街', '大街',
                                  '东街', '西街', '南街', '北街', '中街', '商业街', '步行街',
                                  '巷', '号楼', '号门', '号房', '号院', '号馆', '速递',
                                  '一期', '二期', '三期', '四期', '五期', '六期', '七期', '八期', '九期', '十期', '1期', '2期', '3期', '4期',
                                  '5期', '6期', '7期', '8期', '9期', '10期',
                                  '一区', '二区', '三区', '四区', '五区', '六区', '七区', '八区', '九区', '十区', '1区', '2区', '3区', '4区',
                                  '5区', '6区', '7区', '8区', '9区', '10区',
                                  'A区', 'B区', 'C区', 'D区', 'E区', 'F区', 'G区',
                                  'a区', 'b区', 'c区', 'd区', 'e区', 'f区', 'g区']  ###'单元','栋','幢',

                    if len(filter_list) > 1:
                        for i in range(1, len(filter_list)):  ###合并
                            temp = filter_list[i]
                            if temp in mergeWord2:
                                if filter_list[i - 1].strip() != '':
                                    filter_list[i] = filter_list[i - 1] + filter_list[i]
                                    # filter_list[i]=filter_list[i].strip()   ###如果是 空 '  ' 需要清除
                                    filter_list[i - 1] = filter_list[i]
                                    pointlist.append(filter_list[i])
                    ###对filter_list去重    ##i 和i-1 相同进行去重
                    if len(filter_list) > 1:
                        filter_list_temp = []
                        filter_list_temp.append(filter_list[0])
                        for i in range(1, len(filter_list)):
                            if filter_list[i] != filter_list[i - 1]:
                                filter_list_temp.append(filter_list[i])
                        filter_list = filter_list_temp
                    #####如果第一个分词为单字符，进行合并
                    if len(filter_list[0]) == 1:  #####如果第一个分词为单字符，进行合并
                        filter_list[0] = filter_list[0] + filter_list[1]  # ".join(filter_list[0:2])
                        filter_list.remove(filter_list[1])
                    ####合并路 ---号
                    mergeWord1 = ['路', '道', '街', '巷', '弄', '里']
                    for i in range(len(filter_list) - 2):
                        temp = filter_list[i][-1]
                        if temp in mergeWord1 and len(filter_list[i]) > 1:
                            # try:
                            if (filter_list[i + 1][0] in ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                                                          '0', '1', '2', '3', '4', '5', '6', '7', '8',
                                                          '9']):  ###下一个词需要是数字才可以合并路号
                                if filter_list[i + 2][0] in ['号', '弄', '座', '栋', '幢']:
                                    if len(filter_list[i]) <= 2:
                                        if i != 0:  ###不是第一个词
                                            filter_list[i] = filter_list[i - 1] + filter_list[i]
                                            filter_list[i - 1] = filter_list[i]
                                            filter_list[i + 1] = filter_list[i] + filter_list[i + 1] + filter_list[
                                                i + 2]
                                            filter_list[i + 2] = filter_list[i + 1]
                                            roadlist.append(filter_list[i])
                                            roadlist_num.append(filter_list[i + 1])
                                    else:
                                        filter_list[i + 1] = filter_list[i] + filter_list[i + 1] + filter_list[i + 2]
                                        filter_list[i + 2] = filter_list[i + 1]
                                        roadlist.append(filter_list[i])
                                        roadlist_num.append(filter_list[i + 1])

                                else:
                                    pass
                            ####后面跟的不是数字
                            else:
                                if len(filter_list[i]) <= 2:
                                    if i != 0:
                                        filter_list[i] = filter_list[i - 1] + filter_list[i]
                                        filter_list[i - 1] = filter_list[i]
                                        roadlist.append(filter_list[i])
                                else:
                                    roadlist.append(filter_list[i])

                    ###剔除重复 \数字 和长度小于2的
                    finallist = []
                    for i in filter_list:
                        try:
                            int(i)  ###纯数字不进入结果
                        except:
                            if len(i.strip()) >= 2 and i not in finallist and i.encode(
                                    'UTF-8').isalnum() == False:  ###分词不小于2  不是纯数字  纯字母 或者数字字母混合
                                finallist.append(i.strip())
                else:
                    finallist = []
            elif len(filter_list) == 1:  ###如果分词只有一个词
                if len(filter_list[0]) >= 2:  ##分词长度不小于2
                    finallist = filter_list
                else:
                    finallist = []
            else:  ####如果分词结果剔除停止词后 为空
                finallist = []
        else:
            finallist = []
        return finallist  # ,roadlist ,roadlist_num,pointlist
    elif flag == 0:
        finallist = []
        if rawtext.strip() != '':
            rawtext = rawtext.replace('\n', ' ').replace('\r', ' ')
            segwords = jieba.lcut(rawtext, cut_all=True)  ##默认精准模式  cut_all=True 全模式
            finallist = list(set(segwords))
        return finallist


def standard4classaddress(addr):
    addr = addr
    leftaddr = addr
    out,outcode=['','','','',''],['','','','','']
    rawcode={1:{},2:{},3:{},4:{},5:{}}  #全是原始的code
    supportcode={1:{},2:{},3:{},4:{},5:{}}  ###全是截取的code
    covercode = {1:set(),2:set(),3:set(),4:set(),5:set()}  ####set 基于原始code的组合 非截取的 原始 省 匹配组合
    ##分词结果
    cutwordlist=jieba_address_cut(addr, flag=0)
    ##通过分词找code
    for cutword in cutwordlist:
        if cutword in name_code_dict:  ###优于.keys(),更优于list查找
            for code in name_code_dict[cutword]:
                templen=len(code)
                for i,j in enumerate([2,4,6,9,12],start=1):
                    if j < templen:
                        supportcode[i][code[0:j]] = supportcode[i].get(code[0:j], 0) + 1
                    elif j == templen:
                        rawcode[i][code] = rawcode[i].get(code, [])
                        rawcode[i][code].append(cutword)
                    else:
                        covercode[i].add(code)
    ####匹配的级别数
    class_set = set()
    topclass = 9999   ###足够大的数字都行
    lowclass = 0      ###小于1的数字都行
    for i,j in enumerate([2,4,6,9,12],start=1):
        if len(rawcode[i]) > 0:
            class_set.add(i)
            if i > lowclass:
                lowclass = i
            if i < topclass:
                topclass = i
    getclassnum = len(class_set)

    ###########判断 模式0 模式 0 或者 0
    if getclassnum == 0:  ##w问题件  因为没有识别到任何四级地址
        pass ###out=['','','','','']
    ##############m  模式1  模式1  模式1  模式1  模式1
    else :  ### 匹配一个或者多个行政单位
        ###################################################################
        ######                               第一部分：向下寻求支持  -----整合成一段循环
        ####################################################################
        def getsupported(classlevel):
            tempsupported_dict={}
            temp = []
            if len(rawcode[classlevel]) != 0:
                temp = list(rawcode[classlevel].keys())
                for i in temp:
                    # print(i)
                    if code_name_dict[i[0:2]][i][0] in rawcode[classlevel][i]:  ###匹配的标准名称，则加1分
                        tempsupported_dict[i] = tempsupported_dict.get(i, 0) + 2
                    else:
                        tempsupported_dict[i] = tempsupported_dict.get(i, 0) + 1
                    if i in supportcode[classlevel].keys():  ####无支持则不添加，由下级支持，则加分
                        tempsupported_dict[i] = tempsupported_dict.get(i, 0) + supportcode[classlevel][i]
                    else:
                        pass
            return tempsupported_dict
        ###计算支持度投票
        provincesupported = getsupported(1)
        citysupported = getsupported(2)
        countysupported = getsupported(3)
        townsupported = getsupported(4)
        villagesupported = getsupported(5)


        ###################################################################
        ######                               第二部分：向上寻求保护  -----整合成一段循环
        ####################################################################
        def getcovered(classlevel):
            tempcovered = {}
            temprawcodelist = []
            if len(rawcode[classlevel]) != 0:  ###有乡镇匹配
                temprawcodelist = list(rawcode[classlevel].keys())  ###匹配上的乡镇代码
                for code in temprawcodelist:
                    tempcutset = set()
                    for i ,j in enumerate([2,4,6,9,12],start=1):
                        if i < classlevel:
                            tempcutcode = code[0:j]
                            tempcutset.add(tempcutcode)
                        else:
                            break
                    covernum = len(tempcutset.intersection(set(covercode[classlevel])))
                    if covernum > 0:
                        tempcovered[code] = tempcovered.get(i, 0) + covernum
            return tempcovered

        ###计算cover投票
        provincecovered = getcovered(1)
        citycovered = getcovered(2)
        countycovered = getcovered(3)
        towncovered = getcovered(4)
        villagecovered = getcovered(5)

        ###################################################################
        ######                               第三部分：求并集  整合成一段
        ####################################################################

        def combin_support_cover(suported,covered):
            temp_supported = suported
            temp_covered = covered
            for key, value in temp_covered.items():
                # print ( key, value )
                if key in temp_supported:
                    temp_supported[key] += value
                else:
                    temp_supported[key] = value
            temp_supported = dict(sorted(temp_supported.items(), key=lambda d: d[1], reverse=True))
            return temp_supported

        provincesupported = combin_support_cover(provincesupported,provincecovered)
        citysupported = combin_support_cover(citysupported, citycovered)
        countysupported = combin_support_cover(countysupported, countycovered)
        townsupported = combin_support_cover(townsupported, towncovered)
        villagesupported = combin_support_cover(villagesupported, villagecovered)

        ###################################################################
        ######                               第四部分：求最终值  ----整合成一段循环
        ####################################################################
        ###########1、provincesupported、citysupported、countysupported、townsupported  已经确定（都是匹配到的行政级别，及其支持度）
        ###########2、从从最下级别遍历寻找上下相互呼应的行政级别组合系列。
        ###########3、计算每个系列的投票综合，行政级别之和，坐高行政级别
        ###########4、各配套组合按照总表数（降序）、行政级别数量（降序）、行政级别之和（升序，行政级别越高越好，即和越小越好）、最大行政级别（越高越好）
        supported_dict = {1: provincesupported, 2: citysupported,
                          3: countysupported, 4: townsupported,
                          5: villagesupported}
        supported_lists = []
        tempid = [5, 4, 3, 2, 1]
        templen = [12, 9, 6, 4, 2]
        for i ,j in zip(tempid,templen):
            if supported_dict[i] != {}:
                for k in supported_dict[i]:
                    temp = ['','','','','']
                    temp_vote = 0
                    temp_class_sum = i  ##级别之和
                    temp_topclass = i  ###最高级别
                    temp_class_count = 1
                    #### 级别 i 的处理
                    temp[i - 1] = k
                    temp_vote = temp_vote + supported_dict[i][k]
                    for u , v in enumerate([2,4,6,9,12],start=1):
                        if u > i :
                            temp[u-1]=''
                        elif u < i:
                            if k[0:v] in supported_dict[u]:
                                temp[u-1]=k[0:v]
                                temp_vote = temp_vote + supported_dict[u][k[0:v]]
                                temp_class_sum =temp_class_sum + u
                                if u < temp_topclass:
                                    temp_topclass = u
                                if u != i:
                                    temp_class_count=temp_class_count+1
                        else:
                            pass
                    temp.extend([temp_vote,temp_class_count,temp_class_sum,temp_topclass])
                    supported_lists.append(temp)
            else:
                pass

        supported_df = pd.DataFrame(supported_lists, columns=['code1','code2','code3','code4','code5', 'votes','class_count', 'class_sum', 'top_class'])
        supported_df = supported_df.sort_values(by=['votes', 'class_count', 'class_sum', 'top_class'],
                                                ascending=(False, False, True, True))
        ##如果排序后投票一二名 票数、行政级别之和、最高行政级别都相同，判定是问题件
        if supported_df.shape[0] == 0:  ###虽然有多个行政级别，但是没有相互支持的组合，且没有标准名称
            outcode = ['', '', '', '','']
        elif supported_df.shape[0] == 1:  ##只有一个组合
            outcode = list(supported_df.iloc[0][0:5])
        else:  ##多个组合选项选择
            if_chaos = sum(np.array(supported_df[['votes','class_count', 'class_sum', 'top_class']].iloc[0]) == np.array(
                supported_df[['votes','class_count', 'class_sum', 'top_class']].iloc[1]))  ###是否排序第一第二的投票一样
            if if_chaos == 4:  ##如果排序第一第二的组合投票一样造成混乱，无法选择(票数一样、级别数量一样、等级之和一样，最高等级一样)
                outcode = ['', '', '', '', '']
                for i in range(5):
                    if supported_df.iloc[0][i] == supported_df.iloc[1][i]:
                        outcode[i] = supported_df.iloc[0][i]
                    else:
                        break
            else:
                outcode = list(supported_df.iloc[0][0:5])


        ####寻找最小的唯一行政区划，此时最小的行政单位肯定与上级一致
        cutpoint_max = 0  ###寻找地址切分位置，四级行政区域 最靠后的位置，进行切分
        minclass_index = 0  ###寻找最小的行政级别
        i = 4
        while (i >= 0):
            if outcode[i] != '':
                if minclass_index < i:
                    minclass_index = i
                try:  ##原始匹配里面肯定有此级别行政单位
                    #print(rawcode[i + 1][outcode[i]])
                    for j in rawcode[i + 1][outcode[i]]:
                        cutpoint = [i.start() for i in re.finditer(j, addr)][-1] + len(j)
                        if cutpoint>cutpoint_max:
                            cutpoint_max=cutpoint
                    break
                except:  # 预防意外
                    pass
            else:
                pass
            i += -1
        ##取得截取后的剩余地址文本
        leftaddr=addr[cutpoint_max:]
        ###填充空白的上级行政单位
        if outcode != ['', '', '', '','']:
            #####填充,从最小行政级别开始遍历，空值，则进行填充。
            for i,j in enumerate([2,4,6,9,12]):
                if i<= minclass_index:
                    if outcode[i]=='':
                        ###填充空缺行政单位
                        outcode[i] = outcode[minclass_index][0:j]
                    ###赋予标准名称
                    out[i] = code_name_dict[outcode[i][0:2]][outcode[i]][0]
                else:
                    break

    finalout=out[0:4]
    finalout.append(out[4]+leftaddr)
    ##北京、上海、天津、重庆等直辖市，东莞、中山、儋州等地级市没有县区
    if finalout[0] in['北京市', '上海市', '天津市', '重庆市']:
        finalout[1] = finalout[0]
    if finalout[1] in ['东莞市', '中山市', '儋州市']:
        finalout[2] = finalout[3]
    return finalout


def get_category(addr):
    """
    提取商品类别标签
    :param addr: 输入地址
    :return: goods_cat_set: 商品类别集合
    """
    goods_cat_set=set()
    addr_kw_list=jieba_address_cut(addr)
    for kw in addr_kw_list:
        if kw.upper() in goods_category:
            for i in re.finditer(kw,addr):
                beftempindex=i.span()[0]-1   ###i.span()[0] 开始位置
                aftempindex = i.span()[1] ###i.span()[1]  结束位置后一位
                if (i.span()[0]==0) \
                        or (i.span()[0]>0 and addr[beftempindex] in stop_word_list) \
                        or (i.span()[0]>0 and addr[beftempindex] in ['个','只','支','张','盒','袋','组','套','箱','片','条','颗','粒','瓶','桶', '包','灌','0','1','2','3','4','5','6','7','8','9','一','二','两','三','四','五','六','七','八','九','十'])\
                        or (i.span()[1]==len(addr)) \
                        or (i.span()[1] < len(addr) and addr[aftempindex] in stop_word_list) \
                        or (i.span()[1]<len(addr) and  addr[aftempindex] in ['1','2','3','4','5','6','7','8','9','一','二','两','三','四','五','六','七','八','九','十'] ):
                    goods_cat_set.add(kw)
    return ','.join(goods_cat_set)


if __name__ == '__main__':
    print(standard4classaddress("武汉市沌口经济开发区郑州烩面江城大道538号"))


