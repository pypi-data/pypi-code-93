import pandas as pd
import numpy as np
import json
from .fund_info_filter import EHR_PROBLEM_EKYWORDS

def fund_tag(base_fund_id:str,  #基金母基金代码 非母基金是0
             desc_name:str,     #基金中文简称
             is_open:int,       #是否是开放式基金  1表示开放 0 表示定期开放
             currency:str,      #交易货币类型
             wind_class_2:str,  #wind二级分类
             benchmark_s_raw:str,    #basic.fund_benchmark.benchmark_s_raw
             fund_id:str,       #fund_id
):
    
    '''
    删除基金逻辑
    '''

    # 1.只选择非分级基金
    ## wind 基金信息数据里 基金母基金代码 如果如果base_fund_id 为0表示 非分级基金， 
    ##                               如果base_fund_id 和 基金代码一致，表示是分级基金母基金
    ##                               如果不一致，可以通过desc_name区分 A类分级或者B类分级
    if base_fund_id != 0:
        return None

    # 2.只选择非ETF基金,可以选择ETF联接
    _desc_name = desc_name.replace('ETF联接','')
    if 'ETF' in _desc_name:
        return None

    # 3.只选择开放式基金 不选择定期开放式基金
    if is_open != 1:
        return None

    # 4.只选择人民币交易的基金
    if currency != 'CNY':
        return None

    # 5.去掉基金份额 E类 H类 R类
    ## E类 指定代销机构对基金
    ## H类 基金场内上市份额
    ## R类 对特定投资群体进行发售，特定群体指基本养老保险基金，企业年金计划筹集的资金等

    for type_word, problem_words in EHR_PROBLEM_EKYWORDS.items():
        for problem_i in problem_words:
            _desc_name = desc_name.replace(problem_i, '')
        if type_word in _desc_name:
            return None

    # 6.国债里不包含短债 短融 双债 短期纯债
    debt_black_list = ['超短债','短融','双债']
    for i in debt_black_list:
        if i in desc_name:
            return None
    if wind_class_2 == '短期纯债型基金':
        return None

    '''
    分类逻辑 分类计数在不考虑删除逻辑统计
    '''
    # 1. 沪深300  141 只 hs300 000300.SH
    ## 第一基准是hs300 即权重大于50%
    ## wind 二级投资分类 在 【'增强指数型基金','被动指数型基金'】 不包含 【‘普通股票型基金’,'偏股混合型基金'】
    ## 【'增强指数型基金','被动指数型基金'】 里hs300权重最低 0.9
    hs300_w = json.loads(benchmark_s_raw).get('hs300',0)
    if hs300_w > 0.5 and wind_class_2 in ['增强指数型基金','被动指数型基金']:
        return 'hs300'

    # 2. 中证500 104只 csi500 000905.SH
    ## 第一基准是csi500 即权重大于50%
    ## wind 二级投资分类 在 【'增强指数型基金','被动指数型基金'】 不包含 【‘普通股票型基金’,'偏股混合型基金'】
    ## 【'增强指数型基金','被动指数型基金'】 里hs300权重最低 0.95
    csi500_w = json.loads(benchmark_s_raw).get('csi500',0)
    if csi500_w > 0.5 and wind_class_2 in ['增强指数型基金','被动指数型基金']:
        return 'csi500'

    # 3. 创业板 57 只 gem 
    ## 创业板基金少，考虑所有创业板相关基准
    ## 399295.SZ	cnext_lowv_bc   创业蓝筹     
    ## 399606.SZ	cnext_mome_gr   创业板R      
    ## 399296.SZ	cnext_r         创成长       
    ## 399102.SZ	gei             创业板综指   
    ## 399673.SZ	gem             创业板50    
    ## 399006.SZ	gem_50          创业板指    
    ## 只选 ['增强指数型基金','被动指数型基金']

    gem_list = ['cnext_lowv_bc','cnext_mome_gr','cnext_r','gei','gem','gem_50']
    con1 = False
    for gem_id in gem_list:
        w = json.loads(benchmark_s_raw).get(gem_id,0)
        if w > 0.5:
            con1 = True
            continue
    con2 = wind_class_2 in ['增强指数型基金','被动指数型基金']
    if con1 and con2:
        return 'gem'

    # 4. 标普500 8只 sp500rmb
    ## 第一基准是标普
    sp500rmb_w = json.loads(benchmark_s_raw).get('sp500rmb',0)
    if sp500rmb_w > 0.5 and wind_class_2 in ['增强指数型基金','被动指数型基金']:
        return 'sp500rmb'

    # 5. 国债 2129 只 national_debt
    ## 选取第一基准不是行业债 金融债的 
    ## cba_10ytfp_all              中债10年期国债全价(总值)指数
    ## cba_10y_future              中债10年期国债期货期限匹配金融债全价(总值)指数
    ## cba_130                     中债1-30年利率债财富(1-3年)指数
    ## cba_139qi                   中债-1-3年久期央企20债券财富(总值)指数
    ## cba_5y_future               中债5年期国债期货期限匹配金融债全价(总值)指数
    ## cba_a_fp_1_3y               中债总全价(1-3年)指数
    ## cba_a_fp_all                中债总全价(总值)指数
    ## cba_a_tr_1_3y               中债总财富(1-3年)指数
    ## cba_a_tr_all                中债总财富(总值)指数
    ## cba_crefp_all               中债信用债总全价(总值)指数
    ## cba_cretr_1y                中债信用债总财富(1年以下)指数
    ## cba_cretr_1_3y              中债信用债总财富(1-3年)指数
    ## cba_cretr_3_5y              中债信用债总财富(3-5年)指数
    ## cba_cretr_all               中债信用债总财富(总值)指数
    ## cba_c_fp_1y                 中债综合全价(1年以下)指数
    ## cba_c_fp_1_3y               中债综合全价(3-5年)指数
    ## cba_c_fp_all                中债综合全价(总值)指数
    ## cba_c_tr_1y                 中债综合财富(1年以下)指数
    ## cba_c_tr_1_3y               中债综合财富(1-3年)指数
    ## cba_c_tr_all                中债综合财富(总值)指数
    ## cba_e_fp_all                中债企业债总全价(总值)指数
    ## cba_f_fp_1_3y               中债金融债券总全价(总值)指数
    ## cba_f_tr_all                中债金融债券总财富(总值)指数
    ## cba_hg_fp_1_3y              中债高信用等级债券财富(1-3年)指数
    ## cba_hg_fp_all               中债高信用等级债券全价(总值)指数
    ## cba_hg_tr_all               中债高信用等级债券财富(总值)指数
    ## cba_nc_fp_1y                中债新综合全价(1年以下)指数
    ## cba_nc_fp_1_3y              中债新综合全价(1-3年)指数
    ## cba_nc_fp_all               中债新综合全价(总值)指数
    ## cba_nc_tr_1_3y              中债新综合财富(1-3年)指数
    ## cba_nc_tr_all               中债新综合财富(总值)指数
    ## cba_sm_1_3y                 中债中短期债券财富(1-3年)指数
    ## cba_t_tr_1_3y               中债国债总财富(1-3年)指数
    ## cba_t_tr_3_5y               中债国债总财富(3-5年)指数
    ## cba_t_tr_5_10y              中债国债总财富(7-10年)指数
    ## cba_t_tr_all                中债国债总财富(总值)指数
    ## cni_tpbb                    国证利率
    ## cni_tpbb5                   国证利率1-5
    ## csi_10ytb                   中证10年国债
    ## csi_5ydcdb                  5年久期国开债
    ## csi_cib_mh_b                中证兴业中高信用债
    ## csi_compb                   中证综合债
    ## csi_hcityz                  沪城投债
    ## csi_medcomz                 中期企债
    ## csi_meddnb                  中期国债
    ## csi_nationb                 中证国债
    ## csi_patb                    中证平安5-10年国债
    ## csi_pbb                     政金债
    ## csi_pbb10                   政金债8-10
    ## csi_pbb3                    政金债1-3
    ## csi_pbb5                    政金债3-5
    ## csi_pbb8                    政金债5-8
    ## csi_wholeb                  中证全债
    ## national_debt_index         国债指数
    ## see_3_5y_creb               沪质中高债3-5
    ## sse_nationb5                5年国债
    ## sz_national_10y             10年期国债
    ## tmd_1y                      一年期定期存款利率
    ## tmd_2y                      两年期定期存款利率
    ## tmd_3m                      三个月定期存款利率
    ## tmd_3y                      三年期定期存款利率
    ## tmd_6m                      六个月定期存款利率
    ## tmd_7d                      七天通知存款利率

    ## 选择wind 二级分类 ['被动指数型债券基金','中长期纯债型基金']

    national_index_list = ['cba_10ytfp_all',
                            'cba_10y_future',
                            'cba_130',
                            'cba_139qi',
                            'cba_5y_future',
                            'cba_a_fp_1_3y',
                            'cba_a_fp_all',
                            'cba_a_tr_1_3y',
                            'cba_a_tr_all',
                            'cba_crefp_all',
                            'cba_cretr_1y',
                            'cba_cretr_1_3y',
                            'cba_cretr_3_5y',
                            'cba_cretr_all',
                            'cba_c_fp_1y',
                            'cba_c_fp_1_3y',
                            'cba_c_fp_all',
                            'cba_c_tr_1y',
                            'cba_c_tr_1_3y',
                            'cba_c_tr_all',
                            'cba_e_fp_all',
                            'cba_f_fp_1_3y',
                            'cba_f_tr_all',
                            'cba_hg_fp_1_3y',
                            'cba_hg_fp_all',
                            'cba_hg_tr_all',
                            'cba_nc_fp_1y',
                            'cba_nc_fp_1_3y',
                            'cba_nc_fp_all',
                            'cba_nc_tr_1_3y',
                            'cba_nc_tr_all',
                            'cba_sm_1_3y',
                            'cba_t_tr_1_3y',
                            'cba_t_tr_3_5y',
                            'cba_t_tr_5_10y',
                            'cba_t_tr_all',
                            'cni_tpbb',
                            'cni_tpbb5',
                            'csi_10ytb',
                            'csi_5ydcdb',
                            'csi_cib_mh_b',
                            'csi_compb',
                            'csi_hcityz',
                            'csi_medcomz',
                            'csi_meddnb',
                            'csi_nationb',
                            'csi_patb',
                            'csi_pbb',
                            'csi_pbb10',
                            'csi_pbb3',
                            'csi_pbb5',
                            'csi_pbb8',
                            'csi_wholeb',
                            'national_debt_index',
                            'see_3_5y_creb',
                            'sse_nationb5',
                            'sz_national_10y',
                            'tmd_1y',
                            'tmd_2y',
                            'tmd_3m',
                            'tmd_3y',
                            'tmd_6m',
                            'tmd_7d']   
    national_bench = json.loads(benchmark_s_raw)
    index_list = []
    for index_id, w in national_bench.items():
        if w >= 0.5:
            index_list.append(index_id)
    con1 = False
    for i in national_index_list:
        if i in index_list:
            con1 = True
            break
    con2 = wind_class_2 in ['被动指数型债券基金','中长期纯债型基金']
    if con1 and con2:
        return 'national_debt'
    
    # 6. 货基
    ## 在wind 一级分类下选择 货币市场型基金, 然后在2020年6月30截面上，选择规模最大的前200只
    
    mmf_list = ['000198!0',
                '040038!0',
                '050003!0',
                '000359!0',
                '003515!0',
                '000397!0',
                '003474!0',
                '004501!0',
                '000380!0',
                '000379!0',
                '000693!0',
                '000719!0',
                '001666!0',
                '001211!0',
                '000575!0',
                '000343!0',
                '002758!0',
                '511990!0',
                '000848!0',
                '482002!0',
                '000607!0',
                '003753!0',
                '001134!0',
                '003164!0',
                '000917!0',
                '000638!0',
                '001529!0',
                '000569!0',
                '511880!0',
                '000621!0',
                '200003!0',
                '000330!0',
                '37001B!0',
                '004137!0',
                '004776!0',
                '000662!0',
                '000581!0',
                '000539!0',
                '000559!0',
                '000759!0',
                '180008!0',
                '003536!0',
                '004417!0',
                '004771!0',
                '004545!0',
                '004217!0',
                '003281!0',
                '001821!0',
                '000907!0',
                '004199!0',
                '003480!0',
                '161608!0',
                '003679!0',
                '090022!0',
                '519517!0',
                '519510!0',
                '003871!0',
                '000602!0',
                '161623!0',
                '003003!0',
                '000677!0',
                '000509!0',
                '003483!0',
                '001094!0',
                '675062!0',
                '270047!0',
                '000600!0',
                '005202!0',
                '000891!0',
                '001374!0',
                '000710!0',
                '003022!0',
                '471030!0',
                '000905!0',
                '380011!0',
                '002183!0',
                '110016!0',
                '003043!0',
                '003423!0',
                '004449!0',
                '001982!0',
                '150005!0',
                '519999!0',
                '000618!0',
                '000686!0',
                '000908!0',
                '310339!0',
                '004201!0',
                '150998!0',
                '000725!0',
                '000816!0',
                '003465!0',
                '001391!0',
                '000505!0',
                '001077!0',
                '000010!0',
                '000464!0',
                '000540!0',
                '003034!0',
                '001893!0',
                '003206!0',
                '202308!0',
                '004717!0',
                '511660!0',
                '202302!0',
                '000588!0',
                '000797!0',
                '000716!0',
                '000665!0',
                '002260!0',
                '000371!0',
                '000332!0',
                '110051!0',
                '000599!0',
                '003042!0',
                '000009!0',
                '004039!0',
                '004896!0',
                '000895!0',
                '002847!0',
                '002894!0',
                '000874!0',
                '000627!0',
                '005065!0',
                '070088!0',
                '001234!0',
                '003712!0',
                '240006!0',
                '004373!0',
                '002324!0',
                '004811!0',
                '004097!0',
                '000699!0',
                '000709!0',
                '100028!0',
                '001871!0',
                '004568!0',
                '620011!0',
                '288201!0',
                '000920!0',
                '519506!0',
                '001058!0',
                '000543!0',
                '002673!0',
                '005135!0',
                '541011!0',
                '000301!0',
                '070008!0',
                '000605!0',
                '000830!0',
                '000495!0',
                '380008!0',
                '004970!0',
                '002195!0',
                '217004!0',
                '000855!0',
                '003229!0',
                '004904!0',
                '004839!0',
                '000707!0',
                '003473!0',
                '001931!0',
                '004972!0',
                '000533!0',
                '000773!0',
                '008733!0',
                '000846!0',
                '000872!0',
                '000704!0',
                '091023!0',
                '004841!0',
                '530029!0',
                '000424!0',
                '004056!0',
                '519889!0',
                '460006!0',
                '210013!0',
                '003875!0',
                '000730!0',
                '005057!0',
                '000860!0',
                '260102!0',
                '001478!0',
                '000912!0',
                '000645!0',
                '519717!0',
                '000135!0',
                '003969!0',
                '202301!0',
                '004170!0',
                '360019!0',
                '070036!0',
                '400006!0',
                '003535!0',
                '001621!0',
                '001308!0',
                '000952!0',
                '270014!0',
                '000037!0',
                '000687!0']

                    
    if fund_id in mmf_list:
        return 'mmf'

    # 7. gold 
    if '黄金' in desc_name:
        return 'gold' 
    return None