

from typing import Optional, List
import os
import traceback
import time

import pandas as pd

from ...util.mail_retriever import MailAttachmentRetriever, IMAP_SPType, UID_FILE_NAME
from ...util.wechat_bot import WechatBot
from ...constant import EMailParserType
from ..wrapper.mysql import DerivedDatabaseConnector
from ..view.derived_models import FOFNav  # , FOFUnconfirmedNav
from ..api.derived import DerivedDataApi
from .parser_runner import ParserRunner


class HedgeFundNAVReader:

    def __init__(self, manager_id: str, read_dir: str, user_name: str, password: str):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        self._read_dir = read_dir
        assert os.path.isdir(self._read_dir), f'arg dump_dir should be a directory (now){self._read_dir}'

        self._manager_id = manager_id
        self._user_name = user_name
        self._password = password
        self._wechat_bot = WechatBot()

        self._parser_runner = ParserRunner(manager_id, EMailParserType.E_PARSER_NAV)

    def _notify_error_event(self, err_msg: str):
        print(f'[read_navs_and_dump_to_db] {err_msg}')
        self._wechat_bot.send_hedge_fund_nav_update_failed(err_msg)

    def read_navs_and_dump_to_db(self):
        try:
            with open(os.path.join(self._read_dir, UID_FILE_NAME), 'rb') as f:
                uid_last = f.read()
                if not uid_last:
                    uid_last = None
        except Exception as e:
            self._notify_error_event(f'read uid file failed (e){e}, use None instead(read all emails)')
            uid_last = None

        try:
            mar = MailAttachmentRetriever(self._read_dir, ['xls', 'xlsx', 'pdf'])
            data = mar.get_excels(IMAP_SPType.IMAP_QQ, self._user_name, self._password, uid_last)
        except Exception as e:
            self._notify_error_event(f'FATAL ERROR!! get new data of hedge fund nav failed (e){e}')
            return

        uid_last_succeed: Optional[bytes] = None
        df_list: List[pd.DataFrame] = []
        for name, comp_date in data.items():
            uid, file_path = comp_date

            try:
                df = self._parser_runner.parse_file(file_path, name)
                if df is None:
                    raise NotImplementedError('unknown hedge fund/fof nav file from attachment')
            except Exception as e:
                self._notify_error_event(f'{e} (parse) (name){name} (file_path){file_path}')
                continue

            try:
                df = df.drop(columns=['fof_name', 'v_nav'], errors='ignore')
                df['manager_id'] = self._manager_id
                print(df)
                df = self._dump_to_db(df)
                if df is not None:
                    df_list.append(df)
                else:
                    print(f'[read_navs_and_dump_to_db] duplicated data, do not process it (name){name}')
                # 走到这里都认为是已经处理完了这条数据
                uid_last_succeed = uid
                time.sleep(1)
            except Exception as e:
                traceback.print_exc()
                self._notify_error_event(f'{e} (dump) (name){name} (file_path){file_path}')
                break

        if df_list:
            try:
                whole_df = pd.concat(df_list).set_index('fof_id')
                print(whole_df)
            except Exception as e:
                self._notify_error_event(f'{e} (concat)')
                whole_df = None
            else:
                # self._wechat_bot.send_hedge_fund_nav_update(whole_df)
                print(f'[read_navs_and_dump_to_db] done (uid_last){uid_last_succeed} (df){whole_df}')
        else:
            whole_df = None
            print(f'[read_navs_and_dump_to_db] no new data this time, done (uid_last){uid_last_succeed}')
        # 记录下成功的最后一个uid
        if whole_df is not None and uid_last_succeed is not None:
            with open(os.path.join(self._read_dir, UID_FILE_NAME), 'wb') as f:
                f.write(uid_last_succeed)
            return whole_df
        return

    def _dump_to_db(self, df: pd.DataFrame):
        def _check_after_merged(x: pd.Series, now_df: pd.DataFrame):
            try:
                now_data = now_df[(now_df.fof_id == x.fof_id) & (now_df.datetime == x.datetime)]
                if now_data[['nav', 'acc_net_value']].iloc[0].astype('float64').equals(x[['nav', 'acc_net_value']].astype('float64')):
                    return pd.Series(dtype='object')
                else:
                    return x
            except (KeyError, IndexError):
                return x

        assert df.datetime.nunique() == 1, 'should have single datetime'
        # now_df = DerivedDataApi().get_fof_nav_unconfirmed(manager_id=self._manager_id, fof_id_list=list(df.fof_id.unique()))
        now_df = DerivedDataApi().get_fof_nav(manager_id=self._manager_id, fof_id_list=list(df.fof_id.unique()))
        if now_df is not None and not now_df.empty:
            # 同产品同日期的净值如果已经存在了且没有变化 就不写DB了
            now_df = now_df.drop(columns=['update_time', 'create_time', 'is_deleted', 'adjusted_nav', 'ta_factor', 'volume', 'mv', 'ret']).sort_values(by=['manager_id', 'fof_id', 'datetime']).drop_duplicates(subset=['manager_id', 'fof_id', 'datetime'], keep='last')
            now_df = now_df.astype({'nav': 'float64', 'acc_net_value': 'float64'})
            df = df.reindex(columns=now_df.columns).astype(now_df.dtypes.to_dict())
            df = df.merge(now_df, how='left', on=['manager_id', 'fof_id', 'datetime', 'nav', 'acc_net_value'], indicator=True, validate='one_to_one')
            df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            if df.empty:
                return
            # FIXME 没想到特别好的方法 遍历每一行再check一下
            df['datetime'] = pd.to_datetime(df.datetime, infer_datetime_format=True).dt.date
            df = df.apply(_check_after_merged, axis=1, now_df=now_df)
            if df.empty:
                return
            df = df.set_index(['manager_id', 'fof_id', 'datetime'])
            print(df)
            df.update(now_df.set_index(['manager_id', 'fof_id', 'datetime']), overwrite=False)
            df = df.reset_index()
            df['datetime'] = df.datetime.map(lambda x: x.date())
            print(df)
            # 先删后添
            for fof_id in df.fof_id.unique():
                DerivedDataApi().delete_fof_nav(manager_id=self._manager_id, fof_id=fof_id, date_list=df[df.fof_id == fof_id].datetime.to_list())
                # DerivedDataApi().delete_fof_nav_unconfirmed(manager_id=self._manager_id, fof_id=fof_id, date_list=df[df.fof_id == fof_id].datetime.to_list())
        df.to_sql(FOFNav.__table__.name, DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')
        # df.to_sql(FOFUnconfirmedNav.__table__.name, DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')
        return df


if __name__ == '__main__':
    try:
        email_data_dir = os.environ['SURFING_EMAIL_DATA_DIR']
        user_name = os.environ['SURFING_EMAIL_USER_NAME']
        password = os.environ['SURFING_EMAIL_PASSWORD']
    except KeyError as e:
        import sys
        sys.exit(f'can not found enough params in env (e){e}')

    MANAGER_ID = 'py1'

    hf_nav_r = HedgeFundNAVReader(MANAGER_ID, email_data_dir, user_name, password)
    hf_nav_r.read_navs_and_dump_to_db()
