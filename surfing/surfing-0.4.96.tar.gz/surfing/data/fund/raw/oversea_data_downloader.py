import requests
import traceback
import time
import numpy as np
from sqlalchemy.orm import sessionmaker
from ...api.raw import *
from .raw_data_helper import RawDataHelper
from ...view.raw_models import OSFundNav
from ...api.raw import RawDataApi

class OverseaDataUpdate:

    def __init__(self, update_period:int=35, data_per_page:int=20, data_helper=RawDataHelper()):
        self.update_period = update_period
        self.data_per_page = data_per_page
        self.data_helper = data_helper
        self.raw_data_api = RawDataApi()
        self.today = datetime.datetime.now().date()

    def update_unit(self, fund_id, exsited_price, fund_id_list):
        nav_dic = {
                'navDate':'datetime',
                'price':'nav',
            }
        url = 'https://fund.bluestonehk.com/fund/ifast/info/getHistoryNavs?productId={}&pageSize={}&pageNo={}'.format(
            fund_id, self.data_per_page, 1
        )
        response = requests.get(url)
        datas = response.json()
        if datas['message'] != '请求成功' or datas['body']['data'] == []:
            return None
        new_nav = pd.DataFrame(datas['body']['data'])[nav_dic.keys()].rename(columns=nav_dic)
        td = pd.to_datetime(new_nav.datetime)
        td = [_.date() for _ in td]
        new_nav.datetime = td
        exsited_date = exsited_price[exsited_price['codes'] == fund_id].datetime.max()
        new_df = new_nav[new_nav.datetime > exsited_date].copy()
        if new_df.empty:
            idx = fund_id_list.index(fund_id)
            if idx % 10 == 0:
                time.sleep(0.5)
                print(f'finish fund nav {idx}')
            return None
        new_df.loc[:,'codes'] = fund_id
        idx = fund_id_list.index(fund_id)
        if idx % 10 == 0:
            time.sleep(0.5)
            print(f'finish fund nav {idx}')
        return new_df

    def update_fund_nav(self):
        failed_tasks = []
        try:
            fund_info = self.raw_data_api.get_over_sea_fund_info()
            fund_id_list = fund_info.codes.tolist()
            update_period_dates = self.today - datetime.timedelta(days=self.update_period)
            exsited_price = self.raw_data_api.get_oversea_fund_nav(start_date = update_period_dates).drop(columns=['_update_time'], errors='ignore')
            result = []
            for fund_id in fund_id_list:
                _count = 0
                while True:
                    try:
                        if _count == 5:
                            break                        
                        new_df = self.update_unit(fund_id, exsited_price, fund_id_list)
                        #print(f'    fund_id {fund_id}')
                        if new_df is not None:
                            result.append(new_df)
                    except Exception as e:
                        _count += 1
                        print(e)
                        time.sleep(1)
                    else:
                        break
            if len(result) != 0:
                nav_result = pd.concat(result)
                self.data_helper._upload_raw(nav_result, OSFundNav.__table__.name)
                

        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(f'oversea_fund_nav')
        return failed_tasks
    
    def update_price_unit(self, fund_id, fund_id_list):
        nav_dic = {
                'navDate':'datetime',
                'price':'nav',
            }
        url = 'https://fund.bluestonehk.com/fund/ifast/info/getHistoryNavs?productId={}&pageSize={}&pageNo={}'.format(
            fund_id, self.data_per_page, 1
        )
        response = requests.get(url)
        datas = response.json()
        if datas['message'] != '请求成功' or datas['body']['data'] == []:
            return None
        new_df = pd.DataFrame(datas['body']['data'])
        if new_df.empty:
            idx = fund_id_list.index(fund_id)
            if idx % 10 == 0:
                time.sleep(0.5)
                print(f'finish fund nav {idx}')
            return None
        idx = fund_id_list.index(fund_id)
        if idx % 10 == 0:
            time.sleep(0.5)
            print(f'finish fund nav {idx}')
        return new_df

    def update_fund_adj_factor(self):
        failed_tasks = []
        try:
            fund_info = self.raw_data_api.get_over_sea_fund_info()
            fund_id_list = fund_info.codes.tolist()
            nav_div_factor = self.raw_data_api.get_os_fund_nav_div_factor().drop(columns=['_update_time'], errors='ignore')
            result = []
            for fund_id in fund_id_list:
                _count = 0
                while True:
                    try:
                        if _count == 5:
                            break   
                        idx = fund_id_list.index(fund_id)
                        new_nav_ori = self.update_price_unit(fund_id, fund_id_list)
                        if new_nav_ori is None:
                                print(f'    fund_id {fund_id} does not have nav idx {idx}')
                                break
                        if (new_nav_ori.adjPrice / new_nav_ori.price).unique().tolist() == [1]:
                            print(f'    fund_id {fund_id} does not have divident idx {idx}')
                            break
                        new_nav = new_nav_ori.rename(columns={'navDate':'datetime','adjPrice':'before_adj_price'}).set_index('datetime').sort_index()[['before_adj_price','price']]
                        td = pd.to_datetime(new_nav.index)
                        td = [i.date() for i in td]
                        new_nav.index = td
                        adj_factor_df = nav_div_factor[nav_div_factor.product_id==fund_id][['ex_date','factor']].set_index('ex_date')
                        adj_factor_df.index.name = 'datetime'
                        new_nav.loc[:,'factor'] = new_nav.before_adj_price / new_nav.price
                        new_nav = new_nav[['factor']]
                        new_nav = new_nav.round(4).drop_duplicates().iloc[1:]
                        new_nav = new_nav / new_nav.iloc[0]
                        _adj_factor_df = adj_factor_df.loc[new_nav.index[0]:]
                        new_nav = new_nav * _adj_factor_df.iloc[0]
                        con = new_nav.index > _adj_factor_df.index[-1]
                        if not np.any(con):
                            print(f'    fund_id {fund_id} does not have new adj factor idx {idx}')
                            break
                        new_nav = new_nav[con].copy()
                        new_nav = new_nav.reset_index().rename(columns={'index':'ex_date'})
                        new_nav.loc[:,'product_id'] = fund_id
                        print(f'    fund_id {fund_id} idx {idx} total {len(fund_id_list)} finish')
                        if new_nav is not None:
                            result.append(new_nav)
                    except Exception as e:
                        _count += 1
                        print(e)
                        time.sleep(1)
                    else:
                        break
            if result:
                df_adj_new = pd.concat(result)
                self.data_helper._upload_raw(df_adj_new, OSFundNAVDivFactor.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(f'oversea_fund_nav')
        return False

    def update_index_price(self):
        # todo change file location here
        folder = '/Users/huangkejia/Downloads/Data/'
        excel_name = '8.0_海外基金基准_210220_回溯2000版本_unlink.xlsx'
        sheet_name = 'Benchmark dailydata'
        df = pd.read_excel(folder+excel_name,sheet_name=sheet_name).replace(dic)
        with RawDatabaseConnector().managed_session() as db_session:        
            query = db_session.query(
                OSIndexPrice
            )
            index_price_exsited = pd.read_sql(query.statement, query.session.bind)
        index_price_exsited = index_price_exsited.drop(columns=['_update_time'], errors='ignore')
        dic = {'VNIndex':'VNINDEX','dax':'DAX'}
        fund_cols = df.columns.tolist()
        fund_col_len = len(fund_cols)
        result = []
        for i in range(fund_col_len):
            if i % 2 == 0:
                _fund_cols = fund_cols[i:i+2]
                _df = df[_fund_cols]
                _index_id = _df[_fund_cols[0]].values[0].replace(' Index', '').replace(' index', '')
                _df = _df.iloc[3:].dropna()
                if _df.empty:
                    continue
                _df.columns = ['datetime','close']
                con = [ not isinstance(_, int) for _ in _df.datetime]
                _df = _df[con]
                td = pd.to_datetime(_df.datetime)
                td = [i.date() for i in td]
                _df.datetime = td
                if _index_id in dic.keys():
                    _index_id = dic[_index_id]
                _df.loc[:,'codes'] = _index_id
                _df_exsited = index_price_exsited[index_price_exsited.codes == _index_id]
                _df_new = _df[~_df.datetime.isin(_df_exsited.datetime)]
                result.append(_df_new)
        df_result = pd.concat(result).drop_duplicates(subset=['datetime','codes'])
        df_result.to_sql('oversea_index_price', RawDatabaseConnector().get_engine(), index=False, if_exists='append')

    def check_adj_factor(self):
        # 复权因子有问题的代码
        fund_adj_fac = RawDataApi().get_os_fund_nav_div_factor().drop(columns='_update_time')
        product_id_list = fund_adj_fac.product_id.unique()
        problem_fund_id = []
        for product_id in product_id_list:
            _df = fund_adj_fac[fund_adj_fac.product_id == product_id].dropna()
            if _df.empty:
                continue
            _df.loc[:,'next_single_factor'] = _df['single_factor'].shift(-1)
            _df.loc[:,'calc_factor'] = _df.factor * _df.next_single_factor
            _df.loc[:,'next_factor'] = _df['factor'].shift(-1)
            _df.loc[:,'rate'] = abs(_df['calc_factor'] / _df['next_factor'] - 1)
            if round(_df.rate.max(),4) > 0:
                #print(_df)
                problem_fund_id.append(product_id)

        # 正确的数据
        change_result = []
        for product_id in problem_fund_id:
            _df = fund_adj_fac[fund_adj_fac.product_id == product_id].dropna()
            _df.loc[:,'next_single_factor'] = _df['single_factor'].shift(-1)
            _df.loc[:,'calc_factor'] = _df.factor * _df.next_single_factor
            _df.loc[:,'next_factor'] = _df['factor'].shift(-1)
            _df_not_null = _df.dropna().copy()
            if _df.empty:
                continue
            fac = _df.factor.values[0]
            res = [fac]
            for next_i in _df_not_null.next_single_factor:
                fac = fac * next_i
                res.append(fac)
            _df.loc[:,'right_factor'] = res
            _df.loc[:,'rate'] = abs(_df['right_factor'] / _df['factor'] - 1)
            _df = _df[_df.rate.round(4) > 0].copy()
            change_result.append(_df)

        # 替换正确的数据
        right_df = pd.concat(change_result)[['product_id','ex_date','factor']]
        change_fund_list = right_df.product_id.unique().tolist()
        session = sessionmaker(RawDatabaseConnector().get_engine())
        db_session = session()
        for row in db_session.query(OSFundNAVDivFactor).filter(OSFundNAVDivFactor.product_id.in_(change_fund_list)).all():
            target_df = right_df[(right_df.product_id == row.product_id) & (right_df.ex_date == row.ex_date)]
            if target_df.empty:
                continue
            target = target_df.factor.values[0]
            #print(f'{row.product_id} {row.ex_date} {target}')
            row.factor = float(target)
        db_session.commit()
        db_session.close()  