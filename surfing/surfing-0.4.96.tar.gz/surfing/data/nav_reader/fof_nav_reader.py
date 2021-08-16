

from typing import Optional, List, Dict, Any, Set
import os
import traceback
import time
# import datetime

from sqlalchemy.orm import sessionmaker
import pandas as pd
# import numpy as np

from ...util.mail_retriever import MailAttachmentRetriever, UID_FILE_NAME
from ...util.wechat_bot import WechatBot
from ...util.calculator import Calculator
from ...constant import EMailParserType
from ..wrapper.mysql import BasicDatabaseConnector, DerivedDatabaseConnector
from ..view.basic_models import FOFInfo, HedgeFundEmailRaw
from ..view.derived_models import FOFUnconfirmedNav, FOFNav
from ..api.basic import BasicDataApi
from ..api.derived import DerivedDataApi
from .parser_runner import ParserRunner


class FOFNAVReader:

    def __init__(self, info: Dict[str, Any]):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        email_data_base_dir = os.environ['SURFING_EMAIL_DATA_DIR']

        self._read_dir = os.path.join(email_data_base_dir, f"attachments/{info['manager_id']}_{info['fof_id']}")
        os.makedirs(self._read_dir, exist_ok=True)
        assert os.path.isdir(self._read_dir), f'arg dump_dir should be a directory (now){self._read_dir}'

        self._manager_id = info['manager_id']
        fof_info = BasicDataApi().get_fof_info(self._manager_id)
        assert fof_info is not None and not fof_info.empty, f'get fof info of manager_id {self._manager_id} failed'
        self._hedge_list: Set[str] = set(fof_info[fof_info.asset_type == 'hedge'].fof_id.array)
        self._product_list: Set[str] = set(fof_info[fof_info.asset_type == 'production'].fof_id.array)

        self._fof_id = info['fof_id']
        self._sp_uri = f"{info['server']}:{info['port']}"
        self._user_name = info['email']
        self._password = info['password']
        self._wechat_bot = WechatBot()

        self._parser_runner = ParserRunner(self._manager_id, EMailParserType.E_PARSER_NAV)

    def _notify_error_event(self, err_msg: str):
        print(f'[read_navs_and_dump_to_db] {err_msg}')
        self._wechat_bot.send_hedge_fund_nav_update_failed(err_msg)

    def read_navs_and_dump_to_db(self, is_full: bool = False):
        if not is_full:
            try:
                with open(os.path.join(self._read_dir, UID_FILE_NAME), 'rb') as f:
                    uid_last = f.read()
                    if not uid_last:
                        uid_last = None
            except FileNotFoundError:
                uid_last = None
            except Exception as e:
                self._notify_error_event(f'read uid file failed (e){e}, use None instead(read all emails) (manager_id){self._manager_id} (fof_id){self._fof_id}')
                uid_last = None
        else:
            uid_last = None

        try:
            mar = MailAttachmentRetriever(self._read_dir, ['xls', 'xlsx', 'pdf'])
            data = mar.get_excels(self._sp_uri, self._user_name, self._password, uid_last)
        except Exception as e:
            self._notify_error_event(f'FATAL ERROR!! get new data of hedge fund nav failed (e){e} (manager_id){self._manager_id} (fof_id){self._fof_id}')
            return

        uid_last_succeed: Optional[bytes] = None
        df_list: List[pd.DataFrame] = []
        for name, comp_date in data.items():
            uid, file_path = comp_date

            try:
                df = self._parser_runner.parse_file(file_path, name)
                if df is None:
                    raise NotImplementedError(f'unknown hedge fund nav file from attachment (manager_id){self._manager_id} (fof_id){self._fof_id}')
            except Exception as e:
                self._notify_error_event(f'{e} (parse) (name){name} (file_path){file_path} (manager_id){self._manager_id} (fof_id){self._fof_id}')
                continue

            try:
                df = df.drop(columns=['fof_name'], errors='ignore')
                df['manager_id'] = self._manager_id

                def _transform_fof_id(x: str) -> str:
                    real_fof_id = BasicDataApi().get_hedge_fund_alias(self._manager_id, x)
                    if real_fof_id is not None and not real_fof_id.empty:
                        return real_fof_id.fund_id.array[0]
                    else:
                        return x
                df['fof_id'] = df.fof_id.map(_transform_fof_id)

                if self._manager_id == 'py1':
                    # 暂时先只存 py1 产品的底层资产的净值数据
                    self._dump_proprietary_to_db(df)

                # 这里需要 drop 掉虚拟净值
                df = df.drop(columns='v_nav', errors='ignore')
                r1 = self._dump_hedge_to_db(df[df.fof_id.isin(self._hedge_list)])
                if r1 is not None:
                    df_list.append(r1)
                r2 = self._dump_fof_to_db(df[(df.fof_id == self._fof_id) & (df.fof_id.isin(self._product_list))])

                if r1 is None and r2 is None:
                    print(f'[read_navs_and_dump_to_db] duplicated data, do not process it (name){name} (manager_id){self._manager_id} (fof_id){self._fof_id}')
                else:
                    self._wechat_bot.send_hedge_and_product_nav_update(self._manager_id, r1, r2)
                # 走到这里都认为是已经处理完了这条数据
                uid_last_succeed = uid

                abnormal_fof_ids = df[~df.fof_id.isin(self._hedge_list.union(self._product_list))]
                if not abnormal_fof_ids.empty:
                    self._notify_error_event(f'got unknown fof_ids {abnormal_fof_ids.fof_id.to_list()} (dump) (name){name} (file_path){file_path} (manager_id){self._manager_id} (fof_id){self._fof_id}')
                time.sleep(1)
            except Exception as e:
                traceback.print_exc()
                self._notify_error_event(f'{e} (dump) (name){name} (file_path){file_path} (manager_id){self._manager_id} (fof_id){self._fof_id}')
                break

        if df_list:
            try:
                whole_df = pd.concat(df_list)  # .set_index('fof_id')
                whole_df = whole_df.drop_duplicates(subset=['manager_id', 'fof_id', 'datetime'], keep='last')
                print(whole_df)
                # self._wechat_bot.send_hedge_fund_nav_update(whole_df)
            except Exception as e:
                self._notify_error_event(f'{e} (concat) (manager_id){self._manager_id} (fof_id){self._fof_id}')
                whole_df = None
            else:
                print(f'[read_navs_and_dump_to_db] done (uid_last){uid_last_succeed} (manager_id){self._manager_id} (fof_id){self._fof_id}')
        else:
            whole_df = None
            print(f'[read_navs_and_dump_to_db] no new data this time, done (uid_last){uid_last_succeed} (manager_id){self._manager_id} (fof_id){self._fof_id}')
        # 记录下成功的最后一个uid
        if uid_last_succeed is not None:
            with open(os.path.join(self._read_dir, UID_FILE_NAME), 'wb') as f:
                f.write(uid_last_succeed)

        if whole_df is not None and not whole_df.empty:
            # 这里只更新 hedge 类型的FOF
            print(f'[read_navs_and_dump_to_db] to update fof info (manager_id){self._manager_id} (fof_id){self._fof_id} (hedge_fund_list){whole_df.fof_id.unique()}')
            for fof_id in whole_df.fof_id.unique():
                fof_nav = DerivedDataApi().get_fof_nav(self._manager_id, [fof_id])
                if fof_nav is not None and not fof_nav.empty:
                    fof_nav = fof_nav.drop(columns=['update_time', 'create_time', 'is_deleted']).set_index('datetime').sort_index()
                    fof_latest_acc_nav = fof_nav.acc_net_value.array[-1]
                    fof_latest_adjusted_nav = fof_nav.adjusted_nav.array[-1]
                    nav_of_fof = fof_nav.adjusted_nav
                    res_status = Calculator.get_stat_result(nav_of_fof.index, nav_of_fof.array)

                    Session = sessionmaker(BasicDatabaseConnector().get_engine())
                    db_session = Session()
                    fof_info_to_set = db_session.query(FOFInfo).filter((FOFInfo.manager_id == self._manager_id) & (FOFInfo.fof_id == fof_id)).one_or_none()
                    fof_info_to_set.net_asset_value = float(fof_nav.nav.array[-1]) if not pd.isnull(fof_nav.nav.array[-1]) else None
                    fof_info_to_set.acc_unit_value = float(fof_latest_acc_nav) if not pd.isnull(fof_latest_acc_nav) else None
                    fof_info_to_set.adjusted_net_value = float(fof_latest_adjusted_nav) if not pd.isnull(fof_latest_adjusted_nav) else None
                    # 这里可能不太好算这俩
                    # fof_info_to_set.total_volume = float(self._total_shares) if not pd.isnull(self._total_shares) else None
                    # fof_info_to_set.total_amount = float(self._total_net_assets) if not pd.isnull(self._total_net_assets) else None
                    fof_info_to_set.latest_cal_date = res_status.end_date
                    fof_info_to_set.ret_year_to_now = float(res_status.recent_year_ret) if not pd.isnull(res_status.recent_year_ret) else None
                    fof_info_to_set.ret_total = float(res_status.cumu_ret) if not pd.isnull(res_status.cumu_ret) else None
                    fof_info_to_set.ret_ann = float(res_status.annualized_ret) if not pd.isnull(res_status.annualized_ret) else None
                    fof_info_to_set.mdd = float(res_status.mdd) if not pd.isnull(res_status.mdd) else None
                    fof_info_to_set.sharpe = float(res_status.sharpe) if not pd.isnull(res_status.sharpe) else None
                    fof_info_to_set.vol = float(res_status.annualized_vol) if not pd.isnull(res_status.annualized_vol) else None
                    fof_info_to_set.last_increase_rate = float(res_status.last_increase_rate) if not pd.isnull(res_status.last_increase_rate) else None
                    fof_info_to_set.last_before_date = nav_of_fof.index.array[-2]
                    db_session.commit()
                    db_session.close()
        return whole_df

    def _dump_proprietary_to_db(self, df: pd.DataFrame):
        def _check_after_merged(x: pd.Series, now_df: pd.DataFrame):
            try:
                now_data = now_df[(now_df.fund_id == x.fund_id) & (now_df.datetime == x.datetime)]
                if now_data[['nav', 'acc_net_value', 'v_nav']].iloc[0].astype('float64').equals(x[['nav', 'acc_net_value', 'v_nav']].astype('float64')):
                    return pd.Series(dtype='object')
                else:
                    return x
            except (KeyError, IndexError):
                return x

        if 'v_nav' not in set(df.columns.array):
            return
        df = df[df.v_nav.notnull()]
        if df.empty:
            return
        df = df.rename(columns={'fof_id': 'fund_id'})
        df['fof_id'] = self._fof_id
        assert df.datetime.nunique() == 1, 'should have single datetime'
        now_df = BasicDataApi().get_hedge_fund_email_raw(self._manager_id, list(df.fund_id.unique()))
        if now_df is not None and not now_df.empty:
            # 同产品同日期的净值如果已经存在了且没有变化，就不写DB了
            now_df = now_df.drop(columns=['update_time', 'create_time', 'is_deleted']).sort_values(by=['manager_id', 'fof_id', 'fund_id', 'datetime']).drop_duplicates(subset=['manager_id', 'fof_id', 'fund_id', 'datetime'], keep='last')
            now_df = now_df.astype({'nav': 'float64', 'acc_net_value': 'float64', 'v_nav': 'float64'})
            df = df.reindex(columns=now_df.columns).astype(now_df.dtypes.to_dict())
            df = df.round(6).merge(now_df.round(6), how='left', on=['manager_id', 'fof_id', 'fund_id', 'datetime', 'nav', 'acc_net_value', 'v_nav'], indicator=True, validate='one_to_one')
            df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            if df.empty:
                return
            # FIXME 没想到特别好的方法 遍历每一行再check一下
            df['datetime'] = pd.to_datetime(df.datetime, infer_datetime_format=True).dt.date
            df = df.apply(_check_after_merged, axis=1, now_df=now_df)
            if df.empty:
                return
            df = df.set_index(['manager_id', 'fof_id', 'fund_id', 'datetime'])
            print(f'proprietary before update: {df}')
            df.update(now_df.set_index(['manager_id', 'fof_id', 'fund_id', 'datetime']), overwrite=False)
            df = df.reset_index()
            df['datetime'] = df.datetime.map(lambda x: x.date())
            print(f'proprietary after update: {df}')
            # 先删后添
            for fund_id in df.fund_id.unique():
                BasicDataApi().delete_hedge_fund_email_raw(manager_id=self._manager_id, fof_id=self._fof_id, fund_id=fund_id, date_list=df[df.fund_id == fund_id].datetime.to_list())
        df.to_sql(HedgeFundEmailRaw.__table__.name, BasicDatabaseConnector().get_engine(), index=False, if_exists='append')
        return df

    def _dump_hedge_to_db(self, df: pd.DataFrame):
        def _check_after_merged(x: pd.Series, now_df: pd.DataFrame):
            try:
                now_data = now_df[(now_df.fof_id == x.fof_id) & (now_df.datetime == x.datetime)]
                if now_data[['nav', 'acc_net_value', 'adjusted_nav']].iloc[0].astype('float64').equals(x[['nav', 'acc_net_value', 'adjusted_nav']].astype('float64')):
                    return pd.Series(dtype='object')
                else:
                    return x
            except (KeyError, IndexError):
                return x

        if df.empty:
            return

        assert df.datetime.nunique() == 1, 'should have single datetime'
        now_df = DerivedDataApi().get_fof_nav(self._manager_id, list(df.fof_id.unique()))
        if now_df is not None and not now_df.empty:
            # 同产品同日期的净值如果已经存在了且没有变化，就不写DB了
            now_df = now_df.drop(columns=['update_time', 'create_time', 'is_deleted', 'ta_factor', 'volume', 'mv', 'ret']).sort_values(by=['manager_id', 'fof_id', 'datetime']).drop_duplicates(subset=['manager_id', 'fof_id', 'datetime'], keep='last')
            now_df = now_df.astype({'nav': 'float64', 'acc_net_value': 'float64', 'adjusted_nav': 'float64'})
            df = df.reindex(columns=now_df.columns).astype(now_df.dtypes.to_dict())
            df = df.round(6).merge(now_df.round(6), how='left', on=['manager_id', 'fof_id', 'datetime', 'nav', 'acc_net_value', 'adjusted_nav'], indicator=True, validate='one_to_one')
            df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            if df.empty:
                return
            # FIXME 没想到特别好的方法 遍历每一行再check一下
            df['datetime'] = pd.to_datetime(df.datetime, infer_datetime_format=True).dt.date
            df = df.apply(_check_after_merged, axis=1, now_df=now_df)
            if df.empty:
                return
            df = df.set_index(['manager_id', 'fof_id', 'datetime'])
            print(f'hedge before update: {df}')
            df.update(now_df.set_index(['manager_id', 'fof_id', 'datetime']), overwrite=False)
            df = df.reset_index()
            df['datetime'] = df.datetime.map(lambda x: x.date())
            print(f'hedge after update: {df}')
            # 先删后添
            for fof_id in df.fof_id.unique():
                DerivedDataApi().delete_fof_nav(manager_id=self._manager_id, fof_id=fof_id, date_list=df[df.fof_id == fof_id].datetime.to_list())
        df.to_sql(FOFNav.__table__.name, DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')
        return df

    def _dump_fof_to_db(self, df: pd.DataFrame):
        def _check_after_merged(x: pd.Series, now_df: pd.DataFrame):
            try:
                now_data = now_df[(now_df.fof_id == x.fof_id) & (now_df.datetime == x.datetime)]
                if now_data[['nav', 'acc_net_value', 'v_nav']].iloc[0].astype('float64').equals(x[['nav', 'acc_net_value', 'v_nav']].astype('float64')):
                    return pd.Series(dtype='object')
                else:
                    return x
            except (KeyError, IndexError):
                return x

        if df.empty:
            return

        # fof nav 里已经有了的就不再处理了
        fof_nav = DerivedDataApi().get_fof_nav(self._manager_id, list(df.fof_id.unique()))
        df = df.merge(fof_nav[['fof_id', 'datetime']], how='left', indicator=True)
        df = df[df._merge == 'left_only'].drop(columns=['_merge'])
        print(f'fof after check: {df}')

        if df.empty:
            return

        assert df.datetime.nunique() == 1, 'should have single datetime'
        now_df = DerivedDataApi().get_fof_nav_unconfirmed(self._manager_id, list(df.fof_id.unique()))
        if now_df is not None and not now_df.empty:
            # 同产品同日期的净值如果已经存在了且没有变化，就不写DB了
            now_df = now_df.drop(columns=['update_time', 'create_time', 'is_deleted']).sort_values(by=['manager_id', 'fof_id', 'datetime']).drop_duplicates(subset=['manager_id', 'fof_id', 'datetime'], keep='last')
            now_df = now_df.astype({'nav': 'float64', 'acc_net_value': 'float64', 'v_nav': 'float64'})
            df = df.reindex(columns=now_df.columns).astype(now_df.dtypes.to_dict())
            df = df.merge(now_df, how='left', on=['manager_id', 'fof_id', 'datetime', 'nav', 'acc_net_value', 'v_nav'], indicator=True, validate='one_to_one')
            df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            if df.empty:
                return
            # FIXME 没想到特别好的方法 遍历每一行再check一下
            df['datetime'] = pd.to_datetime(df.datetime, infer_datetime_format=True).dt.date
            df = df.apply(_check_after_merged, axis=1, now_df=now_df)
            if df.empty:
                return
            df = df.set_index(['manager_id', 'fof_id', 'datetime'])
            print(f'fof before update: {df}')
            df.update(now_df.set_index(['manager_id', 'fof_id', 'datetime']), overwrite=False)
            df = df.reset_index()
            df['datetime'] = df.datetime.map(lambda x: x.date())
            print(f'fof after update: {df}')
            # 先删后添
            for fof_id in df.fof_id.unique():
                DerivedDataApi().delete_fof_nav_unconfirmed(manager_id=self._manager_id, fof_id=fof_id, date_list=df[df.fof_id == fof_id].datetime.to_list())
        df.to_sql(FOFUnconfirmedNav.__table__.name, DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')
        return df


if __name__ == '__main__':
    import requests

    url = 'https://fof.prism-advisor.com/api/v1/manager_mail/email_task'
    verify_token = 'jisn401f7ac837da42b97f613d789819f37bee6a'

    res = requests.post(
        url=url,
        data={
            'verify_token': verify_token,
        }
    )
    for one in res.json()['data']:
        print(one)
        fof_nav_r = FOFNAVReader(one)
        fof_nav_r.read_navs_and_dump_to_db()
