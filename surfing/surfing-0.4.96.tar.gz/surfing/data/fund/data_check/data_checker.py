from pandas.tseries.offsets import DateOffset
import numpy as np
from ....util.config import SurfingConfigurator
from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi
from ...api.derived import DerivedDataApi
from ...api.research_api import ResearchApi
from ....util.wechat_bot import *


class DataChecker:

    def __init__(self):
        self.wechat_bot = WechatBot()
        self.wechat_hook = SurfingConfigurator().get_wechat_webhook_settings('wechat_webhook_data_check')
        self.reasearch_api = ResearchApi()

    def get_df_leq_value_index(self, df, index_id, value):
        tds = df[df <= value][index_id].dropna().index.tolist()
        tds = [str(i) for i in tds]
        return tds

    def get_df_le_value_index(self, df, index_id, value):
        tds = df[df < value][index_id].dropna().index.tolist()
        tds = [str(i) for i in tds]
        return tds

    def process_index_price(self):
        max_size = 15
        # 指数检查
        #    ■ 起始日至最新交易日（区分不同国家交易日），每个交易日数据是非空【part】缺少指数国别 和 不同国别交易日
        #    ■ 高开低收量额均为正数【ok】
        #    ■ 成交额介于“成交量最高价”和“成交量最低价”之间【ok】

        try:
            index_info = BasicDataApi().get_index_info()
            default_begin_date = datetime.date(1999,1,1)
            default_end_date = datetime.date.today()
            trade_date_list = BasicDataApi().get_trading_day_list(start_date=default_begin_date,end_date = default_end_date)
            trade_date_list = trade_date_list.datetime
            key_index_list = ['sse50','hs300','csi500','gem','star50','sp500rmb','national_debt','mmf']
            index_list = index_info.index_id.tolist()[:10] + key_index_list
            index_price = BasicDataApi().get_index_price(index_list)

            close_price = index_price.pivot_table(index='datetime',values='close',columns='index_id')
            open_price = index_price.pivot_table(index='datetime', values='open', columns='index_id')
            high_price = index_price.pivot_table(index='datetime', values='high', columns='index_id')
            low_price = index_price.pivot_table(index='datetime', values='low', columns='index_id')
            volume = index_price.pivot_table(index='datetime', values='volume', columns='index_id')
            amount = index_price.pivot_table(index='datetime', values='total_turnover', columns='index_id')

            index_dic = index_info.set_index('index_id')['desc_name'].to_dict()
            result = []
            for index_id in close_price:
                close_price_i = close_price[[index_id]].dropna()
                open_price_i = open_price[[index_id]].dropna()
                high_price_i = high_price[[index_id]].dropna()
                low_price_i = low_price[[index_id]].dropna()
                
                if index_id not in volume:
                    volume_i = pd.DataFrame(columns=[index_id])
                    volume_num = 0
                else:
                    volume_i = volume[[index_id]].dropna()
                    volume_num = volume_i.shape[0]
                
                if index_id not in amount:
                    amount_i = pd.DataFrame(columns=[index_id])
                    amount_num = 0
                else:
                    amount_i = amount[[index_id]].dropna()
                    amount_num = amount_i.shape[0]
                
                # 完整性
                b_d = close_price_i.index[0]
                e_d = close_price_i.index[-1]
                dts = trade_date_list[(trade_date_list >= b_d) & (trade_date_list <= e_d)]
                close_price_i_chg = close_price_i.reindex(dts)
                lack_data_trade_day = close_price_i_chg[pd.isna(close_price_i_chg)[index_id].values].index.tolist()
                lack_data_trade_day = [str(i) for i in lack_data_trade_day]
                
                # 非负
                close_negative_index = self.get_df_leq_value_index(close_price_i, index_id, 0)
                open_negative_index = self.get_df_leq_value_index(open_price_i, index_id, 0)
                high_negative_index = self.get_df_leq_value_index(high_price_i, index_id, 0)
                low_negative_index = self.get_df_leq_value_index(low_price_i, index_id, 0)
                volume_negative_index = self.get_df_le_value_index(volume_i, index_id, 0)
                amount_negative_index = self.get_df_le_value_index(amount_i, index_id, 0)
                
                # 成交额介于 成交量*最低价 成交量*最高价之前
                amount_check_df = index_price[index_price.index_id == index_id][['datetime','volume','low','high','total_turnover']].dropna()
                if amount_check_df.empty:
                    amount_check_reason = 'amount and volume data not complete'
                else:
                    amount_con1 = amount_check_df.total_turnover < (amount_check_df.low * amount_check_df.volume)
                    amount_con2 = amount_check_df.total_turnover > (amount_check_df.high * amount_check_df.volume)
                    amount_problem_date = amount_check_df[amount_con1 |  amount_con2].datetime.tolist()
                    amount_check_reason = f'problem amount and volume date lens {len(amount_problem_date)}'
                    #amount_check_reason = [str(i) for i in amount_problem_date]
                    #amount_check_reason = f'problem date: ' + ','.join(amount_check_reason)
                
                dic = {
                    'index_id':index_id,
                    'index_name':index_dic[index_id],
                    'lack_trade_date_lens':len(lack_data_trade_day),
                    #'lack_trade_date_list':lack_date_trade_day
                    'lack_other_price':f'close:{close_price_i.shape[0]}, open:{open_price_i.shape[0]}, high:{high_price_i.shape[0]},'
                                        +f' low:{low_price_i.shape[0]}, volume:{volume_num}, amount:{amount_num}',
                    'not_positive_index':f'close:{len(close_negative_index)} open:{len(open_negative_index)} high:{len(high_negative_index)} low:{len(low_negative_index)}'+
                                f'volume:{len(volume_negative_index)} amount:{len(amount_negative_index)}',
                    'amount_check_status':amount_check_reason,
                }
                result.append(dic)
            df = pd.DataFrame(result)

            # 分批发送
            bucket_size = int(df.shape[0] / max_size) + 1
            for i in range(bucket_size):
                idx_b = i * max_size
                idx_e = min((i + 1) * max_size - 1, df.shape[0])
                res = f'[指数检查 部分指数] part {i+1} \r'
                for r in df.loc[idx_b:idx_e].itertuples():
                    s = f'    [index_id] {r.index_id} [name] {r.index_name} [lack_trade_date_lens] {r.lack_trade_date_lens} [lack_other_price] {r.lack_other_price} not_positive_index {r.not_positive_index} [amount_check_status] {r.amount_check_status} \r'
                    res += s
                message = {
                    'msgtype': 'markdown',
                    'markdown': {
                        'content': res
                    }
                }
                res = requests.post(url=self.wechat_hook, data=json.dumps(message), timeout=20)

        except Exception as e:
                print(f'Failed to get data <err_msg> {e} from DataChecker.process_index_price')

    def process_fund_manager_info(self):
        # 公募基金经理信息
        #  ■ 公募基金运作的每一天，必须有明确的基金经理（团队）【ok】
        try:
            max_size = 20
            check_num = 500
            fund_info = BasicDataApi().get_fund_info().head(check_num)
            manager_info = DerivedDataApi().get_fund_manager_info(fund_list=fund_info.fund_id.tolist())
            default_begin_date = datetime.date(1999,1,1)
            default_end_date = datetime.date.today()
            trade_date_list = BasicDataApi().get_trading_day_list(start_date=default_begin_date,end_date = default_end_date)
            trade_date_list = trade_date_list.datetime
            result = []
            for r in fund_info.itertuples():
                manager_info_i = manager_info[manager_info.fund_id == r.fund_id]
                trade_date_list_i = trade_date_list[(trade_date_list >= r.start_date) & (trade_date_list <= r.end_date)]
                for r in manager_info_i.itertuples():
                    trade_date_list_i = trade_date_list_i[(trade_date_list_i<r.start_date) | (trade_date_list_i > r.end_date)]
                trade_date_list_i = trade_date_list_i.tolist()
                if len(trade_date_list_i) == 0:
                    continue
                else:
                    dic = {'fund_id':r.fund_id, 'desc_name':r.desc_name, 'wind_class_2':r.wind_class_2, 'lack_manager_date_lenth':len(trade_date_list_i)}
                result.append(dic)
            df = pd.DataFrame(result)
            # 分批发送
            bucket_size = int(df.shape[0] / max_size) + 1
            for i in range(bucket_size):
                idx_b = i * max_size
                idx_e = min((i + 1) * max_size - 1, df.shape[0])
                res = f'[基金经理数据检查] part {i+1} \r'
                for r in df.loc[idx_b:idx_e].itertuples():
                    s = f'    [fund_id] {r.fund_id} [name] {r.desc_name} [wind_class_2] {r.wind_class_2} [lack_manager_date_lenth] {r.lack_manager_date_lenth} \r'
                    res += s
                message = {
                    'msgtype': 'markdown',
                    'markdown': {
                        'content': res
                    }
                }
                res = requests.post(url=self.wechat_hook, data=json.dumps(message), timeout=20)
        except Exception as e:
                print(f'Failed to get data <err_msg> {e} from DataChecker.process_fund_manager_info')


    def process_pf_fund_nav(self):
        max_size = 25
        # 私募数据检查
        #   ■ 每只产品必须有策略一级和二级分类，必须有投资经理
        #   ■ 私募产品终止或者清算，终止日为None
        #   ■ 每只产品成立日至截止日之间

        try:
            research_api =  ResearchApi()
            stg_name_list = ['复合策略',
            '股票策略',
            '管理期货',
            '宏观策略',
            '其他策略',
            '事件驱动',
            '相对价值',
            '债券策略',
            '组合基金']
            # TODO 只检查部分代码
            pf_fund_info_problem = []
            for stg_name in stg_name_list:
                # 私募信息检查
                pf_fund_info = research_api.get_pf_info(stg_name=[stg_name]).head(100)
                _pf_fund_info = pf_fund_info[['RECORD_CD','SEC_FULL_NAME','MANAGER','INVEST_STRATEGY','INVEST_STRATEGY_CHILD','END_DATE','STATUS']]
                record_cds = _pf_fund_info.RECORD_CD.replace('',None).dropna().tolist()
                con1 = _pf_fund_info.STATUS.isin(['到期清算','延期清算','终止','提前清算'])
                con2 = _pf_fund_info.END_DATE.isnull()
                _pf_fund_info_res = _pf_fund_info[(_pf_fund_info.RECORD_CD == '') 
                            |(_pf_fund_info.SEC_FULL_NAME.isnull())
                            |(_pf_fund_info.SEC_FULL_NAME.str.len() <= 2)
                            |(_pf_fund_info.MANAGER.isnull())
                            |(_pf_fund_info.INVEST_STRATEGY_CHILD.isnull())
                            |(con1 & (con2))
                                                ]
                pf_fund_info_problem.append(_pf_fund_info_res.head(20))
                
                # 私募净值检查
                fund_nav = research_api.get_pf_nav(record_cds=record_cds)
                fund_nav = fund_nav.pivot_table(index='END_DATE',columns='RECORD_CD',values='ADJ_NAV')
                nav_not_correct = []
                for r in pf_fund_info.itertuples():
                    info_b_d = r.ESTABLISH_DATE
                    info_e_d = r.END_DATE
                    fund_id = r.RECORD_CD
                    if fund_id in fund_nav:
                        nav_dts = fund_nav[fund_id].dropna().index
                        nav_b_d = nav_dts[0]
                        nav_e_d = nav_dts[-1]
                        if (info_e_d is None and  info_b_d <= nav_b_d) or (info_b_d <= nav_b_d and info_e_d <= nav_e_d):
                            continue
                        else:
                            nav_not_correct_reason = f'[fund_id] {fund_id} [name] nav problem {r.SEC_FULL_NAME} [info_b_d] {info_b_d} [nav_b_d] {nav_b_d} [nav_e_d] {nav_e_d} [info_e_d] {info_e_d}  '
                    else:
                        nav_not_correct_reason = f'[fund_id] {fund_id} [name] {r.SEC_FULL_NAME} nav not exsited'
                    nav_not_correct.append(nav_not_correct_reason)
                break

            # 分批发送
            df = pd.concat(pf_fund_info_problem)
            bucket_size = int(df.shape[0] / max_size) + 1
            for i in range(bucket_size):
                idx_b = i * max_size
                idx_e = min((i + 1) * max_size - 1, df.shape[0])
                res = f'[私募信息检测 部分数据] part {i+1} \r'
                for r in df.loc[idx_b:idx_e].itertuples():
                    s = f'    [index_id] {r.RECORD_CD} [name] {r.SEC_FULL_NAME} [MANAGER] {r.MANAGER} [INVEST_STRATEGY] {r.INVEST_STRATEGY} INVEST_STRATEGY_CHILD {r.INVEST_STRATEGY_CHILD} [INVEST_STRATEGY_CHILD] {r.INVEST_STRATEGY_CHILD} [END_DATE] {r.END_DATE} [STATUS] {r.STATUS} \r'
                    res += s
                message = {
                    'msgtype': 'markdown',
                    'markdown': {
                        'content': res
                    }
                }
                res = requests.post(url=self.wechat_hook, data=json.dumps(message), timeout=20)

            # 分批发送
            l = nav_not_correct
            bucket_size = int(len(l) / max_size) + 1
            for i in range(bucket_size):
                idx_b = i * max_size
                idx_e = min((i+1) * max_size, len(l))
                res = f'[私募净值检测 部分数据] part {i+1} \r'
                print(idx_b,idx_e)
                for s in l[idx_b:idx_e]:
                    
                    s = f'{s} /r'
                    res += s
                message = {
                    'msgtype': 'markdown',
                    'markdown': {
                        'content': res
                    }
                }
                res = requests.post(url=self.wechat_hook, data=json.dumps(message), timeout=20)
        except Exception as e:
                print(f'Failed to get data <err_msg> {e} from DataChecker.process_fund_nav')


    def process_fund_nav(self):
        # 公募净值检查
        #    ■ 尚未清盘的公募基金，每个交易日均应非空，QDII、定开、建仓期基金除外
        #    ■ 单位净值、累计净值、复权净值均应大于0

        try:
            max_size = 15
            check_num = 1000
            fund_info = BasicDataApi().get_fund_info()
            fund_info = fund_info.head(check_num)
            fund_list = fund_info.fund_id.tolist()
            fund_open_info = BasicDataApi().get_fund_open_info()
            fund_open_list = fund_open_info.fund_id.tolist()

            fund_nav_ori = BasicDataApi().get_fund_nav(fund_list)
            fund_nav  = fund_nav_ori.pivot_table(index='datetime', columns='fund_id', values='adjusted_net_value')
            fund_unit_net_value = fund_nav_ori.pivot_table(index='datetime', columns='fund_id', values='unit_net_value')
            fund_acc_net_value = fund_nav_ori.pivot_table(index='datetime', columns='fund_id', values='acc_net_value')

            default_end_date = datetime.date(2040,12,31)
            last_date = fund_nav.index[-1]
            last_friday = (last_date
                - datetime.timedelta(days=last_date.weekday())
                + datetime.timedelta(days=4, weeks=-1))
            qdii_last_date = last_date - datetime.timedelta(days=1)

            res = []
            for r in fund_info.itertuples():
                info_end_date = r.end_date
                if r.fund_id not in fund_nav:
                    dic = {
                        'fund_id':r.fund_id,
                        'desc_name':r.desc_name,
                        'wind_class_2':r.wind_class_2,
                        'type':f'没有净值'
                    }
                    res.append(dic)
                    continue
                fund_nav_i = fund_nav[[r.fund_id]].dropna()
                fund_net_nav_i = fund_unit_net_value[[r.fund_id]].dropna()
                fund_acc_nav_i = fund_acc_net_value[[r.fund_id]].dropna()

                adj_nav_negative_index = self.get_df_leq_value_index(fund_nav_i, r.fund_id, 0)
                net_nav_negative_index = self.get_df_leq_value_index(fund_net_nav_i, r.fund_id, 0)
                acc_nav_negative_index = self.get_df_leq_value_index(fund_acc_nav_i, r.fund_id, 0)  
                not_positive_index = f'adj_nav:{len(adj_nav_negative_index)} net_nav:{len(net_nav_negative_index)} acc_nav:{len(acc_nav_negative_index)}'
                end_date = fund_nav[r.fund_id].dropna().index[-1]
                # 定开
                if r.fund_id in fund_open_list:
                    
                    if end_date >= last_friday:
                        continue
                    else:
                        dic = {
                            'fund_id':r.fund_id,
                            'desc_name':r.desc_name,
                            'wind_class_2':r.wind_class_2,
                            'type':f'定开基金 缺少最新净值 最后净值日 {end_date}',
                            'not_positive_index':not_positive_index,
                        }
                        res.append(dic)
                        continue
                # qdii
                if r.wind_class_2 in ['国际(QDII)股票型基金','国际(QDII)债券型基金']:
                    if end_date >= qdii_last_date:
                        continue
                    else:
                        dic = {
                            'fund_id':r.fund_id,
                            'desc_name':r.desc_name,
                            'wind_class_2':r.wind_class_2,
                            'type':f'qdii基金 缺少最新净值 最后净值日 {end_date}',
                            'not_positive_index':not_positive_index,
                        }
                        res.append(dic)
                        continue
                
                # 非终止基金    
                if info_end_date == default_end_date:
                    if end_date == last_date:
                        continue
                    else:
                        dic = {
                            'fund_id':r.fund_id,
                            'desc_name':r.desc_name,
                            'wind_class_2':r.wind_class_2,
                            'type':f'基金未终止 缺少最新净值 最后净值日 {end_date}',
                            'not_positive_index':not_positive_index,
                        }
                        res.append(dic)
                        continue
                # 终止基金
                else:
                    if (info_end_date - end_date).days > 7:
                        dic = {
                            'fund_id':r.fund_id,
                            'desc_name':r.desc_name,
                            'wind_class_2':r.wind_class_2,
                            'type':f'基金已终止 缺少净值 终止日 {info_end_date} 最后净值日 {end_date}',
                            'not_positive_index':not_positive_index,
                        }
                        res.append(dic)
                        continue
                    else:
                        continue
                
            df = pd.DataFrame(res)
            bucket_size = int(df.shape[0] / max_size) + 1
            for i in range(bucket_size):
                idx_b = i * max_size
                idx_e = min((i + 1) * max_size - 1, df.shape[0])
                res = f'[基金净值检验] part {i+1} 上一个交易日日期 {last_date}\r'
                for r in df.loc[idx_b:idx_e].itertuples():
                    s = f'    [fund_id]{r.fund_id} [name]{r.desc_name} [wind_class_2]{r.wind_class_2} [nav_reason]{r.type} [not_positive_index] {r.not_positive_index} \r'
                    res += s
                message = {
                    'msgtype': 'markdown',
                    'markdown': {
                        'content': res
                    }
                }
                res = requests.post(url=self.wechat_hook, data=json.dumps(message), timeout=20)

        except Exception as e:
                print(f'Failed to get data <err_msg> {e} from DataChecker.process_fund_nav')

    def process_fund_info(self):
        try:
            # 检查基金信息
            # ■ 公募产品运作的每一天，必须有一级分类标签（股票型、债券型、混合型、QDII、货币型）[part] [当前标签没有随着时间变动]
            max_size = 25
            fund_info = BasicDataApi().get_fund_info()
            fund_info = fund_info[['fund_id','desc_name','wind_class_1','wind_class_2']]
            df = fund_info[(fund_info.wind_class_2.isnull()) | (fund_info.wind_class_1.isnull())]
            # TODO 
            df = df.head(50).reset_index(drop=True)
            bucket_size = int(df.shape[0] / max_size) + 1
            for i in range(bucket_size):
                idx_b = i * max_size
                idx_e = min((i + 1) * max_size - 1, df.shape[0])
                res = f'[基金信息检验] part {i+1} \r'
                for r in df.loc[idx_b:idx_e].itertuples():
                    s = f'    [fund_id]{r.fund_id} [name]{r.desc_name} [wind_class_1]{r.wind_class_1} [wind_class_2]{r.wind_class_2} \r'
                    res += s
                message = {
                    'msgtype': 'markdown',
                    'markdown': {
                        'content': res
                    }
                }
                res = requests.post(url=self.wechat_hook, data=json.dumps(message), timeout=20)
        except Exception as e:
                print(f'Failed to get data <err_msg> {e} from DataChecker.process_fund_info')
            
    def _future_check_pre_settlement_price(self, data):
        # 前结算价
        df = data.dropna(how='any')
        df.index=df.datetime
        df.index = pd.to_datetime(df.index)
        cons = (df.pre_clear - df.clear.shift(1))
        cons = cons.dropna()
        thresh_hold = 0.11
        if len(cons[abs(cons)>thresh_hold]) > 0:
            df1 = df[1:].shift(1)[abs(cons)>thresh_hold]
            df1.index=(df1.index - datetime.timedelta(days=1)).tolist()
            cons_df = pd.concat([df1,df[1:][abs(cons)>thresh_hold]],axis=0)
            cons_df.set_index(keys='datetime',drop=True, inplace=True)
            cons_df = cons_df.sort_index()
            cons_df = cons_df.dropna()
        #             tag = {'em_id' : cons_df.em_id.values.tolist(),
        #                    'datetime':pd.Series(cons_df.index.values).apply(lambda x:x.strftime('%Y-%m-%d')).tolist(),
        #                    'pre_clear' : cons_df.pre_clear.values.tolist(),
        #                    'clear' : cons_df.clear.values.tolist()}
            tag = f'    [pre_settlement_price]  em_id : {cons_df.em_id.iloc[0]},days: {int(len(cons_df)/2)}'
            return tag

    def _future_check_average_price(self,data,multiplier):
        # 成交均价
        # multiplier 合约乘数
        df = data.dropna(how='any')
        df.index=df.datetime
        df.index = pd.to_datetime(df.index)
        avg = df.average_price.round(1) - (df.uni_amount/(df.uni_volume * multiplier)).round(1) 
        df = df.copy()
        df['average_price_par'] = (df.uni_amount/(df.uni_volume * multiplier)+np.exp(-8)).round(2)
        thresh_hold = 0.11
        if len(avg[abs(avg)>thresh_hold]) > 0:
            mean_df = df[abs(avg)>thresh_hold]
            #             tag = {'em_id' : mean_df.em_id.values.tolist(),
            #                    'datetime': pd.Series(mean_df.index.values).apply(lambda x:x.strftime('%Y-%m-%d')).tolist(),
            #                    'average_price' : mean_df.average_price.values.tolist(),
            #                    'average_price_par' : mean_df.average_price_par.values.tolist()}
            tag = f'    [average_price]  em_id : {mean_df.em_id.iloc[0]},days: {int(len(mean_df)/2)}'
            return tag

    def _future_check_spread(self,data,index_id,start_date,end_date):
        # 价差
        # index_id: csi500、hs300、sse50
        df = data.dropna(how='any')
        df.index=df.datetime
        df.index = pd.to_datetime(df.index)

        index_quote = self.reasearch_api.get_index_quote(start_date=start_date,
                                             end_date=end_date,
                                             index_ids=[index_id])
        index_quote = index_quote.pivot_table(index='datetime', columns='index_id',values='close')

        df1 = pd.merge(index_quote,df,left_index=True, right_index=True,how='inner')
        # 价差 = 收盘价 - 指数价格
        df1['spread_par'] = (df1.close - df1[index_id]).round(2)
        spr = df1.spread_par - df1.spread.round(2)

        if len(spr[abs(spr)>0.011]) > 0:
            f_df = df1[abs(spr)>0.011]
#             tag = {'em_id': f_df.em_id.values.tolist(),
#                    'datetime': pd.Series(f_df.index.values).apply(lambda x:x.strftime('%Y-%m-%d')).tolist(),
#                    'spread': f_df.spread.values.tolist(),
#                    'spread_par': f_df.spread_par.values.tolist(),
#                    'close': f_df.close.values.tolist(),
#                    'index_quote': f_df[index_id].values.tolist()}
            tag = f'    [spread]  em_id : {f_df.em_id.iloc[0]},days: {len(f_df)}'
            return tag

    def process_future_price(self):
        try:
            # 期货数据
            # ■ 每张合约在存续期每个交易日的行情数据是齐全的
            max_size = 30
            check_num = 20
            future_info = RawDataApi().get_em_future_info()
            today = datetime.date.today()
            tickers = future_info[future_info.deliver_date >= today].em_id.tolist()
            tickers = [i for i in tickers if 'CFE' not in tickers][:check_num]
            future_price = RawDataApi().get_em_future_price_detail(future_ids=tickers)
            close_price = future_price.pivot_table(index='datetime',columns='em_id',values='close')
            future_info = future_info[future_info.em_id.isin(tickers)]
            default_begin_date = datetime.date(1999,1,1)
            default_end_date = datetime.date.today()
            trade_date_list = BasicDataApi().get_trading_day_list(start_date=default_begin_date,end_date = default_end_date)
            trade_date_list = trade_date_list.datetime

            result = []
            result_str = []
            for r in future_info.itertuples():
                future_id = r.em_id
                start_date = r.start_trade_date
                end_date = r.deliver_date
                contract_mul = r.contract_mul
                close_i = close_price[[future_id]]
                trade_date_i = trade_date_list[trade_date_list>=start_date].tolist()
                df_i = close_i.reindex(trade_date_i)
                lack_quote_date = df_i[df_i.isnull()[future_id].values].shape[0]
                dic = {'future_id':future_id, 'name':r.desc_name, 'lack_quote_dates':lack_quote_date}
                result.append(dic)
                future_price_i = future_price[future_price.em_id == r.em_id]
                pre_settlement_result = self._future_check_pre_settlement_price(future_price_i)
                if pre_settlement_result:
                    result_str.append(pre_settlement_result)
                average_price = self._future_check_average_price(future_price_i, contract_mul)
                if average_price:
                    result_str.append(average_price)
                # TODO check cfe data
                # self._future_check_spread()          

            df = pd.DataFrame(result)
            # 分批发送 df
            bucket_size = int(df.shape[0] / max_size) + 1
            for i in range(bucket_size):
                idx_b = i * max_size
                idx_e = min((i + 1) * max_size - 1, df.shape[0])
                res = f'[期货数据检查] part {i+1} \r'
                for r in df.loc[idx_b:idx_e].itertuples():
                    s = f'    [future_id] {r.future_id} [name] {r.name} [lack_quote_dates] {r.lack_quote_dates} \r'
                    res += s
                message = {
                    'msgtype': 'markdown',
                    'markdown': {
                        'content': res
                    }
                }
                res = requests.post(url=self.wechat_hook, data=json.dumps(message), timeout=20)
            
            # 分批发送 str
            l = result_str
            bucket_size = int(len(l) / max_size) + 1
            for i in range(bucket_size):
                idx_b = i * max_size
                idx_e = min((i+1) * max_size, len(l))
                res = f'[期货数据价量检查 部分数据] part {i+1} \r'
                #print(idx_b,idx_e)
                for s in l[idx_b:idx_e]:
                    s = f'{s} /r'
                    res += s
                message = {
                    'msgtype': 'markdown',
                    'markdown': {
                        'content': res
                    }
                }
                res = requests.post(url=self.wechat_hook, data=json.dumps(message), timeout=20)
            

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from DataChecker.process_future_price')

    def process_stock_price(self):
        try:
            # 股票行情检查
            # ■ 每只股票在存续期的每个交易日，行情数据是齐全的，或者有停牌标志[没有停复牌信息]
            # ■ 主板股票在上市三个月之后，单日涨跌幅不应超过正负10%

            max_size = 25
            stock_info = RawDataApi().get_em_stock_info()
            default_begin_date = datetime.date(2000,1,1)
            default_end_date = datetime.date.today()
            trade_date_list = BasicDataApi().get_trading_day_list(start_date=default_begin_date,end_date = default_end_date)
            trade_date_list = trade_date_list.datetime
            con = [(i[0] in ['0','3', '6']) and (i[:2] != '68') and i[:3] != '300' for i in stock_info.stock_id]
            stock_info = stock_info[con]
            stock_list = stock_info.stock_id.tolist()
            stock_price = RawDataApi().get_em_stock_post_price(stock_list=stock_list,start_date=default_begin_date)
            stock_price = stock_price.pivot_table(index='datetime',values='close',columns='stock_id')
            result = []
            for r in stock_info.itertuples():
                list_start_date = r.list_date
                stock_id = r.stock_id
                delist_date = r.delist_date
                if delist_date is None:
                    pass
                else:
                    if delist_date <= default_begin_date:
                        continue
                normal_start_date = (list_start_date + DateOffset(months=3)).date()
                close_i = stock_price[[stock_id]]
                tds = trade_date_list[(trade_date_list >= list_start_date) & (trade_date_list<delist_date)]
                df_i = close_i.reindex(tds)
                lack_quote_date = df_i[df_i.isnull()[stock_id].values].shape[0]
                df_rets = df_i.loc[normal_start_date:][stock_id].pct_change().dropna()
                ret_abnormal_date = df_rets[(df_rets > 0.1) & (df_rets < -0.1)].shape[0]
                if lack_quote_date == 0 and ret_abnormal_date == 0:
                    continue
                dic = {
                    'stock_id': stock_id,
                    'name':r.name,
                    'lack_quote_date':lack_quote_date,
                    'ret_abnormal_date':ret_abnormal_date,
                }
                result.append(dic)
            df = pd.DataFrame(result)
            if df.empty:
                message = {
                    'msgtype': 'markdown',
                    'markdown': {
                        'content': f'[股票价格数据正常 ]'
                    }
                }
                res = requests.post(url=self.wechat_hook, data=json.dumps(message), timeout=20)
            else:
                # 分批发送
                bucket_size = int(df.shape[0] / max_size) + 1
                for i in range(bucket_size):
                    idx_b = i * max_size
                    idx_e = min((i + 1) * max_size - 1, df.shape[0])
                    res = f'[股票价格] part {i+1} \r'
                    for r in df.loc[idx_b:idx_e].itertuples():
                        s = f'    [stock_id] {r.stock_id} [name] {r.name} [lack_quote_date_len] {r.lack_quote_date} [ret_abnormal_date_len] {r.ret_abnormal_date} \r'
                        res += s
                    message = {
                        'msgtype': 'markdown',
                        'markdown': {
                            'content': res
                        }
                    }
                    res = requests.post(url=self.wechat_hook, data=json.dumps(message), timeout=20)
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from DataChecker.process_stock_price')

    def process_stock_industry(self):
        try:
            # 每只股票在每一天属于哪个申万/中信一级/二级/三级行业应是齐全的
            check_num = 50
            max_size = 25
            stock_info = RawDataApi().get_em_stock_info()
            stock_info = stock_info[['stock_id','name','citic_code_2020','bl_sws_ind_code']]
            con = [(i.stock_id[0] in ['0','3', '6']) and (i.name[:2] != 'PT') for i in stock_info.itertuples()]
            stock_info = stock_info[con]
            stock_info = stock_info[stock_info.citic_code_2020.isnull() | stock_info.bl_sws_ind_code.isnull()]
            df = stock_info.head(check_num).reset_index(drop=True)

            # 分批发送
            bucket_size = int(df.shape[0] / max_size) + 1
            for i in range(bucket_size):
                idx_b = i * max_size
                idx_e = min((i + 1) * max_size - 1, df.shape[0])
                res = f'[股票行业检查] part {i+1} \r'
                if idx_b == idx_e:
                    continue
                for r in df.loc[idx_b:idx_e].itertuples():
                    s = f'    [stock_id] {r.stock_id} [name] {r.name} [中信行业分类] {r.citic_code_2020} [申万行业分类] {r.bl_sws_ind_code} \r'
                    res += s
                message = {
                    'msgtype': 'markdown',
                    'markdown': {
                        'content': res
                    }
                }
                res = requests.post(url=self.wechat_hook, data=json.dumps(message), timeout=20)
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from DataChecker.process_stock_industry')

    def process(self):
        self.process_fund_nav()
        self.process_fund_manager_info()
        self.process_pf_fund_nav()
        self.process_fund_info()
        self.process_index_price()
        self.process_future_price()
        self.process_stock_price()
        self.process_stock_industry()
