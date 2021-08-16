import numpy as np
import pandas as pd
import datetime
from .raw_data_helper import RawDataHelper
from ...view.raw_models import OSFundInfo, OSFundNav, OSFundBenchmark, OSStockInfo, OSCorpBondInfo, OSGovtBondInfo, OSComdtyInfo, OSIndexFutureInfo, OSMtgeBondInfo, EmOverseaStockFinFac, OSFundBenchmarks, OSFundNavAdj, HFFundNavMiss
from ...api.raw import RawDataApi

# df.to_sql('em_oversea_stock_fin_fac', RawDatabaseConnector().get_engine(), index=False, if_exists='append')

class OtherRawDataDownloader:

    def __init__(self, data_helper):
        self._data_helper = data_helper

    def oversea_fund_info(self, fund_info):
        fund_info_dic = {
            '基金id':'codes',
            '基金名称':'desc_name',
            '基金管理公司':'company_name',
            '基金类型':'fund_type',
            '行业':'industry',
            '地区':'area',
            '最新净值':'latest_nav',
            '基金系列':'fund_series',
            '是否为新基金':'is_new_fund',
            '赎回资金到账天数':'redeem_dates',
            '换出基金指示滞延时间':'excg_out_t_delay',
            '换入基金指示滞延时间':'excg_in_t_delay',
            '最低初始投资额':'min_init_trade_amt',
            '最低后续投资额':'min_ag_trade_amt',
            '最小赎回类型':'min_redeem_type',
            '最小赎回数量':'min_redeem_vol',
            '最小持有类型':'min_pos_type',
            '最小持有数量':'min_pos_vol',
            '申购周期':'purchase_period',
            '风险级别':'risk_level',
            '可供认购':'is_purchase',
            '证监会是否认可':'is_CSRC_approve',
            '年费':'yearly_fee',
            '申购处理频率':'purchase_process_freq',
            '币种':'money_type',
            '支持转换基金':'is_sup_exchg_fund',
            '支持转换为同系列其他基金':'is_sup_same_series_fund',
            '支持同系列其他基金转换为本基金':'is_sup_same_series_exchg',
            '赎回费(%)':'redeem_fee',
            '赎回方式':'redeem_method',
            '是否衍生产品':'is_derivatives',
            '股息分派方式':'divident_distbt_mtd',
            '派息频率':'divident_freq',
            '资产类别':'asset_type',
            '资产编号':'asset_code',
            '发行日期':'issue_date',
            '发行价':'issue_price',
            '基金规模（单位：百万）':'fund_size_biln',
            '基金规模统计日期':'fund_size_calc_date',
            '基金规模币种':'fund_size_money_type',
            '费率':'fee_rate',
            '费率统计日期':'fee_calc_date',
            '复杂产品':'is_compx_product',
        }
        delete_cols = ['发布日期','处理结果']
        date_list = ['发行日期','费率统计日期','基金规模统计日期']
        con_list = ['是否为新基金','可供认购','证监会是否认可','支持转换基金','支持转换为同系列其他基金',
                '是否衍生产品','复杂产品','支持同系列其他基金转换为本基金']

        for date_col in date_list:
            td = pd.to_datetime(fund_info[date_col])
            td = [i.date() for i in td]
            fund_info.loc[:,date_col] = td

        for del_col in delete_cols:
            fund_info = fund_info.drop(columns=[del_col])

        for con_col in con_list:
            fund_info.loc[:,con_col] = fund_info[con_col].replace({'是':True, '否':False,})
            
        fund_info = fund_info.rename(columns=fund_info_dic)
        self._data_helper._upload_raw(fund_info, OSFundInfo.__table__.name)

    def oversea_fund_nav(self, df):
        td = pd.to_datetime(df.datetime)
        td = [i.date() for i in td]
        df['datetime'] = td
        self._data_helper._upload_raw(df, OSFundNav.__table__.name)

    def oversea_fund_benchmark(self, df):
        dic = {
            '#N/A Field Not Applicable':None,
            '#N/A Invalid Security':None,
        }
        df = df.replace(dic)
        self._data_helper._upload_raw(df, OSFundBenchmark.__table__.name)

    def oversea_stock_info(self, df):
        df = df.rename(columns={'code':'codes','stock name':'stock_name_e','证券简称':'stock_name_c','行业分类':'industry'}).drop(columns=['number'])
        df.loc[:,'district_code'] = df.codes.map(lambda x: x.split(' ')[1])
        self._data_helper._upload_raw(df, OSStockInfo.__table__.name)

    def oversea_corp_bond_info(self, df):
        df = df.rename(columns={'code':'codes','债券名称/公司名称':'bond_name_e','公司名称-繁体中文':'company_name_c','债券对应的股票代码':'company_code','国家全称':'district_name_e','行业分类-一级':'industry_1','行业分类-二级':'industry_2','行业分类-三级':'industry_3','到期日':'maturity','穆迪评级':'md_rate','标普评级':'sp_rate','惠誉评级':'hy_rate','ISIN':'isin_code'}).drop(columns=['number'])
        df = df.replace('#N/A Field Not Applicable',None)
        td = pd.to_datetime(df.maturity)
        df.maturity = [i.date() for i in td]
        self._data_helper._upload_raw(df, OSCorpBondInfo.__table__.name)
        
    def oversea_govt_bond_info(self, df):
        df = df.rename(columns={'code':'codes','债券名称/公司名称':'bond_name_e','公司名称-繁体中文':'bond_name_c','国家全称':'district_name','到期日':'maturity','穆迪评级':'md_rate','标普评级':'sp_rate','惠誉评级':'hy_rate','ISIN':'isin_code','发行金额':'total_amount'}).drop(columns=['number'])
        df = df.replace('#N/A Field Not Applicable',None)
        td = pd.to_datetime(df.maturity)
        df.maturity = [i.date() for i in td]
        self._data_helper._upload_raw(df, OSGovtBondInfo.__table__.name)

    def oversea_comdty_info(self, df):
        df = df.rename(columns={'code':'codes','证券名称':'asset_name_e','证券类型':'future_type','期货合约到期日':'maturity'}).drop(columns=['number'])
        df = df.replace('#N/A Field Not Applicable',None)
        td = pd.to_datetime(df.maturity)
        df.maturity = [i.date() for i in td]
        self._data_helper._upload_raw(df, OSComdtyInfo.__table__.name)
        return df

    def oversea_index_info(self, df):
        df = df.rename(columns={'code':'codes','证券名称':'asset_name_c','期货合约到期日':'maturity'}).drop(columns=['number'])
        df = df.replace('#N/A Field Not Applicable',None)
        td = pd.to_datetime(df.maturity)
        df.maturity = [i.date() for i in td]
        df.loc[:,'asset_type'] = 'Index'
        self._data_helper._upload_raw(df, OSIndexFutureInfo.__table__.name)

    def oversea_mtge_bond_info(self, df):
        df = df.rename(columns={'code':'codes','资产类别':'asset_type','证券名称':'bond_name_e','抵押债本金偿付期限开始日期':'mtge_pay_start','抵押债本金偿付期限结束日期':'mtge_pay_end','ISIN':'isin_code'}).drop(columns='number')
        td = pd.to_datetime(df.mtge_pay_start)
        df.mtge_pay_start = [i.date() for i in td]
        td = pd.to_datetime(df.mtge_pay_end)
        df.mtge_pay_end = [i.date() for i in td]
        self._data_helper._upload_raw(df, OSMtgeBondInfo.__table__.name)

    def oversea_stock_fin_fac(self, df):
        f = '/Users/huangkejia/Home/'
        market=['全部美股','全部港股']
        stock_list = ['_19_4.xls','_20_1.xls','_20_2.xls','_20_3.xls']
        date_dic = {
            '_19_4.xls':'20191231',
            '_20_1.xls':'20200331',
            '_20_2.xls':'20200630',
            '_20_3.xls':'20200930',
        }
        res = []
        res_cols = []
        for market_i in market:
            for stock_i in stock_list:
                df = pd.read_excel(f+market_i+stock_i).dropna(subset=['证券名称'])
                df.columns = [i.split('\r\n')[0] for i in df.columns]
                df = df.drop(columns=['市盈率(PE)','市净率(PB)','市销率(PS)','股息率'], errors='ignore')
                df.loc[:,'report_date'] = date_dic[stock_i]
                df = df.loc[:,~df.columns.duplicated()]
                cols = df.columns.tolist()
                df = df[sorted(cols)]
                res_cols.append(cols)
                res.append(df)

        df = pd.concat(res)
        dic = {
            'report_date':'report_date',
            '已发行普通股':'indicator_1',
            '年度分红':'indicator_2',
            '归属母公司净利润(TTM)':'indicator_3',
            '每股净资产':'indicator_4',
            '每股净资产(最新股本摊薄)':'indicator_5',
            '每股收益EPS(基本)':'indicator_6',
            '每股收益EPS(稀释)':'indicator_7',
            '每股收益EPS(调整股本数)':'indicator_8',
            '每股派息':'indicator_9',
            '每股现金流量净额':'indicator_10',
            '每股现金流量净额(TTM)':'indicator_11',
            '每股经营现金净流量':'indicator_12',
            '每股经营现金净流量(TTM)':'indicator_13',
            '每股营业收入':'indicator_14',
            '稀释每股收益':'indicator_15',
            '经营活动产生的现金':'indicator_16',
            '营业收入':'indicator_17',
            '证券代码':'stock_code',
            '证券名称':'desc_name',
        }
        df = df.rename(columns=dic)
        '''
        for i,j in dic.items():
            if j in ['report_date','stock_code','desc_name']:
                data_row = f'{j} = Column(CHAR(20)) # {i} '
            else:
                data_row = f'{j} = Column(DOUBLE(asdecimal=False)) # {i} '
            print(data_row)
        '''
        df= df.replace('——',np.nan)
        self._data_helper._upload_raw(df, EmOverseaStockFinFac.__table__.name)


    def benchmark_process(self):
        #### 修补逻辑  
        ##### 1. bloomberg 1
        ##### 2. morning star
        ##### 3. bloomberg 3
        ##### 4. 人工
        folder = '/Users/huangkejia/Downloads/Data/'
        excel = 'Benchmark-210118-unlink.xlsx'
        fund_benchmark_total = pd.read_excel(folder+excel,sheet_name='Benchmark')
        fund_benchmark_total = fund_benchmark_total.replace('#N/A Field Not Applicable',np.nan).replace('#N/A Invalid Security',np.nan).replace(0,np.nan).drop(columns=['Benchmark_Souce_Factsheet','筛选原因'])
        
        # 无净值基准
        invaild_index_id = ['PCY US Equity']
        for i in invaild_index_id:
            fund_benchmark_total = fund_benchmark_total.replace(i,np.nan)
        
        # 替换列名
        dic = {
            '基金名称':'desc_name',
            '产品编号':'codes',
            'ISIN 编号':'isin_code',
            '行业-一级分类':'industry_1',
            '行业-二级分类':'industry_2',
            '地域侧重':'area',
            '行业分类_Morningstar':'morning_star_group',
            '筛选1':'benchmark_artificial',
            'Benchmark_Souce_Bloomberg Primary':'benchmark_1',
            'Benchmark_Souce_Bloomberg Secondary':'benchmark_2',
            'Benchmark_Souce_Bloomberg Third':'benchmark_3',
            'Benchmark_Souce_Morningstar':'benchmark_ms',
        }
        fund_benchmark_total = fund_benchmark_total.rename(columns=dic)
        
        # 人工补全基金基准
        artificial_list = [{
            'isin_code':'LU1694771590',
            'morning_star_benchmark':'MSCI World/Information Tech NR USD',
        },
        {
            'isin_code':'LU1529780063',
            'morning_star_benchmark':'MSCI World/Information Tech NR USD',
        },
        {
            'isin_code':'HK0000179314',
            'morning_star_benchmark':'Cat 50%Barclays US Agg TR&50%FTSE Wld TR',
        },
        {
            'isin_code':'IE00BG85LS38',
            'morning_star_benchmark':'BBgBarc US Agg Bond TR USD',
        },
        {
            'isin_code':'IE00BDB5PG57',
            'morning_star_benchmark':'BBgBarc US Agg Bond TR USD',
        },
        {
            'isin_code':'IE00BLP5S353',
            'morning_star_benchmark':'MSCI World NR USD',
        },
        ]
        fund_benchmark_total = fund_benchmark_total.set_index('isin_code')
        for i in artificial_list:
            fund_benchmark_total.loc[i['isin_code'],'benchmark_ms'] = i['morning_star_benchmark']
        fund_benchmark_total = fund_benchmark_total.reset_index()

        # 分组设置基金基准
        fund_benchmark_total.loc[:,'benchmark_final_mix'] = None 
        df_1 = fund_benchmark_total[~fund_benchmark_total['benchmark_1'].isnull()].copy()
        df_1['benchmark_final_mix'] = df_1['benchmark_1']

        df_2 = fund_benchmark_total[(fund_benchmark_total['benchmark_1'].isnull())
                                &(~fund_benchmark_total['benchmark_ms'].isnull())].copy()
        df_2['benchmark_final_mix'] = df_2['benchmark_ms']

        df_3 = fund_benchmark_total[(fund_benchmark_total['benchmark_1'].isnull())
                                &(fund_benchmark_total['benchmark_ms'].isnull())
                                &(~fund_benchmark_total['benchmark_3'].isnull())].copy()
        df_3['benchmark_final_mix'] = df_3['benchmark_3']

        df_4 = fund_benchmark_total[(fund_benchmark_total['benchmark_1'].isnull())
                                &(fund_benchmark_total['benchmark_ms'].isnull())
                                &(fund_benchmark_total['benchmark_3'].isnull())].copy()
        df_4['benchmark_final_mix'] = df_4['benchmark_artificial']
        df = pd.concat([df_1,df_2,df_3,df_4])

        # 替换用bloomberg代码替换晨星代码
        folder = '/Users/huangkejia/Downloads/Data/'
        excel = 'Benchmark-210118-unlink.xlsx'
        ms_data = pd.read_excel(folder+excel,sheet_name='Morning star对应BBG Ticker')
        ms_ticker_to_bb_ticker_dic = ms_data.set_index('Category Index').to_dict()['Bloomberg code ']
        df.loc[:,'benchmark_final_bb_only'] = df.benchmark_final_mix.replace(ms_ticker_to_bb_ticker_dic)

        # 去掉index_id 代码后缀 '_index' '_Index' .. 
        df.loc[:,'benchmark_final'] =  df.benchmark_final_bb_only.map(lambda x:x.replace(' Index','').replace(' index','').replace(' INDEX','').replace(' iNDEX',''))

        # 部分指数是jpm 没有基金代码 人工选取替换
        replace_dict = {
            'JPMGGLBL':'BGAGTRUU',
            'JPMGEUTR':'LEGVTREU',
            'JACINGTR':'I02885JP',
            'JBCD103':'JPEIGLBL',
            'JPMGBRUS':'HEC0',
            'NRIEEED':'M1EU4000',
            'JESGEMHE':'BEHGTRUU',
            'DLJLVAL':'BGAGTRUU',
            'JGENBAUU':'I02859JP',
            'JPMGGLBP':'LG30TRUU',
            'M1CXKAA':'SPEMAUT',
            'JACIIGPR':'I02859JP',
            'JPGCCOMP':'BEHGTRUU',
            'JACICOTR':'I02859JP',
            'JGENVUUG':'BEHGTRUU',
            'JBCDCOMP':'BEHGTRUU',
            'JPEGHECP':'BEHGTRUU',
            'JPGCCPPI':'BEHGTRUU',
        }
        df.benchmark_final = df.benchmark_final.replace(replace_dict)

        # 部分指数没有净值 人工替换
        replace_dic = {
            'HEC0':'LP02OAS',
            'MSAUCAPF':'MSAPUSDN',
            'HW00':'LG30TRUU',
            'H4DC':'LG30TRUU',
            'E0A0':'BEHGTRUU',
            'BVA0':'LU13TRUU',
            'HUC0':'LF98TRUU',
            'EBRL':'LECPTREU',
            'FTGCY':'M1WO0MT',
            'C0C0':'LUACTRUU',
            'HW0C':'LG30TRUU',
            'JUC0':'LF98TRUU',
            'MSAUIA':'MXIN',
            'HW4C':'LG30TRUU',
            'G0O1':'LEGATRUU',
            'H0A0':'LG30TRUU',  
            'I02885JP':'I09585JP', 
            'USC0TR03':'LD08TRUU',
            'I08273CN':'mmf',
        }
        df.benchmark_final = df.benchmark_final.replace(replace_dic)
        #df.to_sql('oversea_fund_benchmarks', RawDatabaseConnector().get_engine(), index=False, if_exists='append')
        self._data_helper._upload_raw(df, OSFundBenchmarks.__table__.name)

    def fund_nav_adj_process(self):
        try:
            os_nav_div_factor = RawDataApi().get_os_fund_nav_div_factor().drop(columns='_update_time')
            os_nav_div_factor = os_nav_div_factor.pivot(index='ex_date', columns='product_id', values='factor')
            os_nav = RawDataApi().get_oversea_fund_nav()
            os_nav = os_nav.drop(columns='_update_time').pivot(index='datetime', columns='codes', values='nav')
            os_nav_div_factor = os_nav_div_factor.reindex(os_nav.index.union(os_nav_div_factor.index))
            os_nav_div_factor.iloc[0, :].fillna(1)
            os_nav_div_factor = os_nav_div_factor.ffill()
            os_nav_div_factor = os_nav_div_factor[os_nav_div_factor.index <= os_nav.index.max()]
            adj_nav = os_nav.ffill().mul(os_nav_div_factor, fill_value=1)
            df = pd.DataFrame(adj_nav.stack())
            df.columns = ['nav']
            df = df.reset_index()
            df = df.rename(columns={'level_1':'codes'})
            #df.to_sql('oversea_fund_nav_adj', RawDatabaseConnector().get_engine(), index=False, if_exists='append')
            self._data_helper._upload_raw(df, OSFundNavAdj.__table__.name, to_truncate=True)
            return True
        except Exception as e:
            print(e)
            return False

    def hf_fund_nav_miss(self):
        try:
            failed_tasks = []
            fund_info = RawDataApi().get_hf_fund_info()
            begin_date = datetime.datetime.today() - datetime.timedelta(days=365)
            fund_nav = RawDataApi().get_hf_fund_nav_dt(start_date=begin_date)
            exsited_fund_list = fund_nav.fund_id.unique().tolist()
            df = fund_info[~fund_info.fund_id.isin(exsited_fund_list)][['fund_id','desc_name']]
            self._data_helper._upload_raw(df, HFFundNavMiss.__table__.name, to_truncate=True)
        except Exception as e:
            print(e)
            failed_tasks.append(f'hf_fund_nav_miss')
        return failed_tasks
