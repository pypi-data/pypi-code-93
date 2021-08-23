from pymongo import InsertOne
from pymongo.errors import BulkWriteError
from seleya.DataAPI.db.mongodb import MongoDBManager
from seleya config.default_config import MONGO_DB
from seleya import *


class FetchEngine(object):
    def __init__(self):
        self._MONGO_DB = MONGO_DB
        self._mongo_client = MongoDBManager(self._MONGO_DB)
        self._sly_engine = DBFetchEngine.create_engine('sly')
        
    def max_cid(self, uid):
        query = {'uid': uid}
        cid = self._mongo_client[self._MONGO_DB['db']].esg_combine.distinct('cid')
        cid = max(cid) if len(cid) > 0 else 10000
        return cid + 1
    
        
    def write_combine(self, combine, name='user_combine'):
        requests = [InsertOne(d) for d in combine.to_dict(orient='record')]
        self._mongo_client[self._MONGO_DB['db']][name].bulk_write(
                        requests, bypass_document_validation=True)
        
    def fetch_combine(self, uid, columns):
        query = {'uid': uid}
        results = self._mongo_client[self._MONGO_DB['db']].user_combine.find(
            query, dict(zip(columns, [1 for i in range(0,len(columns))])))
        results = pd.DataFrame(results)
        results = results.drop(['_id'],axis=1) if not results.empty else pd.DataFrame(
            columns=columns)
        return results
    
    def fetch_metrics(self, table_name, codes, columns):
        query = {'code':{'$in':codes}}
        results = self._mongo_client[self._MONGO_DB['db']][table_name].find(
            query, dict(zip(columns, [1 for i in range(0,len(columns))])))
        results = pd.DataFrame(results)
        results = results.drop(['_id'],axis=1) if not results.empty else pd.DataFrame(
            columns=columns)
        return results
    
    
    def fetch_indicator_detail(self, key, indicator):
        return ESGMetricsDetailFactory(self._sly_engine).result(
            key=key, codes=indicator, columns=['category','column_name'])
        
        
fetch_engine = FetchEngine()

def custom_combine(uid, data):
    if 'RIC Code' not in data.columns or 'Portfolio Weight' not in data.columns:
        return False
    current_id = fetch_engine.max_cid(uid=uid)
    data = data[['RIC Code', 'ISIN', 'Portfolio Weight']].rename(
                columns={'RIC Code':'code','ISIN':'isin','Portfolio Weight':'weight'})
    data['cid'] = current_id
    data['uid'] = uid
    fetch_engine.write_combine(data)
    return True
    
    
def esg_portfolio(uid, indicator, key, cid=None):
    def _weighted(data):
        weighted = data[['weight']] / data[['weight']].sum()
        weighted['code'] = data['code']
        return weighted
    ##提取指标信息
    indicator_info = fetch_engine.fetch_indicator_detail(key=key, 
                                                  indicator=indicator)
    if indicator_info.empty:
        return
    
    ##提取组合信息
    combine_info = fetch_engine.fetch_combine(
        uid=uid,columns=['code', 'cid', 'isin', 'weight'])
    codes = combine_info.code.unique().tolist()
    ##按类别提取
    grouped = indicator_info.groupby('category')
    res = []
    for name,group in grouped:
        columns = ['date','code'] + group['column_name'].unique().tolist()
        print('esg_metrics_' + name.lower())
        data = fetch_engine.fetch_metrics('esg_metrics_' + name.lower(), 
                                          codes, columns)
        columns = [col for col in data.columns.tolist() if col not in ['code','date']]
        for col in columns:
            for cid, combine in combine_info.groupby('cid'):
                df = combine.merge(data[['date','code',col]],on=['code'])
                df = df.dropna(subset=[col])
                new_weight = df.set_index('date').groupby(level=['date']).apply(lambda x: _weighted(x))
                new_df = new_weight.reset_index().merge(df[['date','code','cid', col]], on=['date','code'])
                result = new_df.set_index(['date']).groupby(level=['date']).apply(lambda x: (x[col] * x['weight']).sum())
                result.name = 'portfolio'
                result = result.reset_index()
                result['name'] = col
                result['uid'] = uid
                result['cid'] = cid
                res.append(result)
    portfolio_data = pd.concat(res,axis=0)
    fetch_engine.write_combine(combine=portfolio_data, name='esg_portfolio')
    return portfolio_data