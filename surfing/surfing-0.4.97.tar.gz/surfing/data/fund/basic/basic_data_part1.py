
import datetime
import traceback
import json
import re

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple, Union, Set

from ....constant import SectorType, IndexPriceSource
from ....constant import INDEX_PRICE_EXTRA_TRADE_DAYS, FUND_NAV_EXTRA_TRADE_DAYS, QUARTER_UPDATE_DATE_LIST, SEMI_UPDATE_DATE_LIST
from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi
from ...view.basic_models import *
from ...manager.fund_tag_update import fund_tag
from ..raw.raw_data_helper import RawDataHelper
from .basic_data_helper import BasicDataHelper


class BasicDataPart1:

    def __init__(self, data_helper: BasicDataHelper):
        self._data_helper = data_helper
        self._raw_data_api = RawDataApi()
        self._basic_data_api = BasicDataApi()
        self._index_info_df = self._basic_data_api.get_index_info()
        self._fund_info_df = self._basic_data_api.get_fund_info()

    def _status_mapping(self, x):
        if x == 'Open':
            return 0
        elif x == 'Suspended':
            return 1
        elif x == 'Limited':
            return 2
        elif x == 'Close':
            return 3
        else:
            return None

    def _find_tag(self, symbol, wind_class_II):
        if '沪深300' in symbol and wind_class_II in ['普通股票型基金', '增强指数型基金', '被动指数型基金']:
            return 'A股大盘'
        elif '中证500' in symbol and wind_class_II in ['普通股票型基金', '增强指数型基金', '被动指数型基金']:
            return 'A股中盘'
        elif '标普500' in symbol:
            return '美股大盘'
        elif '创业板' in symbol and wind_class_II in ['普通股票型基金', '增强指数型基金', '被动指数型基金']:
            return '创业板'
        elif '德国' in symbol:
            return '德国大盘'
        elif '日本' in symbol or '日经' in symbol:
            return '日本大盘'
        elif (('国债' in symbol or '利率' in symbol or '金融债' in symbol)
              and wind_class_II in ['短期纯债型基金', '中长期纯债型基金', '被动指数型债券基金']):
            return '利率债'
        elif (('信用' in symbol or '企债' in symbol or '企业债' in symbol)
              and wind_class_II in ['短期纯债型基金', '中长期纯债型基金', '被动指数型债券基金']):
            return '信用债'
        elif '黄金' in symbol:
            return '黄金'
        elif '原油' in symbol or '石油' in symbol or '油气' in symbol:
            return '原油'
        elif ('地产' in symbol or '金融' in symbol) and ('美国'not in symbol):
            return '房地产'
        else:
            return 'null'

    def fund_info(self):
        # Update manually
        # Not verified
        track_index_df = pd.read_csv('./data/fund_track_index.csv', index_col=0)
        wind_fund_info = self._raw_data_api.get_wind_fund_info()
        fund_fee = self._raw_data_api.get_fund_fee()
        wind_fund_info['order_book_id'] = [_.split('!')[0].split('.')[0] for _ in wind_fund_info['wind_id'] ]
        res = []
        for i in wind_fund_info['wind_id']:
            if not '!' in i:
                res.append(0)
            else:
                res_i = int(i.split('!')[1].split('.')[0])
                res.append(res_i)
        wind_fund_info['transition'] = res
        wind_fund_info['fund_id'] = [o + '!' + str(t) for o, t in zip(wind_fund_info['order_book_id'], wind_fund_info['transition'])]
        wind_fund_info = wind_fund_info.set_index('fund_id')
        fund_fee = fund_fee.drop(['id','desc_name'], axis = 1).set_index('fund_id')
        wind_fund_info = wind_fund_info.join(fund_fee)
        wind_fund_info['fund_id'] = wind_fund_info.index
        wind_fund_info['asset_type'] = [self._find_tag(symbol, wind_class_II) for symbol, wind_class_II in zip(wind_fund_info['desc_name'],wind_fund_info['wind_class_2'])]
        wind_fund_info = wind_fund_info[[i.split('.')[1] == 'OF' for i in wind_fund_info['wind_id']]]
        wind_fund_info = wind_fund_info.set_index('wind_id')
        dic = {k:v for k,v in zip(self._index_info_df['desc_name'], self._index_info_df['index_id'])}
        wind_fund_info = wind_fund_info.join(track_index_df[['track_index']])
        wind_fund_info['wind_id'] = wind_fund_info.index
        wind_fund_info['track_index'] = wind_fund_info['track_index'].map(lambda x: dic.get(x,'none'))
        self._data_helper._upload_basic(wind_fund_info, FundInfo.__table__.name)

    def fund_info_from_raw(self, fund_id_list: Set[str]):
        def _invest_type_class_to_wind_class_1(x: pd.Series) -> str:
            if x.invest_type_class_1 == '其他基金':
                if 'QDII' in x.desc_name:
                    return '国际(QDII)基金'
            return x.invest_type_class_1

        def _invest_type_class_to_wind_class_2(x: pd.Series) -> str:
            '''Choice的基金二级类型转换为wind的'''

            if x.invest_type_class_2 == '混合债券型基金（一级）':
                return '混合债券型一级基金'
            elif x.invest_type_class_2 == '长期纯债型基金':
                return '中长期纯债型基金'
            elif x.invest_type_class_2 == '中短期纯债型基金':
                return '短期纯债型基金'
            elif x.invest_type_class_2 == '混合债券型基金（二级）':
                return '混合债券型二级基金'
            elif x.invest_type_class_1 == '债券型基金' and x.invest_type_class_2 == '被动指数型基金':
                return '被动指数型债券基金'
            elif x.invest_type_class_2 == 'QDII基金':
                if x.invest_type_class_1 == '债券型基金':
                    return '国际(QDII)债券型基金'
                elif x.invest_type_class_1 == '股票型基金':
                    return '国际(QDII)股票型基金'
                elif x.invest_type_class_1 == '混合型基金':
                    return '国际(QDII)混合型基金'
                # error case
                return
            elif x.invest_type_class_2 in ('封闭式基金', '保本型基金'):
                # error case
                return
            else:
                return x.invest_type_class_2

        def _lambda_structure_type(x: pd.Series) -> int:
            if x.base_fund_id is None:
                return 0
            if x.base_fund_id == x.wind_id:
                return 1
            # 到这里应该必然是分级基金，所以直接判断A,B即可
            elif 'A' in x.desc_name:
                return 2
            elif 'B' in x.desc_name:
                return 3
            else:
                # 分级基金A,B份额可能名字里不带A,B，之后需要手工修改下
                return 4

        def _lambda_index_id_new(x: pd.Series, benchmark: pd.DataFrame) -> Optional[str]:
            try:
                return fund_tag(x.base_fund_id, x.desc_name, x.is_open, x.currency, x.wind_class_2, benchmark.at[x.wind_id, 'benchmark_s_raw'], x.fund_id)
            except KeyError:
                print(f'{x.fund_id} no benchmark info')
                return

        def _lambda_fund_manager(x: str) -> pd.Series:
            manager_list: List[str] = x.split(',')
            return pd.Series(['\r\n'.join(manager_list), re.sub(r'\(.*\)$', '', manager_list[0])])

        def _lambda_benchmark(x: str) -> pd.Series:
            def _parse_index(part: str):
                if '×' in part:
                    es = part.split('×')
                elif '*' in part:
                    es = part.split('*')
                elif '╳' in part:
                    es = part.split('╳')
                else:
                    return part

                if '%' in es[0]:
                    return es[1]
                else:
                    return es[0]

            if x is None:
                return
            benchmarks: List[str] = str(x).split('+')
            if len(benchmarks) == 1:
                second = None
            else:
                second = _parse_index(benchmarks[1])
            return pd.Series([_parse_index(benchmarks[0]), second])

        def _lambda_fee(x: str, em_fund_fee: pd.DataFrame) -> pd.Series:
            def _parse_fee(fee: str):
                if fee is None:
                    return
                cheapest_fee = fee.split(';')[0]
                es = cheapest_fee.split(':')
                if len(es) > 1:
                    value = es[1]
                else:
                    value = es[0]
                if value[-1] == '%':
                    value = float(value[:-1]) / 100
                else:
                    try:
                        value = float(value) / 100
                    except ValueError:
                        return
                return value

            try:
                fee = em_fund_fee.loc[x, ['manage_fee', 'trustee_fee', 'purchase_fee', 'redeem_fee']]
            except KeyError:
                return pd.Series()
            else:
                return fee.transform(_parse_fee)

        benchmark = RawDataApi().get_em_fund_benchmark()
        if benchmark is None:
            return
        benchmark = benchmark[benchmark.em_id.isin(fund_id_list)]
        benchmark = benchmark.sort_values(by=['em_id', 'datetime']).drop_duplicates(subset='em_id', keep='last')
        benchmark = benchmark.set_index('em_id')
        # 获取raw中的基金基础信息
        df = RawDataApi().get_em_fund_info(fund_id_list).drop(columns='_update_time')
        if df is None:
            return
        # 其中一部分列可以直接使用，改一下名字即可
        df = df.rename(columns={'em_id': 'wind_id', 'name': 'desc_name', 'manager_id': 'pre_fund_manager'})
        # is open
        df['is_open'] = 1
        key_words = ['封闭', '定期', '定开']
        key_words = '|'.join(key_words)
        _wind_ids = df[df['desc_name'].str.contains(key_words)].wind_id
        df = df.set_index('wind_id')
        df.loc[_wind_ids, 'is_open'] = 0
        df = df.reset_index()
        # 没有end_date的话给一个默认值
        df['end_date'] = df['end_date'].where(df.end_date.notna(), '2040-12-31')
        df['currency'] = df.currency.map({'人民币元': 'CNY', '美元': 'USD', '港元': 'HKD', '港币': 'HKD'})
        # 基金经理
        df[['manager_id', 'fund_manager']] = df.pre_fund_manager.apply(_lambda_fund_manager)
        # 新基金都是!0，这里需要检查是否有相同order_book_id的旧基金
        df['order_book_id'] = df.wind_id.transform(lambda x: x.split('.')[0])
        df['transition'] = 0
        df['fund_id'] = df.order_book_id.transform(lambda x: x + '!0')
        # Choice的基金一二级分类转换为wind的
        df['wind_class_1'] = df[['desc_name', 'invest_type_class_1']].apply(_invest_type_class_to_wind_class_1, axis=1)
        df['wind_class_2'] = df[['invest_type_class_1', 'invest_type_class_2']].apply(_invest_type_class_to_wind_class_2, axis=1)
        df['asset_type'] = df.apply(lambda x: self._find_tag(x.desc_name, x.wind_class_2), axis=1)
        df['structure_type'] = df.apply(_lambda_structure_type, axis=1)
        df['is_etf'] = df.desc_name.transform(lambda x: 1 if ('ETF' in x and '联接' not in x) else 0)
        fund_benchmark = self._basic_data_api.get_fund_benchmark(fund_id_list).set_index('em_id')
        df['index_id_new'] = df.apply(_lambda_index_id_new, axis=1, benchmark=fund_benchmark)
        em_fund_fee = self._raw_data_api.get_em_fund_fee(fund_id_list).drop(columns='_update_time').set_index('em_id')
        df[['manage_fee', 'trustee_fee', 'purchase_fee', 'redeem_fee']] = df.wind_id.apply(_lambda_fee, em_fund_fee=em_fund_fee)
        df = df.set_index('wind_id').join(em_fund_fee[['subscr_fee', 'purchase_fee', 'redeem_fee', 'service_fee']].rename(columns={'subscr_fee': 'subscr_fee_detail', 'purchase_fee': 'purchase_fee_detail', 'redeem_fee': 'redeem_fee_detail'}))
        df['benchmark'] = benchmark.benchmark
        # 拆解上边的benchmark
        df[['benchmark_1', 'benchmark_2']] = df.benchmark.apply(_lambda_benchmark)
        df = df.drop(columns=['invest_type_class_1', 'invest_type_class_2']).reset_index()
        # 将场内变为场外的
        df['wind_id'] = df.wind_id.transform(lambda x: x.split('.')[0] + '.OF' if '.OF' not in x else x)
        BasicDataApi().delete_fund_info(df.fund_id.to_list())
        self._data_helper._upload_basic(df, FundInfo.__table__.name)

    def index_info(self):
        # Update manually
        # Not verified
        df = pd.read_csv('./data/index_info.csv')
        self._data_helper._upload_basic(df, IndexInfo.__table__.name)

    def index_info_from_raw(self, index_list: Union[Tuple[str], List[str]], index_ids: List[str]):
        assert len(index_list) == len(index_ids), 'index list length should match the ids'

        df = self._raw_data_api.get_em_index_info(index_list).drop(columns=['name', 'publish_date', '_update_time'])
        assert df.shape[0] == len(index_ids), 'index info length should match the ids'
        df = df.rename(columns={'short_name': 'desc_name'})
        # 先全体置为false，后续可以手工修改
        df['is_select'] = False
        df['is_stock_factor_universe'] = False
        df['tag_method'] = 'PE百分位'
        # index_id是人工起的，所以只能作为参数传进来
        df = df.set_index('em_id').reindex(index_list)
        df['index_id'] = index_ids
        df = df.reset_index().set_index('index_id')
        if 'csi_new_ev' in df.index:
            df.loc['csi_new_ev','desc_name'] = '中证新能源汽车'
        if 'csi_biomedi' in df.index:
            df.loc['csi_biomedi','desc_name'] = '中证生物医药'
        if 'csi_cssw_elec' in df.index:
            df.loc['csi_cssw_elec','desc_name'] = '中证申万电子'
        if 'csi_computer' in df.index:
            df.loc['csi_computer','desc_name'] = '中证计算机'
        if 'csi_food_beve' in df.index:
            df.loc['csi_food_beve','desc_name'] = '中证食品饮料'
        df = df.reset_index()
        self._data_helper._upload_basic(df, IndexInfo.__table__.name)

    def index_component(self):
        def _lambda_func_index_component_2(em_id_to_index_id: Dict[str, str], x: str):
            info = json.loads(x)
            r = []
            for one in info:
                em_id = one[0]
                if em_id in ['000915.SH', '000916.SH']:
                    em_id = em_id.split('.')[0] + '.CSI'
                r.append((em_id_to_index_id[em_id], one[1]))
            return json.dumps(r)

        def _lambda_func_index_component_3(wind_id_to_id: Dict[str, str], x: str):
            if x is None:
                return x
            r = []
            info = json.loads(x)
            for one in info:
                try:
                    r.append(wind_id_to_id[one + '.OF'])
                except KeyError:
                    r.append(one + '!0')
            return json.dumps(r)

        index_info_df = self._index_info_df[self._index_info_df.em_id.notna()]
        index_info_df = index_info_df.set_index('em_id')
        em_id_to_index_id: Dict[str, str] = index_info_df['index_id'].to_dict()

        df = self._raw_data_api.get_cs_index_component().drop(columns=['_update_time'])
        df['index_id'] = df['index_id'].map(em_id_to_index_id)
        df['sector'] = df['sector'].transform(lambda x: _lambda_func_index_component_2(em_id_to_index_id, x))
        fund_info_df = self._fund_info_df.set_index('wind_id')
        wind_id_to_id: Dict[str, str] = fund_info_df['fund_id'].to_dict()
        df['related_funds'] = df['related_funds'].transform(lambda x: _lambda_func_index_component_3(wind_id_to_id, x))
        self._data_helper._upload_basic(df, IndexComponent.__table__.name)

    def fund_nav_from_rq(self, start_date, end_date):
        df = self._raw_data_api.get_rq_fund_nav(start_date, end_date)
        df['fund_id'] = df.apply(
            lambda x: self._data_helper._get_fund_id_from_order_book_id(x['order_book_id'], x['datetime']), axis=1)
        df['subscribe_status'] = df['subscribe_status'].map(self._status_mapping)
        df['redeem_status'] = df['redeem_status'].map(self._status_mapping)
        df = df[df['fund_id'].notna()]
        self._data_helper._upload_basic(df, FundNav.__table__.name)

    def fund_nav(self, start_date, end_date, fund_list: Tuple[str] = ()):
        try:
            raw_start_date_dt: datetime.date = pd.to_datetime(start_date, infer_datetime_format=True).date()
            end_date = pd.to_datetime(end_date, infer_datetime_format=True).date()

            # 多取N个交易日的数据
            start_date = raw_start_date_dt - datetime.timedelta(days=40)
            trading_day_df = BasicDataApi().get_trading_day_list(start_date, end_date)
            trading_day_df = trading_day_df[trading_day_df.datetime <= raw_start_date_dt]
            assert trading_day_df.datetime.size >= FUND_NAV_EXTRA_TRADE_DAYS, f'should at least have {FUND_NAV_EXTRA_TRADE_DAYS} trading days'
            # del_date在start_date后边一天，确保可以正确计算ret等daily difference
            start_date = trading_day_df.datetime.array[-FUND_NAV_EXTRA_TRADE_DAYS]
            del_date = trading_day_df.datetime.array[-(FUND_NAV_EXTRA_TRADE_DAYS-1)]
            print(f'[fund_nav] (start_date){start_date} (del_date){del_date} (end_date){end_date}')

            # start_date = start_date.strftime('%Y%m%d')
            df = self._raw_data_api.get_em_fund_nav(start_date, end_date, fund_ids=fund_list).drop(columns='_update_time')
            df['fund_id'] = df.apply(
                lambda x: self._data_helper._get_fund_id_from_order_book_id(x['CODES'].split('.')[0], x['DATES']), axis=1)
            df = df.drop(['CODES'], axis=1)
            df = df[df['fund_id'].notna()]
            df = df.rename(columns={
                    'DATES': 'datetime',
                    'ORIGINALUNIT': 'unit_net_value',
                    'ORIGINALNAVACCUM': 'acc_net_value',
                    'ADJUSTEDNAV': 'adjusted_net_value',
                    'UNITYIELD10K': 'daily_profit',
                    'YIELDOF7DAYS': 'weekly_yield'
                })
            df['weekly_yield'] = df['weekly_yield'].map(lambda x: x / 100.0 if not pd.isnull(x) else x)

            anv_df = df.pivot_table(index='datetime', columns='fund_id', values='adjusted_net_value').fillna(method='ffill')
            df = df.set_index(['datetime', 'fund_id'])
            df['change_rate'] = (anv_df / anv_df.shift(1) - 1).stack()

            df = df[df.index.get_level_values(level='datetime').date >= del_date]
            df = df.reset_index()
            # TODO: 最好应该原子提交下边两步
            BasicDataApi().delete_fund_nav(del_date, end_date, df.fund_id.to_list())
            self._data_helper._upload_basic(df, FundNav.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def fund_benchmark(self, end_date: str = '', is_history=True):
        def _parse_raw_benchmark(x: str):
            if '×' in x:
                x.split('x')
            elif '*' in x:
                x.split('*')

        raw_fund_bc = RawDataApi().get_em_fund_benchmark(end_date)
        now_fund_bc = BasicDataApi().get_fund_benchmark()
        to_insert = set(raw_fund_bc.em_id.array) - set(now_fund_bc.em_id.array)
        if not to_insert and is_history:
            return
        if is_history:
            raw_fund_bc = raw_fund_bc[raw_fund_bc.em_id.isin(to_insert)]
            df = raw_fund_bc.set_index('em_id').benchmark.transform(_parse_raw_benchmark)
        else:
            pass
        self._data_helper._upload_basic(df, FundBenchmark.__table__.name)

    def fund_benchmark_parser(self, file_path: str):
        from sympy import simplify

        _CHAR_TO_BE_REPLACED = {
            ' ': '',
            '*+': '+',
            '×*': '*',
            '╳': '*',
            'X': '*',
            '%8': '%',
            '×': '*',
            '本基金的业绩比较基准为:': '',
            '互联网+': '互联网PLUS',
            'AA+': 'AAPLUS',
            'DJ-AIGCommodity': 'DJAIGCommodity',
            '500信息技术': '中证500信息技术',
            '180治理': '上证180治理',
            'A-H50': 'AH50',
            '中债-综合财富': '中债综合财富',
            '中债-综合全价': '中债综合全价',
            '中债-综合指数': '中债综合指数',
            '中债-广西壮族自治区': '中债广西壮族自治区',
            '中债-总财富': '中债总财富',
            '中债-总全价': '中债总全价',
            '中债-新综合财富': '中债新综合财富',
            '中债-农发行': '中债农发行',
            '中债-安徽省': '中债安徽省',
            '中债-信用债': '中债信用债',
            '中债-国债及政策性银行债': '中债国债及政策性银行债',
            '中债-湖北省': '中债湖北省',
            '中债-金融债券总全价': '中债金融债券总全价',
            '中债-新中期票据': '中债新中期票据',
            '中债-市场隐含评级': '中债市场隐含评级',
            '道琼斯-美国国际集团': '道琼斯美国国际集团',
            '-0-3年': '零至三年',
            '-0-2年': '零至二年',
            '-0-5年': '零至五年',
            '-1-3年': '一至三年',
            '-1-5年': '一至五年',
            '-3-5年': '三至五年',
            '-5-10年': '五至十年',
            '-7-10年': '七至十年',
            '1-3年': '一至三年',
            '1-7年': '一至七年',
            '0-1年': '零至一年',
            '0-3年': '零至三年',
            '0-4年': '零至四年',
            '3-5年': '三至五年',
            '5-10年': '五至十年',
            '5-8年': '五至八年',
            '8-10年': '八至十年',
            '-5年': '五年',
            '-10年': '十年',
            '1三年': '三年',
            '7天': '七天',
            '3个月': '三个月',
            '6个月': '六个月',
            '1年': '一年',
            '2年': '二年',
            '3年': '三年',
            '4.0': '',
            '(税后)': '',
        }
        _CHAR_TO_BE_REPLACED_BY_RE = {
            r'[\[\];:”,\x7f]': r'',
            r'x(\d+\%)': r'*\1',
            r'\n.*': r'',
            r'^年化收益率|固定业绩基准(\d+\%)$': r'\1',
            r'^(\d+\%)\/年$': r'\1',
            r'[\(\（][^\-\+]*?[\)\）]': r'',
            r'A[uU]\d+\.\d+': r'',
            r'(\d+\%)的': r'\1*',
            r'^(.+?)[\*\×]?(\d+\%)\+(.+?)[\*\×]?(\d+\%)$': r'\1*\2+\3*\4',
            r'^(.+?)[\*\×]?(\d+\%)\+(.+?)[\*\×]?(\d+\%)\+(.+?)[\*\×]?(\d+\%)$': r'\1*\2+\3*\4+\5*\6',
            r'^(\d+\%)[\*\×]?(.+)\+(\d+\%)[\*\×]?(.+)$': r'\1*\2+\3*\4',
            r'^(\d+\%)[\*\×]?(.+)\+(\d+\%)[\*\×]?(.+)\+(\d+\%)[\*\×]?(.+)$': r'\1*\2+\3*\4+\5*\6',
            r'\%': r'/100',
        }

        def _parse_raw_benchmark(x: pd.Series):
            r = {}
            if pd.isnull(x.BENCHMARK):
                # print(x)
                return json.dumps({'-1': -1})

            normalized = x.BENCHMARK
            normalized = normalized.lstrip('0')
            for k, v in _CHAR_TO_BE_REPLACED.items():
                normalized = normalized.replace(k, v)
            for k, v in _CHAR_TO_BE_REPLACED_BY_RE.items():
                normalized = re.sub(k, v, normalized)

            try:
                # print(x.name, normalized, x.BENCHMARK)
                normalized = str(simplify(normalized).evalf(strict=True))
            except Exception as e:
                if '+' in normalized:
                    if 'X' not in x.BENCHMARK and 'I' not in x.BENCHMARK and 'S' not in x.BENCHMARK and '下滑曲线值' not in x.BENCHMARK:
                        print(f'x {normalized} {x.BENCHMARK} {e}')
                    return json.dumps({'-1': -1})
            parts = normalized.split('+')
            for i in range(len(parts)):
                try:
                    value = x.at[f'BMINDEXCODE_{i+1}']
                except KeyError:
                    print(f'1 {normalized}')
                else:
                    if pd.isnull(value):
                        try:
                            r['1'] = float(parts[i])
                            continue
                        except Exception:
                            if '银行活期存款利率' in parts[i] or '银行活期存款税后收益率' in parts[i]:
                                value = 'RA0000.IR'
                            elif '利差' not in x.BENCHMARK and x.name not in ('000988.OF', '000989.OF', '000990.OF', '006585.OF', '007272.OF', '007976.OF', '007977.OF', '007978.OF',
                                                                            '008142.OF', '008143.OF', '008701.OF', '008702.OF', '009198.OF', '159812.OF', '161116.OF', '164701.OF',
                                                                            '202101.OF', '253010.OF', '518660.OF', '518850.OF'):
                                print(f'2 {x.name} {i+1} {normalized} {x.BENCHMARK}')
                                continue
                    value_parts = parts[i].split('*')
                    if len(value_parts) not in (1, 2):
                        if len(value_parts) == 3:
                            for one in value_parts:
                                if '汇率' in one:
                                    value_parts.remove(one)
                                    break
                            else:
                                if 'X' not in x.BENCHMARK and '下滑曲线值' not in x.BENCHMARK and 'A%' not in x.BENCHMARK and 'B%' not in x.BENCHMARK:
                                    print(f'4 {normalized} {x.BENCHMARK}')
                                continue
                        else:
                            if 'X' not in normalized and '人民币/港币汇率' not in x.BENCHMARK:
                                print(f'3 {normalized} {x.BENCHMARK}')
                            continue

                    if len(value_parts) == 1:
                        r[value] = 1
                    else:
                        try:
                            if '活期存款' in value_parts[0] or '七天通知存款' in value_parts[0] or '一年期定期' in value_parts[0] or '一年期银行定期' in value_parts[0] or '六个月银行定期' in value_parts[0]:
                                r[value] = 1
                            else:
                                r[value] = float(value_parts[0])
                        except Exception:
                            if 'm' not in x.BENCHMARK and 'n' not in x.BENCHMARK and 'I' not in x.BENCHMARK and '人民币/港币汇率' not in x.BENCHMARK:
                                print(x.name, x.BENCHMARK, normalized, value_parts)
            return json.dumps({k: v for k, v in zip(r.keys(), sorted(r.values(), reverse=True))})

        df = pd.read_csv(file_path, header=0, index_col=0)
        r = df.apply(_parse_raw_benchmark, axis=1)
        return df, r

    def recalc_all_funds_benchmark(self, path: str):
        def replaced_with_index_id(x):
            if not pd.isnull(x.benchmark):
                replaced = {}
                b = json.loads(x.benchmark)
                for k, v in b.items():
                    if k == '1':
                        replaced[k] = v
                    else:
                        try:
                            replaced[em_id_to_index_id[k.upper()]] = v
                        except KeyError:
                            if '-1' not in replaced:
                                replaced['-1'] = v
                            else:
                                replaced['-1'] += v
                return json.dumps(replaced)

        r = self.fund_benchmark_parser(path)
        all_funds_benchmark = pd.concat([r[0].CODES.rename('em_id'), r[0].BENCHMARK.rename('index_text'), r[1].rename('benchmark')], axis=1)
        index_info = BasicDataApi().get_index_info()
        em_id_to_index_id = index_info.set_index('em_id')['index_id'].to_dict()
        all_funds_benchmark['benchmark_s_raw'] = all_funds_benchmark.apply(replaced_with_index_id, axis=1)
        now_fund_benchmark = BasicDataApi().get_fund_benchmark()
        whole_funds_benchmark = all_funds_benchmark.join(now_fund_benchmark.set_index('em_id')[['assets', 'industry']], on='em_id', how='left')
        whole_funds_benchmark['benchmark_s'] = whole_funds_benchmark.benchmark_s_raw
        whole_funds_benchmark['fund_id'] = whole_funds_benchmark.apply(lambda x: x.em_id.split('.')[0] + '!0', axis=1)
        # return whole_funds_benchmark
        # TODO asset and industry
        BasicDataApi().delete_fund_benchmark(whole_funds_benchmark.em_id.to_list())
        BasicDataHelper()._upload_basic(whole_funds_benchmark, FundBenchmark.__table__.name)

    def index_price(self, start_date, end_date):
        try:
            raw_start_date_dt: datetime.date = pd.to_datetime(start_date, infer_datetime_format=True).date()
            # 多取N个交易日的数据
            start_date = raw_start_date_dt - datetime.timedelta(days=90)
            trading_day_df = BasicDataApi().get_trading_day_list(start_date.strftime('%Y%m%d'), end_date)
            trading_day_df = trading_day_df[trading_day_df.datetime <= raw_start_date_dt]
            assert trading_day_df.datetime.size >= INDEX_PRICE_EXTRA_TRADE_DAYS, f'should at least have {INDEX_PRICE_EXTRA_TRADE_DAYS} trading days'
            # del_date在start_date后边一天，确保可以正确计算ret等daily difference
            start_date = trading_day_df.datetime.array[-INDEX_PRICE_EXTRA_TRADE_DAYS]
            del_date = trading_day_df.datetime.array[-(INDEX_PRICE_EXTRA_TRADE_DAYS-1)]
            print(f'[index_price] (start_date){start_date} (del_date){del_date} (end_date){end_date}')
            # 准备多个数据源
            cm_index_price = self._raw_data_api.get_raw_cm_index_price_df(start_date, end_date).drop(columns=['_update_time']).set_index('datetime').fillna(method='ffill')
            cxindex_index_price = self._raw_data_api.get_cxindex_index_price_df(start_date, end_date).drop(columns=['_update_time'])
            yahoo_index_price = self._raw_data_api.get_yahoo_index_price_df(start_date, end_date).drop(columns=['_update_time'])
            index_info_df = self._index_info_df[self._index_info_df.price_source == IndexPriceSource.default]
            em_id_list: Dict[str, str] = index_info_df[['em_id', 'index_id']].dropna().set_index('em_id').to_dict()['index_id']
            # 这几个指数需要从yahoo下载数据 因为每日更新时choice还没有数据
            for index in ('DJIA.GI', 'FTSE.GI', 'IXIC.GI'):
                try:
                    del em_id_list[index]
                except KeyError:
                    pass
            em_index_price = self._raw_data_api.get_em_index_price(start_date, end_date, em_id_list.keys()).drop(columns=['_update_time'])
            em_index_price = em_index_price.rename(columns={'amount': 'total_turnover'})
            df_list = []
            # 处理Choice数据
            index_id_list = []
            for em_id, index_id in em_id_list.items():
                df = em_index_price[em_index_price['em_id'] == em_id]
                df = df.drop(columns=['em_id'])
                df['index_id'] = index_id
                df['ret'] = df.close / df.close.shift(1) - 1
                df = df[df.datetime >= pd.to_datetime(del_date).date()]
                df_list.append(df)
                if not df.empty:
                    index_id_list.append(index_id)
                # if em_id == 'SPX.GI':
                #     df['index_id'] = 'sp500'
                #     df_list.append(df.copy())
                #     if not df.empty:
                #         index_id_list.append('sp500')

                #     df = df.set_index('datetime').join(cm_index_price[['usd_central_parity_rate']])
                #     df['index_id'] = 'sp500rmb'
                #     df['open'] *= df['usd_central_parity_rate']
                #     df['close'] *= df['usd_central_parity_rate']
                #     df['low'] *= df['usd_central_parity_rate']
                #     df['high'] *= df['usd_central_parity_rate']
                #     df['ret'] = df.close / df.close.shift(1) - 1
                #     df = df.copy().reset_index().drop('usd_central_parity_rate', axis=1)
                #     df_list.append(df.copy())
                #     if not df.empty:
                #         index_id_list.append('sp500rmb')
                # else:
                #     df_list.append(df)
                #     if not df.empty:
                #         index_id_list.append(index_id)

            start_date_dt: datetime.date = pd.to_datetime(del_date, infer_datetime_format=True).date()
            end_date_dt: datetime.date = pd.to_datetime(end_date, infer_datetime_format=True).date()
            index_list = ['sp500']  #, 'dax30', 'n225']
            cm_index_list = ['sp500rmb']  #, 'dax30rmb', 'n225rmb']
            for i, c in zip(index_list, cm_index_list):
                df = yahoo_index_price[yahoo_index_price['index_id'] == i]
                df = df.set_index('datetime').reindex(cm_index_price.index).fillna(method='ffill')
                # 存进去人民币计价的数据
                df = df[['close', 'open', 'low', 'high', 'volume']]
                df['close'] *= cm_index_price['usd_central_parity_rate']
                df['open'] *= cm_index_price['usd_central_parity_rate']
                df['low'] *= cm_index_price['usd_central_parity_rate']
                df['high'] *= cm_index_price['usd_central_parity_rate']
                df['index_id'] = c
                df['ret'] = df.close / df.close.shift(1) - 1
                df = df.loc[start_date_dt:end_date_dt, :]
                df = df.reset_index()
                df_list.append(df)
                if not df.empty:
                    index_id_list.append(c)

            cx_index_df = cxindex_index_price[cxindex_index_price.datetime.between(start_date_dt, end_date_dt)]
            df_list.append(cx_index_df)
            if not cx_index_df.empty:
                index_id_list.extend(list(cx_index_df.index_id.unique()))

            # 存进去美元计价的数据
            yahoo_index_price = yahoo_index_price[yahoo_index_price.index_id != 'n225']

            # yahoo下载的指数名字与我们自己的指数名字做一下转换
            naming_dict = {
                'ftse100': 'gi_ftse100',
                'ixic': 'nasdaq'
            }
            yahoo_index_price['index_id'] = yahoo_index_price.index_id.map(lambda x: naming_dict[x] if x in naming_dict else x)
            yahoo_index_df = yahoo_index_price[yahoo_index_price.datetime.between(start_date_dt, end_date_dt)]
            df_list.append(yahoo_index_df)
            if not yahoo_index_df.empty:
                index_id_list.extend((yahoo_index_df.index_id.unique()))

            df = pd.concat(df_list, ignore_index=True)
            # TODO: 改成原子提交下边两个操作
            BasicDataApi().delete_index_price(index_id_list, del_date, end_date)
            self._data_helper._upload_basic(df.replace([np.Inf, -np.Inf], np.nan), IndexPrice.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def fund_rating_latest(self):
        try:
            fund_rating_df = self._raw_data_api.get_fund_rating()
            fund_info = self._fund_info_df[['fund_id', 'order_book_id', 'start_date', 'end_date']]
            score_name = ['zs', 'sh3', 'sh5', 'jajx']
            score_dic = {}
            for s in score_name:
                score_df = fund_rating_df[['order_book_id', 'datetime', s]]
                datelist = sorted(list(set(score_df.dropna().datetime.tolist())))
                score_dic[s] = datelist[-1]
            res = []
            for s, d in score_dic.items():
                try:
                    df = fund_rating_df[['order_book_id', 'datetime', s]]
                    df = df[df['datetime'] == d]
                    con1 = fund_info['start_date'] <= d
                    con2 = fund_info['end_date'] >= d
                    fund_info_i = fund_info[con1 & con2]
                    dic = {row['order_book_id']: row['fund_id']
                        for index, row in fund_info_i.iterrows()}
                    df['fund_id'] = df['order_book_id'].map(lambda x: dic[x])
                    df = df[['fund_id', s]].copy().set_index('fund_id')
                    res.append(df)
                except Exception as e:
                    print(e)
            df = pd.concat(res, axis=1, sort=False)
            df['fund_id'] = df.index
            df['update_time'] = datetime.date.today()
            self._data_helper._upload_basic(df, FundRatingLatest.__table__.name, to_truncate=True)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def rq_stock_price(self, start_date, end_date):
        try:
            stock_price_df = self._raw_data_api.get_rq_stock_price(start_date, end_date)
            stock_post_price_df = self._raw_data_api.get_rq_stock_post_price(start_date, end_date)

            stock_post_price_df['adj_close'] = stock_post_price_df['close']
            stock_post_price_df = stock_post_price_df.filter(items=['adj_close', 'datetime', 'order_book_id'],
                axis='columns')

            stock_price_merge_df = stock_price_df.merge(stock_post_price_df, how='left', on=['datetime', 'order_book_id'])
            stock_price_merge_df['post_adj_factor'] = stock_price_merge_df['adj_close'] / stock_price_merge_df['close']
            stock_price_merge_df = stock_price_merge_df.rename(columns={'order_book_id': 'stock_id'})
            self._data_helper._upload_basic(stock_price_merge_df, StockPrice.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def rq_fund_ret(self, start_date, end_date):
        try:
            column_rename_dict = {
                'sharp_ratio': 'sharpe_ratio',
                'last_week_return': 'w1_ret',
                'last_month_return': 'm1_ret',
                'last_three_month_return': 'm3_ret',
                'last_six_month_return': 'm6_ret',
                'last_twelve_month_return': 'y1_ret',
                'max_drop_down': 'mdd',
                'annualized_returns': 'annual_ret',
                'average_size': 'avg_size',
                'information_ratio': 'info_ratio',
                'to_date_return':'to_date_ret'
            }
            column_drop_list = ['order_book_id', 'year_to_date_return', 'annualized_risk']

            df = self._raw_data_api.get_rq_fund_indicator(start_date, end_date)
            df['fund_id'] = df.apply(
                lambda x: self._data_helper._get_fund_id_from_order_book_id(x['order_book_id'], x['datetime']), axis=1)
            df = df.rename(columns=column_rename_dict).drop(columns=column_drop_list)
            df = df[df['fund_id'].notnull()]

            self._data_helper._upload_basic(df, FundRet.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def stock_info(self):
        try:
            df = self._raw_data_api.get_stock_info()
            self._data_helper._upload_basic(df, StockInfo.__table__.name, to_truncate=True)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def sector_info(self):
        try:
            df = pd.read_csv('./data/sector_info.csv', index_col=0)
            df['sector_type'] = df['sector_type'].map({'industry': SectorType.industry.name, 'topic': SectorType.topic.name})
            self._data_helper._upload_basic(df, SectorInfo.__table__.name, to_truncate=True) 
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def sector_funds(self, dm):
        def _lambda_sector_funds_1(em_id_map: Dict[str, str], x: str):
            try:
                return em_id_map[x]
            except KeyError:
                return x

        try:
            index_info_df = self._index_info_df[self._index_info_df.em_id.notna()]
            index_info_df = index_info_df.set_index('em_id')
            em_id_list: List[str] = index_info_df.index.to_list()
            em_id_to_index_id: Dict[str, str] = index_info_df['index_id'].to_dict()

            df = pd.read_csv('./data/sector_funds.csv', index_col=0)
            df['csi_index_id'] = df['csi_index_id'].transform(lambda x: _lambda_sector_funds_1({em_id.split('.')[0]: em_id for em_id in em_id_list if em_id is not None}, x))
            df['index_id'] = df['csi_index_id'].map(em_id_to_index_id)
            sector_funds = BasicDataApi().get_sector_index_info()
            fund_score = dm.dts.fund_indicator_score
            sector_funds = sector_funds.dropna(subset=['fund_id'])
            sector_list = df.sector_id.tolist()
            sector_dic = {}
            for sector_id in sector_list:
                fund_list = sector_funds[sector_funds.sector_id == sector_id].fund_id.tolist()
                top_fund = fund_score.loc[fund_score.index.intersection(fund_list)].sort_values('total_score', ascending=False)#
                if top_fund.empty:
                    continue
                top_fund = top_fund.index[0]
                sector_dic[sector_id] = top_fund
            df.loc[:,'main_fund_id'] = df.sector_id.map(lambda x : sector_dic.get(x, None))
            self._data_helper._upload_basic(df, SectorFunds.__table__.name, to_truncate=True)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False
        '''
        人工添加 板块对应基金
        思路1: 东财基金对应概念， 加入有未插入的同概念基金， 如果基金涵盖类别少，手动增加 index_id， 如果类别下基金繁杂，比如材料（涉及钢铁 煤炭 金属 有色 水泥）
        思路2: 未找到东财基金对应概念，查看板块涉及的指数，找关键字，在基金名称里查找 
        文件 surfing/rpm/etc/sector_info_extend.txt
        '''

    def fund_size(self, start_date, end_date):
        try:
            # Since fund_size in basic db is latest snapshot, we only use end_date as param
            df = self._raw_data_api.get_em_fund_scale(end_date=end_date)
            if df is None:
                print('failed to get em fund scale for fund size')
                return False
            # 将场内变为场外的
            df['CODES'] = df.CODES.transform(lambda x: x.split('.')[0] + '.OF' if '.OF' not in x else x)
            df = df.pivot_table(index='DATES', columns='CODES', values='FUNDSCALE').fillna(method='ffill')
            df = df.iloc[[-1], :].apply(lambda x: pd.Series({'fund_id': self._data_helper._get_fund_id_from_order_book_id(x.name.split('.')[0], x.index.array[0]), 'latest_size': float(x.array[0])})).T
            df = df.reset_index(drop=True)
            df = df[df.notnull().all(axis=1)]
            self._data_helper._upload_basic(df, FundSize.__table__.name, to_truncate=True)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def fund_status_latest(self, end_date: str):
        try:
            df: Optional[pd.DataFrame] = self._raw_data_api.get_em_fund_status(end_date=end_date).drop(columns='_update_time')
            if df is None:
                print('failed to get em fund scale for fund status latest')
                return False
            # 将场内变为场外的
            df['CODES'] = df.CODES.transform(lambda x: x.split('.')[0] + '.OF' if '.OF' not in x else x)
            df = df.sort_values(by=['DATES', 'CODES']).drop_duplicates(subset=['CODES'], keep='last')
            # pivot on all remaining columns
            df = df.pivot(index='DATES', columns='CODES').ffill()
            df = df.iloc[[-1], :].stack().reset_index()
            df['fund_id'] = df[['DATES', 'CODES']].apply(lambda x: self._data_helper._get_fund_id_from_order_book_id(x.CODES.split('.')[0], x.DATES), axis=1)
            df = df[df.fund_id.notna()]
            df = df.drop(columns=['DATES', 'CODES']).rename(columns=lambda x: FundStatusLatest.__getattribute__(FundStatusLatest, x).name)
            self._data_helper._upload_basic(df, FundStatusLatest.__table__.name, to_truncate=True)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def fund_rate(self, end_date):
        def _count_star_history(x):
            color_change = {
                '红':'蓝',
                '蓝':'白',
                '白':'红',
            }
            if x is None:
                return None
            if '星' in x:
                return str(x.count('★') + x.count('☆') + 1) + color_change[x[-2]]
            else:
                return str(x.count('★') + x.count('☆'))

        def _count_A_rating(x: Optional[str]) -> Optional[str]:
            if x is None:
                return
            return str(x.count('A'))

        def _count_star_recent(x):
            if x is None:
                return None
            if '星' in x:
                return str(x.count('★') + x.count('☆') + 1) + x[-2]
            else:
                return str(x.count('★') + x.count('☆'))
        try:
            df = self._raw_data_api.get_em_fund_rate(end_date)
            df['fund_id'] = df.apply( lambda x : self._data_helper._get_fund_id_from_order_book_id(x.CODES.split('.')[0], x.DATES), axis=1)
            no_star_columns = ['CODES','DATES','_update_time','fund_id']
            A_rate_columns = ['TXCOMRATRAT']
            for col in df:
                if col in no_star_columns:
                    continue
                if col in A_rate_columns:
                    df[col] = df[col].map(_count_A_rating)
                else:
                    df[col] = df[col].map(lambda x: _count_star_recent(x))
            df = df.drop(['CODES','_update_time'], axis=1)
            name_dic = {
                'DATES':'datetime',
                'MKTCOMPRE3YRAT':'mkt_3y_comp',
                'MORNSTAR3YRAT':'mornstar_3y',
                'MORNSTAR5YRAT':'mornstar_5y',
                'MERCHANTS3YRAT':'merchant_3y',
                'TXCOMRATRAT':'tx_comp',
                'SHSTOCKSTAR3YCOMRAT':'sh_3y_comp',
                'SHSTOCKSTAR3YSTOCKRAT':'sh_3y_stock',
                'SHSTOCKSTAR3YTIMERAT':'sh_3y_timeret',
                'SHSTOCKSTAR3YSHARPERAT':'sh_3y_sharpe',
                'SHSTOCKSTAR5YCOMRATRAT':'sh_5y_comp',
                'SHSTOCKSTAR5YSTOCKRAT':'sh_5y_stock',
                'SHSTOCKSTAR5YTIMERAT':'sh_5y_timeret',
                'SHSTOCKSTAR5YSHARPRAT':'sh_5y_sharpe',
                'JAJXCOMRAT':'jian_comp',
                'JAJXEARNINGPOWERRAT':'jian_earn',
                'JAJXACHIEVESTABILITYRAT':'jian_stable',
                'JAJXANTIRISKRAT':'jian_risk',
                'JAJXSTOCKSELECTIONRAT':'jian_stock',
                'JAJXTIMESELECTIONRAT':'jian_timeret',
                'JAJXBENCHMARKTRACKINGRAT':'jian_track',
                'JAJXEXCESSEARNINGSRAT':'jian_alpha',
                'JAJXTOTALFEERAT':'jian_fee',
                'fund_id':'fund_id',
            }
            df = df.rename(columns = name_dic)
            df = df.dropna(subset=['fund_id','datetime'], axis=0)
            real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
            df['datetime'] = real_date
            # TODO: 最好原子提交下边两步
            BasicDataApi().delete_fund_rate(real_date, df.fund_id.to_list())
            self._data_helper._upload_basic(df, FundRate.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def trading_day_list(self, start_date, end_date, is_automatic_update=True):
        try:
            # 如果是每日自动更新，我们需要去存T+1日的数据
            if is_automatic_update:
                start_date = end_date
                end_date = ''
            df = self._raw_data_api.get_em_tradedates(start_date, end_date)
            df = df.rename(columns={'TRADEDATES': 'datetime'})
            if is_automatic_update:
                df = df.iloc[[1], :]
            self._data_helper._upload_basic(df, TradingDayList.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def fund_size_hold_rate(self, start_date: str, end_date: str, is_history=True):
        try:
            if is_history:
                fund_holding_rate = self._raw_data_api.get_em_fund_holding_rate(start_date=start_date, end_date=end_date)
            else:
                real_date = RawDataHelper.get_prev_target_date(end_date, SEMI_UPDATE_DATE_LIST)
                fund_holding_rate = self._raw_data_api.get_em_fund_holding_rate(start_date=real_date, end_date=real_date)
            if fund_holding_rate is not None and not fund_holding_rate.empty:
                fund_holding_rate['fund_id'] = fund_holding_rate.apply(
                    lambda x: self._data_helper._get_fund_id_from_order_book_id(x['CODES'].split('.')[0], x['DATES']), axis=1)
                fund_holding_rate = fund_holding_rate[fund_holding_rate.fund_id.notna()]
                fund_holding_rate = fund_holding_rate.drop(columns=['CODES', '_update_time']).rename(columns={
                    'DATES': 'datetime',
                    'HOLDPERSONALHOLDINGPCT': 'personal_holds',
                    'HOLDINSTIHOLDINGPCT': 'institution_holds',
                    'HOLDNUM': 'hold_num',
                })
                fund_holding_rate = fund_holding_rate[fund_holding_rate.drop(columns='fund_id').notna().any(axis=1)]

            if is_history:
                fund_scale = self._raw_data_api.get_em_fund_scale(start_date=start_date, end_date=end_date)
            else:
                real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
                fund_scale = self._raw_data_api.get_em_fund_scale(start_date=real_date, end_date=real_date)
            fund_scale = fund_scale.pivot(index='DATES', columns='CODES', values=['FUNDSCALE', 'UNITTOTAL']).fillna(method='ffill').stack().reset_index()
            fund_scale['fund_id'] = fund_scale.apply(
                lambda x: self._data_helper._get_fund_id_from_order_book_id(x['CODES'].split('.')[0], x['DATES']), axis=1)
            fund_scale = fund_scale[fund_scale.fund_id.notna()]
            fund_scale = fund_scale.drop(columns=['CODES']).rename(columns={'DATES': 'datetime', 'FUNDSCALE': 'size', 'UNITTOTAL': 'unit_total'})

            if fund_holding_rate is not None and not fund_holding_rate.empty:
                df = fund_scale.set_index(['fund_id', 'datetime']).join(fund_holding_rate.set_index(['fund_id', 'datetime']), how='left').reset_index()
                df['datetime'] = df.datetime.dt.date
            else:
                df = fund_scale
            df = df.drop_duplicates(subset='fund_id')
            if not is_history:
                now_df = BasicDataApi().get_history_fund_size(start_date=real_date, end_date=real_date)
                if now_df is not None:
                    now_df = now_df.replace({None: np.nan}).infer_objects()
                    # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
                    now_df = now_df.drop(columns=['_update_time']).sort_values(by=['fund_id', 'datetime']).drop_duplicates(subset='fund_id', keep='last')
                    # merge on all columns
                    df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
                    df = df[df._merge == 'left_only'].drop(columns=['_merge'])
                # TODO: 最好原子提交下边两步
                BasicDataApi().delete_fund_size_hold_rate(real_date, df.fund_id.to_list())
            self._data_helper._upload_basic(df, Fund_size_and_hold_rate.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def fund_hold_asset(self, start_date: str, end_date: str, is_history=True):
        try:
            if is_history:
                # history, update only on report date
                df = self._raw_data_api.get_em_fund_hold_asset(start_date, end_date)
            else:
                real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
                df = self._raw_data_api.get_em_fund_hold_asset(real_date, real_date)
            df['CODES'] = df.apply(lambda x: self._data_helper._get_fund_id_from_order_book_id(x.CODES.split('.')[0], x.DATES), axis=1)
            df = df.drop(columns='_update_time').dropna(subset=['CODES']).drop_duplicates(subset=['CODES', 'DATES'], keep='last')
            name_dict = {
                'CODES': 'fund_id',
                'DATES': 'datetime',
                'PRTSTOCKTONAV': 'stock_nav_ratio',
                'PRTBONDTONAV': 'bond_nav_ratio',
                'PRTFUNDTONAV': 'fund_nav_ratio',
                'PRTCASHTONAV': 'cash_nav_ratio',
                'PRTOTHERTONAV': 'other_nav_ratio',
                'MMFFIRSTREPOTONAV': 'first_repo_to_nav',
                'MMFAVGPTM': 'avg_ptm',
            }
            df = df.rename(columns=name_dict)
            if not is_history:
                now_df = BasicDataApi().get_fund_hold_asset(dt=real_date)
                if now_df is not None:
                    df = df.replace({None: np.nan}).infer_objects()
                    now_df = now_df.replace({None: np.nan}).infer_objects()
                    # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
                    now_df = now_df.drop(columns=['_update_time']).sort_values(by=['fund_id', 'datetime']).drop_duplicates(subset='fund_id', keep='last')
                    # merge on all columns
                    df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
                    df = df[df._merge == 'left_only'].drop(columns=['_merge'])
                # TODO: 最好原子提交下边两步
                BasicDataApi().delete_fund_hold_asset(real_date, df.fund_id.to_list())
            self._data_helper._upload_basic(df, FundHoldAsset.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def fund_hold_industry(self, start_date: str, end_date: str, is_history=False):
        try:
            if is_history:
                # history, update only on report date
                df = self._raw_data_api.get_em_fund_hold_industry(start_date, end_date)
                df_qdii = self._raw_data_api.get_em_fund_hold_industry_qdii(start_date, end_date)
                df = pd.concat([df, df_qdii], axis=0)
            else:
                real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
                df = self._raw_data_api.get_em_fund_hold_industry(real_date, real_date)
                df_qdii = self._raw_data_api.get_em_fund_hold_industry_qdii(real_date, end_date)
                df = pd.concat([df, df_qdii], axis=0)
            
            df['CODES'] = df.apply(lambda x: self._data_helper._get_fund_id_from_order_book_id(x.CODES.split('.')[0], x.DATES), axis=1)
            df = df.dropna(subset=['CODES']).drop(columns='_update_time')
            name_dict = {
                'CODES': 'fund_id',
                'DATES': 'datetime',
            }
            df = df.rename(columns=name_dict)
            if not is_history:
                now_df = BasicDataApi().get_fund_hold_industry(dt=real_date)
                if now_df is not None:
                    # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
                    now_df = now_df.drop(columns=['_update_time']).sort_values(by=['fund_id', 'datetime']).drop_duplicates(subset='fund_id', keep='last')
                    # merge on all columns
                    df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
                    df = df[df._merge == 'left_only'].drop(columns=['_merge'])
                # TODO: 最好原子提交下边两步
                BasicDataApi().delete_fund_hold_industry(real_date, df.fund_id.to_list())
            self._data_helper._upload_basic(df, FundHoldIndustry.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def fund_hold_stock(self, start_date: str, end_date: str, is_history=True):
        try:
            if is_history:
                # history, update only on report date
                df = self._raw_data_api.get_em_fund_hold_stock(start_date, end_date)
                df_qdii = self._raw_data_api.get_em_fund_hold_stock_qdii(start_date, end_date)
                res_stock = []
                for r in df_qdii.iterrows():
                    res_stock.append(self._data_helper._qdii_fund_hold_r(r,'股票'))
                df_qdii = pd.DataFrame(res_stock)
                df = pd.concat([df, df_qdii], axis=0)

            else:
                real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
                df = self._raw_data_api.get_em_fund_hold_stock(real_date, real_date)
                df_qdii = self._raw_data_api.get_em_fund_hold_stock_qdii(real_date, end_date)
                res_stock = []
                for r in df_qdii.iterrows():
                    res_stock.append(self._data_helper._qdii_fund_hold_r(r,'股票'))
                df_qdii = pd.DataFrame(res_stock)
                df = pd.concat([df, df_qdii], axis=0)
            
            df['CODES'] = df.apply(lambda x: self._data_helper._get_fund_id_from_order_book_id(x.CODES.split('.')[0], x.DATES), axis=1)
            df = df.dropna(subset=['CODES']).drop(columns='_update_time')
            name_dict = {
                'CODES': 'fund_id',
                'DATES': 'datetime',
            }
            df = df.rename(columns=name_dict)
            if not is_history:
                now_df = BasicDataApi().get_fund_hold_stock(dt=real_date)
                if now_df is not None:
                    # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
                    now_df = now_df.drop(columns=['_update_time']).sort_values(by=['fund_id', 'datetime']).drop_duplicates(subset='fund_id', keep='last')
                    # merge on all columns
                    df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
                    df = df[df._merge == 'left_only'].drop(columns=['_merge'])
                # TODO: 最好原子提交下边两步
                BasicDataApi().delete_fund_hold_stock(real_date, df.fund_id.to_list())
            print(df)
            self._data_helper._upload_basic(df, FundHoldStock.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def fund_hold_bond(self, start_date: str, end_date: str, is_history=True):
        try:
            if is_history:
                # history, update only on report date
                df = self._raw_data_api.get_em_fund_hold_bond(start_date, end_date)
                df_qdii = self._raw_data_api.get_em_fund_hold_stock_qdii(start_date, end_date)
                
            else:
                real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
                df = self._raw_data_api.get_em_fund_hold_bond(real_date, real_date)
                df_qdii = self._raw_data_api.get_em_fund_hold_stock_qdii(start_date, end_date)

            cols_list = df_qdii.columns.tolist()
            df_qdii.columns = [i.replace('stock','bond') for i in cols_list]
            res_bond = []
            for r in df_qdii.iterrows():
                res_bond.append(self._data_helper._qdii_fund_hold_r(r,'债券'))
            df_qdii = pd.DataFrame(res_bond).dropna(axis=0)
            df = pd.concat([df, df_qdii], axis=0)

            df['CODES'] = df.apply(lambda x: self._data_helper._get_fund_id_from_order_book_id(x.CODES.split('.')[0], x.DATES), axis=1)
            df = df.dropna(subset=['CODES']).drop(columns='_update_time')
            name_dict = {
                'CODES': 'fund_id',
                'DATES': 'datetime',
            }
            df = df.rename(columns=name_dict)
            if not is_history:
                now_df = BasicDataApi().get_fund_hold_bond(dt=real_date)
                if now_df is not None:
                    # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
                    now_df = now_df.drop(columns=['_update_time']).sort_values(by=['fund_id', 'datetime']).drop_duplicates(subset='fund_id', keep='last')
                    # merge on all columns
                    df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
                    df = df[df._merge == 'left_only'].drop(columns=['_merge'])
                # TODO: 最好原子提交下边两步
                BasicDataApi().delete_fund_hold_bond(real_date, df.fund_id.to_list())
            self._data_helper._upload_basic(df, FundHoldBond.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def fund_stock_portfolio(self, start_date: str, end_date: str, is_history=True):
        try:
            if is_history:
                # history, update only on report date
                df = self._raw_data_api.get_em_fund_stock_portfolio(start_date, end_date)
            else:
                real_date = RawDataHelper.get_prev_target_date(end_date, SEMI_UPDATE_DATE_LIST)
                df = self._raw_data_api.get_em_fund_stock_portfolio(real_date, real_date)
            df = df.drop(columns='_update_time')
            df['em_id'] = df.apply(lambda x: self._data_helper._get_fund_id_from_order_book_id(x.em_id.split('.')[0], x.report_date), axis=1)
            df = df[df.em_id.notna()]
            name_dict = {
                'em_id': 'fund_id',
                'report_date': 'datetime',
            }
            df = df.rename(columns=name_dict)
            # if not is_history:
            #     now_df = BasicDataApi().get_fund_stock_portfolio(dt=real_date)
            #     if now_df is not None:
            #         # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
            #         now_df = now_df.drop(columns=['_update_time']).sort_values(by=['fund_id', 'datetime']).drop_duplicates(subset='fund_id', keep='last')
            #         # merge on all columns
            #         df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
            #         df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            #     # TODO: 最好原子提交下边两步
            #     BasicDataApi().delete_fund_hold_bond(real_date, df.fund_id.to_list())
            # self._data_helper._upload_basic(df, FundStockPortfolio.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def mng_info(self):
        df = self._raw_data_api.get_em_mng_info()
        df['fund_id'] = df.apply(lambda x : 
                    self._data_helper._get_fund_id_from_order_book_id(x.code.split('.')[0], datetime.date(2020,8,10)), axis=1)
        df = df.drop('code',axis=1).dropna(subset=['fund_id'])
        self._data_helper._upload_basic(df, MngInfo.__table__.name)

    def mng_change(self):
        df = self._raw_data_api.get_em_fund_mng_change()
        df['fund_id'] = df.apply(lambda x : 
                    self._data_helper._get_fund_id_from_order_book_id(x.code.split('.')[0], datetime.date(2020,8,10)), axis=1)
        df = df.drop('code',axis=1).dropna(subset=['fund_id'])
        self._data_helper._upload_basic(df, FundMngChange.__table__.name)

    def fund_comp_mng_change(self):
        df = self._raw_data_api.get_fund_com_mng_change()
        self._data_helper._upload_basic(df, FundCompMngChange.__table__.name)

    def fund_comp_core_mng(self):
        df = self._raw_data_api.get_em_fund_com_core_mng()
        df['fund_id'] = df.apply(lambda x : 
                    self._data_helper._get_fund_id_from_order_book_id(x.code.split('.')[0], datetime.date(2020,8,10)), axis=1)
        df = df.drop('code',axis=1).dropna(subset=['fund_id'])
        self._data_helper._upload_basic(df, FundCompCoreMng.__table__.name)

    def fund_open_info(self):
        df = self._raw_data_api.get_em_fund_open()
        df['fund_id'] = df.apply(
            lambda x : self._data_helper._get_fund_id_from_order_book_id(x.em_id.split('.')[0], datetime.date(2020,9,15)), axis = 1)       
        df = df.dropna(subset=['fund_id'])
        df = df.drop(['em_id','_update_time'],axis=1)
        self._data_helper._upload_basic(df, FundOpenInfo.__table__.name)

    def stock_in_fund(self):
        dt = datetime.date(2020,9,30)
        stock_info = RawDataApi().get_em_stock_info()
        fund_info = BasicDataApi().get_fund_info()
        stock_fund = BasicDataApi().get_fund_hold_stock(dt=dt)
        stock_fund = stock_fund.set_index('fund_id')
        cols = [[f'rank{i+1}_stock_code', f'rank{i+1}_stock', f'rank{i+1}_stockweight'] for i in range(10)]
        res = []
        for i in cols:
            df = stock_fund[i]
            df.columns = ['stock_id','stock_name','stock_weight']
            res.append(df)
        stock_fund = pd.concat(res).dropna(axis=0)
        stock_fund = stock_fund.reset_index()
        stock_fund['datetime'] = dt
        stock_fund = pd.merge(stock_fund, fund_info[['fund_id','desc_name']].rename(columns={'desc_name':'fund_name'}), on ='fund_id')
        # 海外股票简称未处理，过长，仅展示国内股票
        stock_fund = stock_fund[stock_fund.stock_id.str.contains('.SH') | stock_fund.stock_id.str.contains('.SZ')]
        self._data_helper._upload_basic(stock_fund, StockInFund.__table__.name)

    def bond_in_fund(self):
        dt = datetime.date(2020,9,30)
        bond_info = RawDataApi().get_em_bond_info()
        fund_info = BasicDataApi().get_fund_info()
        bond_fund = BasicDataApi().get_fund_hold_bond(dt=dt)
        bond_fund = bond_fund.set_index('fund_id')
        cols = [[f'rank{i+1}_bond_code', f'rank{i+1}_bond', f'rank{i+1}_bondweight'] for i in range(10)]
        res = []
        for i in cols:
            df = bond_fund[i]
            df.columns = ['bond_id','bond_name','bond_weight']
            res.append(df)
        bond_fund = pd.concat(res).dropna(axis=0)
        bond_fund = bond_fund.reset_index()
        bond_fund['datetime'] = dt
        bond_fund = pd.merge(bond_fund, fund_info[['fund_id','desc_name']].rename(columns={'desc_name':'fund_name'}), on ='fund_id')
        # 海外债券简称未处理，过长，仅展示国内债券
        bond_fund = bond_fund[bond_fund.stock_id.str.contains('.SH') | bond_fund.stock_id.str.contains('.SZ') | bond_fund.stock_id.str.contains('.IB')]
        self._data_helper._upload_basic(bond_fund, BondInFund.__table__.name)

    def stock_tag(self):
        def get_concept_id(tag_name, raw_concept_id):
            return f'{tag_name}@{str(raw_concept_id)}'
        
        ''' em cpt
        df = self._raw_data_api.get_em_stock_concept_info()
        tag_group_id = 'em_cpt_201223'
        concept_id_dic = {}
        concept_stock_dic = {}
        raw_concept_id = 1
        for r in df.itertuples():
            if r.concepts is None:
                continue
            concept_list = r.concepts.split(',')
            for concept_i in concept_list:
                if concept_i not in concept_id_dic:
                    concept_id_dic[concept_i] = get_concept_id(tag_group_id, raw_concept_id)
                    raw_concept_id += 1
                else:
                    pass
                
                if concept_i not in concept_stock_dic:
                    concept_stock_dic[concept_i] = []
                else:
                    concept_stock_dic[concept_i].append(r.codes)
        concept_df = pd.DataFrame([concept_id_dic]).T
        concept_df.columns=['tag_id']

        concept_stock_df = pd.DataFrame([concept_stock_dic]).T
        concept_stock_df.columns=['stock_id']
        df = concept_df.join(concept_stock_df).explode('stock_id').reset_index()
        df = df.rename(columns={'index':'tag_name'})
        df.loc[:,'tag_group_id'] = tag_group_id
        '''
        '''
        tag_group_id = 'dm_cpt_201223'
        stock_used_cpt = self._basic_data_api.get_fund_stock_concept(tag_group_id)
        cpt_rules_raw = {'白酒':['白酒'],
        '5G':['5G概念'],
        '半导体':['半导体','第三代半导体'],
        '芯片':['国产芯片'],
        '光伏':['太阳能'],
        '农业':['农业种植','生态农业'],
        '新能源':['新能源车','新能源'],
        '医疗':['医疗器械','互联医疗','精准医疗'],
        '医美':['医疗美容'],
        '银行':['参股银行'],
        '券商':['参股券商','券商概念'],
        '黄金':['黄金概念'],
        '军工':['军工'],
        '养老':['养老概念']}

        cpt_rules = {}
        for k, vs in cpt_rules_raw.items():
            for v in vs:
                cpt_rules[v] = k
        concept_id_dic = {}
        concept_stock_dic = {}
        raw_concept_id = 1
        select_cpts = list(cpt_rules.keys())
        stock_cpt_selected = stock_used_cpt[stock_used_cpt.tag_name.isin(select_cpts)]
        for r in stock_cpt_selected.itertuples():
            new_tag_name = cpt_rules[r.tag_name]
            if new_tag_name not in concept_id_dic:
                concept_id_dic[new_tag_name] = get_concept_id(tag_group_id, raw_concept_id)
                raw_concept_id += 1
            else:
                pass
            
            if new_tag_name not in concept_stock_dic:
                concept_stock_dic[new_tag_name] = []
            else:
                concept_stock_dic[new_tag_name].append(r.stock_id)
        concept_df = pd.DataFrame([concept_id_dic]).T
        concept_df.columns=['tag_id']

        concept_stock_df = pd.DataFrame([concept_stock_dic]).T
        concept_stock_df.columns=['stock_id']
        df = concept_df.join(concept_stock_df).explode('stock_id').reset_index()
        df = df.rename(columns={'index':'tag_name'})
        df.loc[:,'tag_group_id'] = tag_group_id
        df = df.drop_duplicates(subset=['tag_id','stock_id','tag_group_id'])
        '''
        tag_group_id = 'dm_ind_201224'
        industry_info = self._raw_data_api.get_em_industry_info()
        stock_info = self._raw_data_api.get_em_stock_info()
        stock_info.loc[:,'sw_indus_1'] = stock_info.bl_sws_ind_code.map(lambda x: x.split('-')[0] if x is not None else None)
        ind_rules_raw = {'食品饮料':['食品饮料'],
                        '消费':['休闲服务','家用电器','纺织服装','食品饮料'],
                        '可选消费':['休闲服务','家用电器','纺织服装'],
                        '主要消费':['食品饮料'],
                        '科技':['电子','计算机','通信'],
                        '农业':['农林牧渔'],
                        '医药':['医药生物'],
                        '券商':['非银金融'],
                        '金融地产':['房地产','非银金融','银行'],
                        '金融':['非银金融','银行'],
                        '地产':['房地产'],
                        '有色':['有色金属'],
                        '军工':['国防军工']}
        # combine rule
        ind_rules = {}
        for k, vs in ind_rules_raw.items():
            for v in vs:
                if v not in ind_rules:
                    ind_rules[v] = []
                ind_rules[v].append(k)
                
        # make id 
        num = 1
        id_dic = {}
        for ind in ind_rules_raw:
            id_dic[ind] = get_concept_id(tag_group_id, num)
            num += 1
            
        _df1 = stock_info[['stock_id','sw_indus_1']]
        _df2 = industry_info[['em_id','ind_name']].rename(columns={'em_id':'sw_indus_1'})
        df = pd.merge(_df1, _df2, on='sw_indus_1' )[['stock_id','ind_name']].rename(columns={'ind_name':'tag_name'})
        df['tag_name_new'] = df.tag_name.map(lambda x: ind_rules.get(x))
        df = df.dropna().explode('tag_name_new')
        df.loc[:,'tag_id'] = df.tag_name_new.map(lambda x : id_dic[x])
        df = df.drop(columns=['tag_name']).rename(columns={'tag_name_new':'tag_name'})
        df.loc[:,'tag_group_id'] = tag_group_id


        self._data_helper._upload_basic(df, StockTag.__table__.name)

    def etf_info(self):
        def main_index(x):
            if x == '':
                return None
            x = json.loads(x)
            x = sorted(x.items(), key=lambda x:x[1], reverse=True)[0][0]
            if x == '-1':
                return None
            return x
        
        benchmark_info = self._basic_data_api.get_fund_benchmark()
        inside_market_fund = self._basic_data_api.get_inside_market_funds()
        outside_market_funds = self._basic_data_api.get_outside_market_funds()
        index_info = self._basic_data_api.get_index_info()

        inside_market_fund = inside_market_fund[inside_market_fund.desc_name.str.contains('ETF')]
        outside_market_funds = outside_market_funds[outside_market_funds.desc_name.str.contains('ETF')]
        benchmark_info['main_index'] = benchmark_info.benchmark_s.map(lambda x : main_index(x))
        df = pd.merge(inside_market_fund, benchmark_info[['fund_id','main_index']], on=['fund_id'])
        in_market = df[['fund_id','desc_name','wind_class_1','wind_class_2','company_id','main_index']].rename(columns={'main_index':'index_id'})
        in_market['etf_type'] = '场内'
        df = pd.merge(outside_market_funds, benchmark_info[['fund_id','main_index']], on=['fund_id'])
        out_market = df[['fund_id','desc_name','wind_class_1','wind_class_2','company_id','main_index']].rename(columns={'main_index':'index_id'})
        out_market['etf_type'] = '场外'
        result = pd.concat([in_market,out_market], axis=0)
        result = pd.merge(result, index_info[['index_id','desc_name']].rename(columns={'desc_name':"index_name"}), on='index_id')
        change_fund_list = result[(result.etf_type == '场内') & (result.desc_name.str.contains('ETF联接'))].fund_id.tolist()
        result = result.set_index('fund_id')
        result.loc[change_fund_list,'etf_type'] = '场外'
        result = result.reset_index()
        self._data_helper._upload_basic(result, ETFInfo.__table__.name)

    def process_all(self, start_date, end_date):
        failed_tasks = []
        # Depend on RQ
        # if not self.rq_fund_ret(start_date, end_date):
        #     failed_tasks.append('rq_fund_ret')

        # # Depend on RQ
        # if not self.stock_info():
        #     failed_tasks.append('stock_info')

        # Depend on RQ
        # if not self.rq_stock_price(start_date, end_date):
        #     failed_tasks.append('rq_stock_price')

        if not self.index_price(start_date, end_date):
            failed_tasks.append('index_price')

        # new_fund_list, _ = RawDataHelper.get_new_and_delisted_fund_list(end_date)
        # if new_fund_list is None:
        #     failed_tasks.append('get new_fund_list')
        # else:
        #     if not self.fund_info_from_raw(new_fund_list):
        #         failed_tasks.append('fund_info')

        # Depend on RQ
        # if not self.fund_rating_latest():
        #     failed_tasks.append('fund_rating_latest')

        if not self.fund_size(start_date, end_date):
            failed_tasks.append('fund_size')

        if not self.fund_nav(start_date, end_date):
            failed_tasks.append('fund_nav')

        if not self.trading_day_list(start_date, end_date):
            failed_tasks.append('trading_day_list')

        if not self.fund_rate(end_date):
            failed_tasks.append('fund_rate')

        if not self.fund_status_latest(end_date):
            failed_tasks.append('fund_status_latest')

        # 获取下一个交易日
        trading_day_df = BasicDataApi().get_trading_day_list(start_date=end_date)
        if trading_day_df.shape[0] <= 1:
            print(f'get trading days start with {end_date} failed')
            failed_tasks.append('get_trading_day_list for weekly update in basic')
        else:
            next_trading_day = trading_day_df.iloc[1, :].datetime
            print(f'got next trading day {next_trading_day}')
            end_date_dt = pd.to_datetime(end_date, infer_datetime_format=True).date()
            next_trading_dt = pd.to_datetime(next_trading_day, infer_datetime_format=True).date()
            if end_date_dt.weekday() < next_trading_dt.weekday() and next_trading_dt < end_date_dt + datetime.timedelta(weeks=1):
                # 表明本周后边还有交易日，今天不需要更新
                print(f'weekly data only update on the last day of week, not today {end_date_dt}')
            else:
                if not self.fund_hold_asset(end_date, end_date, is_history=False):
                    failed_tasks.append('fund_hold_asset')

                if not self.fund_size_hold_rate(end_date, end_date, is_history=False):
                    failed_tasks.append('fund_size_hold_rate')

                if not self.fund_hold_stock(end_date, end_date, is_history=False):
                    failed_tasks.append('fund_stock')

                if not self.fund_hold_bond(end_date, end_date, is_history=False):
                    failed_tasks.append('fund_bond')

                if not self.fund_hold_industry(end_date, end_date, is_history=False):
                    failed_tasks.append('fund_industry')

        return failed_tasks

    def process_not_trading_day(self, start_date, end_date):
        failed_tasks = []
        
        if not self.index_price(start_date, end_date):
            failed_tasks.append('index_price')

        if not self.fund_nav(start_date, end_date):
            failed_tasks.append('fund_nav')

        return failed_tasks


if __name__ == '__main__':
    bdp = BasicDataPart1(BasicDataHelper())
    # start_date = '20210624'
    # end_date = '20210624'
    # bdp.fund_nav(start_date, end_date)
    # bdp.index_price(start_date, end_date)
    # bdp.rq_stock_price(start_date, end_date)
    # bdp.rq_fund_ret(start_date, end_date)
    # bdp.fund_rating_latest()
    # bdp.fund_size('20200513', '20200513')
    # bdp.trading_day_list('20200124', '20200301', False)
    # bdp.fund_benchmark()
    # bdp.sector_info()
    # bdp.sector_funds()
    # bdp.index_component()
    # bdp.fund_rate('20200812')
    # bdp.fund_size_hold_rate_history()
    # bdp.recalc_all_funds_benchmark('/Users/ido/Downloads/new_funds_benchmark_info.csv')
