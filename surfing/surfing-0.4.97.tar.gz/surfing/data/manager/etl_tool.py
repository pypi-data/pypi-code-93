
import os
import dataclasses
import time
from typing import List, Optional
from collections import defaultdict

import pandas as pd

from ..._version import __version__
from ...constant import SectorType, IndexPriceSource
from ...util.config import SurfingConfigurator, AWSSettings
from ..wrapper.mysql import RawDatabaseConnector, BasicDatabaseConnector, DerivedDatabaseConnector
from ..view.raw_models import CSIndexComponent
from ..view.basic_models import FundInfo, TradingDayList, IndexInfo, IndexPrice, FundNav, Fund_size_and_hold_rate, FundBenchmark, FundIPOStats
from ..view.basic_models import FundConvStats, FundStatusLatest, FundOpenInfo
from ..view.derived_models import FundIndicator, FundIndicatorAnnual, IndexValuationLongTerm, FundIndicatorWeekly
from ..view.derived_models import FundIndicatorMonthly, BarraCNE5FactorReturn, FundManagerScore, FundManagerInfo, FundManagerFundRank
from .data_tables import FundDataTables
from .score import FundScoreManager


_DEFAULT_BUCKET_NAME = 'tl-fund-dm'

# 存储版本号文件的文件名
_VERSION_FILE_NAME = '_version.csv'


class S3ETLTool:
    def __init__(self):
        try:
            self._conf = SurfingConfigurator().get_aws_settings()
        except AssertionError as e:
            print(f'{e}, use default value')
            self._conf = AWSSettings.get_default_config()
        print('s3 config: ')
        print(f'    {self._conf}')
        if self._conf.etl_tool_bucket_name is None or not self._conf.etl_tool_bucket_name:
            bucket_name = _DEFAULT_BUCKET_NAME
        else:
            bucket_name = self._conf.etl_tool_bucket_name
        # 原始(指从数据库里读出来未加以任何调整的)table的uri on s3
        self._raw_s3_bucket_uri: str = f's3://{bucket_name}/raw_tables'
        # dm调整后的data的uri on s3
        self._s3_bucket_uri: str = f's3://{bucket_name}/dm'
        print('bucket uri: ')
        print(f'    {self._raw_s3_bucket_uri}')
        print(f'    {self._s3_bucket_uri}')
        # 在to_parquet/read_parquet中通过storage_options传递如下参数的方法不好用，这里直接设置环境变量
        os.environ['AWS_ACCESS_KEY_ID'] = self._conf.aws_access_key_id
        os.environ['AWS_SECRET_ACCESS_KEY'] = self._conf.aws_secret_access_key
        os.environ['AWS_DEFAULT_REGION'] = self._conf.region_name


class SynchronizerS3ForDM(S3ETLTool):
    '''将数据同步到S3的工具'''

    # DM中需要使用的raw table
    _RAW_TABLE_LIST = [
        CSIndexComponent,
    ]
    # DM中需要使用的basic table
    _BASIC_TABLE_LIST = [
        FundInfo,
        TradingDayList,
        IndexInfo,
        IndexPrice,
        FundNav,
        Fund_size_and_hold_rate,
        FundBenchmark,
        FundIPOStats,
        FundConvStats,
        FundStatusLatest,
        FundOpenInfo,
    ]
    # DM中需要使用的derived table
    _DERIVED_TABLE_LIST = [
        FundIndicator,
        FundIndicatorAnnual,
        IndexValuationLongTerm,
        FundIndicatorWeekly,
        FundIndicatorMonthly,
        BarraCNE5FactorReturn,
        FundManagerScore,
        FundManagerInfo,
        FundManagerFundRank,
    ]

    # 如果不传dm, 可以使用dump_all_tables
    # 否则也可以使用dump_all_dfs
    def __init__(self, dm=None):
        super().__init__()

        if dm is not None:
            # 存下来dts中所有的字段和值
            self._data_tables_dict = dataclasses.asdict(dm.dts)
            # 存下来dm的score manager
            self._score_manager = dm._score_manager

    def _dump_dts(self) -> List[str]:
        '''dump all dfs in dts'''

        failed_tables: List[str] = []
        for name, data in self._data_tables_dict.items():
            if not isinstance(data, pd.DataFrame) or (data is None):
                # 这里不处理df以外的数据
                continue

            _t0 = time.time()
            try:
                # if name == 'cs_index_component':
                #     data['id_cat'] = data.id_cat.transform(lambda x: x.value)
                # elif name == 'index_info':
                #     data['price_source'] = data.price_source.transform(lambda x: x.value)
                data.to_parquet(f'{self._s3_bucket_uri}/{name}.parquet', compression='gzip')
            except Exception as e:
                print(f'WARNING!! dump df {name} to s3 failed (err_msg){e}')
                failed_tables.append(name)
            _t1 = time.time()
            print(f'cost {_t1 - _t0}s, table {name} to s3 done')
        return failed_tables

    def _dump_misc(self) -> List[str]:
        '''dump all datas except dfs in dts and all datas in score manager'''

        # dts部分
        failed_tables: List[str] = []
        for name, data in self._data_tables_dict.items():
            if isinstance(data, pd.DataFrame) or (data is None):
                # 这里只处理df以外的数据
                continue
            if name in ('mng_best_fund', 'mng_index_list'):
                # 这两个data是在fund_manager_processor_advanced里dump的
                continue

            # 由于df写parquet很方便，因此这里我们做一些类型转换，把类型均转为df
            if isinstance(data, set) or isinstance(data, list):
                df = pd.DataFrame.from_dict({name: list(data)})
            elif isinstance(data, dict):
                df = pd.Series(data).to_frame(name)
            else:
                print(f'ERROR!! do not recognize the type of data (type){type(data)} (name){name}')
                failed_tables.append(name)
                continue

            _t0 = time.time()
            try:
                df.to_parquet(f'{self._s3_bucket_uri}/_ndf_{name}.parquet', compression='gzip')
            except Exception as e:
                print(f'WARNING!! dump data {name} to s3 failed (err_msg){e}')
                failed_tables.append(name)
            _t1 = time.time()
            print(f'cost {_t1 - _t0}s, data {name} to s3 done')

        # score manager部分
        for name in ('score_cache', 'score_raw_cache', 'score_manager_cache'):
            _t0 = time.time()
            try:
                df = pd.Series(self._score_manager.__dict__[name]).to_frame(name)
                if name == 'score_manager_cache':
                    df['score_manager_cache'] = df.score_manager_cache.transform(lambda x: {k: v.to_dict() for k, v in x.items()})
                df.to_parquet(f'{self._s3_bucket_uri}/_ndf_{name}.parquet', compression='gzip')
            except Exception as e:
                print(f'WARNING!! dump data {name} to s3 failed (err_msg){e}')
                failed_tables.append(name)
            _t1 = time.time()
            print(f'cost {_t1 - _t0}s, , data {name} to s3 done')
        return failed_tables

    def _dump_whole_table_data(self, session, table_list, processor=None) -> List[str]:
        '''dump whole data of tables from db'''

        def _fetch_whole_table(session, view):
            query = session.query(view)
            return pd.read_sql(query.statement, query.session.bind)

        failed_tables: List[str] = []
        for table in table_list:
            name = table.__table__.name
            try:
                print(f'to dump table {name}')
                _t0 = time.time()
                data = _fetch_whole_table(session, table)
                if processor is not None:
                    data = processor(table, data)
                _t1 = time.time()
                print(f'cost {_t1 - _t0}s, and send table {name} to s3')
                data.to_parquet(f'{self._raw_s3_bucket_uri}/{name}.parquet', compression='gzip', index=False)
                _t2 = time.time()
                print(f'cost {_t2 - _t1}s, table {name} to s3 done')
            except Exception as e:
                print(f'WARNING!! dump table {name} failed (err_msg){e}')
                failed_tables.append(name)
        return failed_tables

    def _dump_raw_table(self) -> List[str]:
        def _raw_table_processor(table, data):
            # if table == CSIndexComponent:
            #     data['id_cat'] = data.id_cat.transform(lambda x: x.value)
            return data

        print('to dump raw tables')
        with RawDatabaseConnector().managed_session() as session:
            failed_tables: List[str] = self._dump_whole_table_data(session, self._RAW_TABLE_LIST, _raw_table_processor)
        print('dump raw tables done')
        return failed_tables

    def _dump_basic_table(self) -> List[str]:
        def _basic_table_processor(table, data):
            # if table == IndexInfo:
            #     data['price_source'] = data.price_source.transform(lambda x: x.value)
            return data

        print('to dump basic tables')
        with BasicDatabaseConnector().managed_session() as session:
            failed_tables: List[str] = self._dump_whole_table_data(session, self._BASIC_TABLE_LIST, _basic_table_processor)
        print('dump basic tables done')
        return failed_tables

    def _dump_derived_table(self) -> List[str]:
        print('to dump derived tables')
        with DerivedDatabaseConnector().managed_session() as session:
            failed_tables: List[str] = self._dump_whole_table_data(session, self._DERIVED_TABLE_LIST)
        print('dump derived tables done')
        return failed_tables

    def dump_one_df(self, name: str) -> bool:
        _t0 = time.time()
        try:
            data = self._data_tables_dict[name]
        except KeyError as e:
            print(e)
            return False

        if not isinstance(data, pd.DataFrame):
            # 这里不处理df以外的数据
            print(f'{name} is not a df, can not dump it')
            return False

        try:
            # if name == 'cs_index_component':
            #     data['id_cat'] = data.id_cat.transform(lambda x: x.value)
            # elif name == 'index_info':
            #     data['price_source'] = data.price_source.transform(lambda x: x.value)
            data.to_parquet(f'{self._s3_bucket_uri}/{name}.parquet', compression='gzip')
        except Exception as e:
            print(f'WARNING!! dump df {name} to s3 failed (err_msg){e}')
        _t1 = time.time()
        print(f'cost {_t1 - _t0}s, table {name} to s3 done')
        return True

    def dump_all_dfs(self) -> List[str]:
        try:
            pd.DataFrame({'version': __version__}, index=['now']).to_csv(f'{self._s3_bucket_uri}/{_VERSION_FILE_NAME}')
            print(f'version {__version__} to s3 done')
        except Exception as e:
            print(f'WARNING!! version {__version__} to s3 failed (err_msg){e}')
            return ['version']

        failed_tables: List[str] = self._dump_dts()
        failed_tables += self._dump_misc()
        print(f'dump all dfs done (failed tables){failed_tables}')
        return failed_tables

    def dump_all_tables(self) -> List[str]:
        try:
            pd.DataFrame({'version': __version__}, index=['now']).to_csv(f'{self._raw_s3_bucket_uri}/{_VERSION_FILE_NAME}')
            print(f'version {__version__} to s3 done')
        except Exception as e:
            print(f'WARNING!! version {__version__} to s3 failed (err_msg){e}')
            return ['version']

        failed_tables: List[str] = self._dump_raw_table()
        failed_tables += self._dump_basic_table()
        failed_tables += self._dump_derived_table()
        print(f'dump all tables done (failed tables){failed_tables}')
        return failed_tables


class S3RetrieverForDM(S3ETLTool):
    '''从S3获取数据的工具'''

    def __init__(self, activation: Optional[List[str]] = None):
        super().__init__()
        # 默认先不激活
        self._activation: S3RetrieverForDM = activation

    @property
    def is_activated(self) -> bool:
        # 只有self._activation是空列表的情况才返回True; 非空表示一部分table需要从mysql读取
        return self._activation is not None and not self._activation

    def fetch_table(self, query, post_processor=None):
        table_name = query.selectable.froms[0].name
        # 如果没有开启的话，直接从mysql读取
        if self._activation is None or (table_name in self._activation):
            print(f'loading data of {table_name} from sql')
            return pd.read_sql(query.statement, query.session.bind).drop(columns='_update_time', errors='ignore')

        try:
            print(f'loading data of {table_name} from s3')
            df = pd.read_parquet(f'{self._raw_s3_bucket_uri}/{table_name}.parquet').drop(columns='_update_time', errors='ignore')
            columns_need = []
            col_desc = query.column_descriptions
            for one in col_desc:
                # 这里表明是查询全表，而不是只查询特定几列
                if one['type'] == one['entity']:
                    break
                # 把查询的特定几列的列名字都记下来
                columns_need.append(one['name'])
            else:
                # 只取查询的特定几列
                df = df[columns_need]

            if post_processor is not None:
                df = post_processor(df)

            # 这里为了与从DB里读出来的数据内容一样，需要做一个转换
            if table_name == 'cs_index_component':
                df['id_cat'] = df.id_cat.transform(lambda x: SectorType(x))
            elif table_name == 'index_info':
                df['price_source'] = df.price_source.transform(lambda x: IndexPriceSource(x))
            return df
        except Exception as e:
            print(f'WARNING!! fetch table {table_name} from s3 failed (err_msg){type(e).__name__}: {e}, try mysql')
            # TODO: 如果这里DB也失败，应该也需要适当的处理
            return pd.read_sql(query.statement, query.session.bind).drop(columns='_update_time', errors='ignore')

    def retrieve_dts(self, data_tables: FundDataTables, candidates=None) -> List[str]:
        failed_tables: List[str] = []
        for field in dataclasses.fields(data_tables):
            # 这里不处理df以外的数据
            if field.type != pd.DataFrame:
                continue
            # 以下df理论上没必要保存，可以自己生成出来且较快
            if field.name in ['index_fund_indicator_pack','stock_ipo_data','conv_bond_ipo_data','stock_ipo_data_detail','conv_bond_ipo_data_detail','stock_ipo_info','conv_bond_ipo_info']:
                continue
            name = field.name

            if candidates and name not in candidates:
                continue

            _t0 = time.time()
            try:
                if name in ['mng_indicator_score', 'fund_indicator_score']:
                    _bucket_name = 'tl-fund-dm'
                    _s3_bucket_uri: str = f's3://{_bucket_name}/dm'
                    data = pd.read_parquet(f'{_s3_bucket_uri}/{name}.parquet')
                else:
                    data = pd.read_parquet(f'{self._s3_bucket_uri}/{name}.parquet')
                    # if name == 'cs_index_component':
                    #     data['id_cat'] = data.id_cat.transform()
                    # elif name == 'index_info':
                    #     data['price_source'] = data.price_source.transform()
                data_tables.__dict__[name] = data
            except (FileNotFoundError, PermissionError, Exception) as e:
                print(f'WARNING!! retrieve df {name} failed (err_msg){e}')
                failed_tables.append(name)
            _t1 = time.time()
            print(f'cost {_t1 - _t0}s, retrieve df {name} from s3 done')
        return failed_tables

    def _retrieve_all_dts(self, data_tables: FundDataTables) -> List[str]:
        _t0 = time.time()
        failed_tables: List[str] = self.retrieve_dts(data_tables)
        _t1 = time.time()
        print(f'all dts total cost {_t1 - _t0}s (failed_tables){failed_tables}')
        return failed_tables

    def retrieve_misc(self, dm, candidates=None) -> List[str]:
        failed_tables: List[str] = []
        for field in dataclasses.fields(dm.dts):
            # 这里不处理df以外的数据
            if field.type == pd.DataFrame:
                continue
            name = field.name

            if candidates and name not in candidates:
                continue

            _t0 = time.time()
            try:
                # 把我们保存的df转换回原来的类型
                if name in ('fund_list', 'all_fund_list', 'fund_ipo_list', 'fund_conv_list', 'index_list', 'index_date_list'):
                    df = pd.read_parquet(f'{self._s3_bucket_uri}/_ndf_{name}.parquet')
                    data = set(df.to_dict(orient='list')[name])
                    if name == 'index_date_list':
                        data = sorted(data)
                elif name in ('mng_best_fund','mng_index_list'):
                    df = pd.read_parquet(f'{self._s3_bucket_uri}/{name}.parquet')
                    data = {}
                    for col in df:
                        _df = df[[col]]
                        data[col] = pd.DataFrame(_df[col].values.tolist(), index=_df.index)
                elif name in ('fund_index_map', 'fund_end_date_dict'):
                    df = pd.read_parquet(f'{self._s3_bucket_uri}/_ndf_{name}.parquet')
                    data = df.to_dict()[name]
                elif name in ('stock_ipo_data','conv_bond_ipo_data','stock_ipo_data_detail','conv_bond_ipo_data_detail','stock_ipo_info','conv_bond_ipo_info'):
                    data = {}
                else:
                    raise FileNotFoundError(f'do not support retrieve this data {name} from s3')
                dm.dts.__dict__[name] = data
            except (FileNotFoundError, PermissionError, Exception) as e:
                print(f'WARNING!! retrieve data {name} failed (err_msg){e}')
                failed_tables.append(name)
            _t1 = time.time()
            print(f'cost {_t1 - _t0}s, retrieve data {name} from s3 done')
        return failed_tables

    def _retrieve_all_misc(self, dm) -> List[str]:
        _t0 = time.time()
        failed_tables: List[str] = self.retrieve_misc(dm)
        _t1 = time.time()
        print(f'all misc total cost {_t1 - _t0}s (failed_tables){failed_tables}')
        return failed_tables

    def retrieve_fund_score(self, score_manager: FundScoreManager):
        def remove_values_in_dict(item):
            if not isinstance(item, dict):
                return

            to_delete = []
            for k, v in item.items():
                if v is None:
                    to_delete.append(k)
                else:
                    remove_values_in_dict(v)
            for one in to_delete:
                del item[one]

        failed_tables: List[str] = []
        for name in ('score_cache', 'score_raw_cache', 'score_manager_cache'):
            _t0 = time.time()
            try:
                data = pd.read_parquet(f'{self._s3_bucket_uri}/_ndf_{name}.parquet').to_dict(into=defaultdict(dict))[name]
                # 转成df的过程中可能产生了很多None，这里把这些都干掉
                remove_values_in_dict(data)
                if name == 'score_manager_cache':
                    for v in data.values():
                        for lk, lv in v.items():
                            v[lk] = pd.Series(lv).rename_axis('manager_id')
                score_manager.__dict__[name] = data
            except (FileNotFoundError, PermissionError) as e:
                print(f'WARNING!! retrieve data {name} failed (err_msg){e}')
                failed_tables.append(name)
            _t1 = time.time()
            print(f'cost {_t1 - _t0}s, retrieve data {name} from s3 done')
        return failed_tables

    def retrieve_all_dfs(self, dm):
        try:
            version = pd.read_csv(f'{self._s3_bucket_uri}/{_VERSION_FILE_NAME}', index_col=0).at['now', 'version']
        except Exception as e:
            print(f'WARNING!! retrieve version info from s3 failed (err_msg){e}')
            return ['version']

        print(f'to retrieve all datas of version {version}')

        failed_datas: List[str] = self._retrieve_all_dts(dm.dts)
        failed_datas += self._retrieve_all_misc(dm)
        # failed_datas += self.retrieve_fund_score(dm._score_manager)
        return failed_datas
