from collections import defaultdict

import numpy as np
import pandas as pd

import PySQL
from Util.MySqlHelper import MysqlHelper

from Core.Log import Log
from Core.EntityBase import EntityBase
from Util.JobHelper import *
from Util.EmailHelper import QaErrorEmailHelper
import inspect


class QaBase:
    def __init__(self, **kwargs):
        self.log = kwargs.get('log', Log(self.__class__.__name__))
        self.run_result = {}
        self.qa_dfs = {}
        self.qa_name = None
        self.qa_report_file = None
        self.mysql = None

    def get_history_qa_result(self, qa_type: str, record_count=10):
        qas = []
        sql = '''
        select B.qa_name, B.qa_type, B.RunDate, B.InsertUpdateTime, B.tid, B.qa_id, B.result_key, B.result_value from 
        (SELECT * FROM qa.qa_category where qa_name = '{}' and qa_type = '{}' order by RunDate desc limit {} ) as A  
        join
        (SELECT * FROM qa.qa_info) as B 
        on A.tid = B.qa_id order by B.qa_id desc
                '''.format(self.qa_name, qa_type, record_count)
        check_key = defaultdict(dict)
        for each in self.mysql.select(sql):
            run_date = each.get('RunDate')
            qa_id = each.get('qa_id')
            check_key['{}__{}'.format(run_date, qa_id)][each['result_key']] = each['result_value']
        for each, value in check_key.items():
            qas.append(pd.DataFrame(value, index=[each]))
        if not qas:
            return pd.DataFrame()
        if len(qas) == 1:  # std is nan if we have only one history record, duplicate it so that the std change to 0.0
            qas.append(qas[0].copy())
        qa_history = pd.concat(qas).sort_index(ascending=False)
        return qa_history

    def check_qa_result(self, qa_now: pd.Series, check_method: str = '3_sigma',
                        **kwargs):  # check qa result using 3 sigema princ
        if check_method == '3_sigma':
            self.check_qa_result_use_3_sigma(qa_now)
        else:
            raise ValueError('unknown check method', str(check_method))

    def check_qa_result_use_3_sigma(self, qa_now: pd.Series):  # check qa result using 3 sigema princ
        qa_type = qa_now['qa_type']
        qa_history = self.get_history_qa_result(qa_type)
        if qa_history.empty:
            self.log.error("we haven't got any history records yet", qa_type)
            return

        # check field info
        diff1 = set(qa_now.index) - set(qa_history.columns)
        if len(diff1) != 1:
            self.log.error('we got new fields in this run', diff1)

        diff2 = set(qa_history.columns) - set(qa_now.index)
        if len(diff2) != 0:
            self.log.error('we lost fields in this run', diff2)

        # check data count info
        for col in qa_history:
            try:
                if col == 'rundate':
                    continue
                data_history = qa_history[col]
                std = data_history.std()
                mean = data_history.mean()
                if mean is np.nan:
                    self.log.info('Col %s in Nan' % col)
                    continue
                if col in qa_now.index:
                    data_this_run = qa_now[col]
                else:
                    self.log.error('''PAY ATTENTION !!!! We don't have column {} in this run'''.format(col))
                    continue

                if mean - 3 * std <= data_this_run <= mean + 3 * std:
                    pass
                else:
                    self.log.error(
                        "Column %s not qualified\n mean %s std %s data this run %s" % (
                            str(col), str(mean), str(std), str(data_this_run)))
                    self.log.error("increase/decrease ratio is %s" % str((data_this_run - mean) / mean))
            except Exception as e:
                self.log.error("failed to process col %s except: %s" % (str(col), str(e)))

    def save_qa_result(self, qa_result: pd.Series, run_date, **kwargs):
        qa_type = qa_result['qa_type']
        del qa_result['qa_type']  # qa type val is a string
        qa_category = QaCategoryEntity()
        qa_category.qa_name = self.qa_name
        qa_category.RunDate = run_date if run_date else kwargs.get('rundate')
        qa_category.qa_type = qa_type
        qa_id = self.mysql.save(qa_category)
        qa_result_dict = qa_result.to_dict()
        for key, val in qa_result_dict.items():
            qa_info = QaInfoEntity()
            qa_info.update(qa_category)
            qa_info.result_key = key
            qa_info.result_value = val
            qa_info.qa_id = qa_id
            self.mysql.save(qa_info)

        self.report_qa(qa_type)

    @staticmethod
    def read_data_from_file(file) -> pd.DataFrame:
        '''
        user pandas to read data from file
        :param file:
        :return: pandas data frame
        '''
        if str(file).split('.')[-1] == 'csv':
            df = pd.read_csv(file)
        elif str(file).split('.')[-1] == 'parquet':
            df = pd.read_parquet(file)
        else:
            raise ValueError('Unknown file type', file)
        return df

    def read_data_from_mysql(self, **kwargs):
        pass

    def before_run(self, **kwargs):  # do something before run
        self.qa_name = self.__module__ + self.__class__.__name__
        if debug():
            stack = inspect.stack()
            self.qa_report_file = os.path.join(os.path.dirname(get_stack_frame(stack)[1]), 'QaReports',
                                               '{}.html'.format(self.qa_name))
        else:
            self.qa_report_file = os.path.join(os.path.expanduser('~'), 'QaReports', '{}.html'.format(self.qa_name))

        try:
            from airflow.providers.mysql.hooks.mysql import MySqlHook
            self.log.info('using airflow.providers.mysql.hooks.mysql.MySqlHook')
        except ImportError:
            self.log.info('not using airflow v2')
            try:
                from airflow.hooks.mysql_hook import MySqlHook
                self.log.info('using airflow.hooks.mysql_hook.MySqlHook')
            except ImportError:
                self.log.info('not using airflow v1')
                from Util.MySqlHelper import MySqlHook
                self.log.info('using Util.MysqlHelper.MySqlHook')
        mysql_hook = MySqlHook('mysql_conn_qa')
        self.mysql = MysqlHelper(mysql_hook=mysql_hook)
        self.mysql.connect()

    def on_run(self, **kwargs):
        pass

    def run(self, **kwargs):
        self.before_run()
        self.run_result['run_result'] = self.on_run(**kwargs)
        self.after_run(**kwargs)
        return self.run_result

    def after_run(self, **kwargs):  # do something after run
        self.save_qa_report()
        dag = kwargs.get('dag')
        if dag:
            email = dag.default_args.get('email')
            if email:
                email_result = self.send_qa_error_email(email)
                self.run_result['email_result'] = email_result

    def report_qa(self, qa_type):
        from tabulate import tabulate
        df_report = self.get_history_qa_result(qa_type)
        report_msg_consle = tabulate(df_report, showindex=True, headers='keys', tablefmt='psql')
        print('\n' + '{}:'.format(qa_type) + '\n' + report_msg_consle)
        self.qa_dfs[qa_type] = df_report

    def send_qa_error_email(self, to):
        if debug():
            return
        if not self.log.error_list:
            self.log.info('nothing wrong happened')
            return
        error_html = pd.DataFrame(self.log.error_list).to_html()
        QaErrorEmailHelper(to=to, html_content=error_html, subject=self.qa_name + 'LogError').send_email()
        return to

    def send_qa_df_email(self, to):
        with open(self.qa_report_file, encoding='utf-8') as fh:
            qa_df_html = fh.read()
        QaErrorEmailHelper(to=to, html_content=qa_df_html, subject=self.qa_name + 'DataFrame').send_email()
        return to

    def save_qa_report(self):
        qa_htmls = []
        for qa_type, qa_df in self.qa_dfs.items():
            html = qa_df.reset_index(drop=True).style.bar().render()
            qa_htmls.append('<h2>{}: </h2>'.format(qa_type) + html)
        report_str = '\n'.join(qa_htmls)
        if not os.path.exists(os.path.dirname(self.qa_report_file)):
            os.makedirs(os.path.dirname(self.qa_report_file))
        with open(self.qa_report_file, 'w', encoding='utf-8') as fh:
            fh.write(report_str)

    def check_count_info(self, df: pd.DataFrame, fields=None, run_date=None, **kwargs):
        if not fields:
            fields = df.columns
        run_date = run_date if run_date else \
            (kwargs.get('rundate') if kwargs.get('rundate') else df['RunDate'].unique()[0])
        count_info = df[fields].count()
        count_info['qa_type'] = 'count_info'
        self.check_qa_result(count_info)
        self.save_qa_result(count_info, run_date)

    def check_null_info(self, df: pd.DataFrame, fields=None, run_date=None, **kwargs):
        if not fields:
            fields = df.columns
        run_date = run_date if run_date else \
            (kwargs.get('rundate') if kwargs.get('rundate') else df['RunDate'].unique()[0])
        null_count_info = df[fields].isna().sum()
        null_count_info['qa_type'] = 'null_count_info'
        self.check_qa_result(null_count_info)
        self.save_qa_result(null_count_info, run_date)

    def check_unique_count_info(self, df: pd.DataFrame, fields=None, run_date=None, **kwargs):
        if not fields:
            fields = df.columns
        run_date = run_date if run_date else (
            kwargs.get('rundate') if kwargs.get('rundate') else df['RunDate'].unique()[0])

        unique_count_info = df[fields].nunique()
        unique_count_info['qa_type'] = 'unique_count_info'
        self.check_qa_result(unique_count_info)
        self.save_qa_result(unique_count_info, run_date)


@PySQL.table(table_name='qa_category')
class QaCategoryEntity(EntityBase):
    qa_name = None
    qa_type = None
    RunDate = None
    InsertUpdateTime = None


@PySQL.table(table_name='qa_info')
class QaInfoEntity(EntityBase):
    qa_id = None
    qa_name = None
    qa_type = None
    result_key = None
    result_value = None
    RunDate = None
    InsertUpdateTime = None


if __name__ == '__main__':
    t = QaCategoryEntity()
    t.qa_name = 1
    t.qa_type = 2
    print(t.values())
    print(t.keys())
