
from typing import Dict, List, Set, Optional
import requests
import json
import datetime
import time
import traceback

import pandas as pd

from .config import SurfingConfigurator


class WechatBot(object):

    _SEND_PARTIALLY_UNIT = 4000

    def __init__(self):
        self.wechat_webhook = SurfingConfigurator().get_wechat_webhook_settings('wechat_webhook')
        assert self.wechat_webhook is not None, 'could not find wechat_webhook config'
        self._wechat_err_msg_webhook = SurfingConfigurator().get_wechat_webhook_settings('wechat_webhook_err_msg')
        if self._wechat_err_msg_webhook is None:
            self._wechat_err_msg_webhook = self.wechat_webhook

    def send(self, markdown_content, webhook=None):
        if webhook is None and self.wechat_webhook is None:
            return

        print(markdown_content)
        i = 0
        while i < len(markdown_content):
            md_part = markdown_content[i:i+WechatBot._SEND_PARTIALLY_UNIT]
            if i > 0:
                # 非第一部分 加一行注解
                md_part = '**(接上文)**' + md_part
            if i + len(md_part) < len(markdown_content):
                # 如果没办法一次性过把剩余部分发完 倒着找一下换行符
                pos = md_part.rfind('\n')
                if pos != -1:
                    # 如果找到了 这次只发送到这里
                    md_part = md_part[:pos]
                    i += pos
                else:
                    # 否则就直接全发走
                    i += len(md_part)
                # 加一个还有后文的注解
                md_part += '\n**(接下文)**'
            else:
                # 表示这次可以一次性把剩余部分全发完
                i += len(md_part)
            # Send markdown content
            # print(md_part)
            message = {
                'msgtype': 'markdown',
                'markdown': {
                    'content': md_part
                }
            }
            try:
                res = requests.post(url=self.wechat_webhook if webhook is None else webhook, data=json.dumps(message), timeout=20)
                print(res)
                time.sleep(4)
            except Exception as e:
                print(e)
                traceback.print_exc()

    def send_data_update_status(self, dt, tag, failed_tasks, updated_count):
        # Send markdown content
        markdown_content = f'{dt} {tag}已完成数据更新，'
        if len(failed_tasks) == 0:
            markdown_content += '所有数据更新成功'
        else:
            markdown_content += '以下数据更新失败: '
            for key, task_names in failed_tasks.items():
                if len(task_names) > 0:
                    markdown_content += f'\n>{key}: <font color=\"error\">{task_names}</font>'

        markdown_content += '\n更新数据统计: '
        for key, item_count in updated_count.items():
            for item, count in item_count.items():
                markdown_content += f'\n>{key}.{item}: <font color=\"info\">{count}</font>'

        return self.send(markdown_content)

    def send_new_fund_list(self, dt, new_funds: Dict[str, str], new_delisted_funds: Dict[str, str], indexes_that_become_invalid: Optional[Set[str]]):
        markdown_content = f'#### {dt}'
        if new_funds is None or new_delisted_funds is None:
            markdown_content += f' **<font color=\"warning\">获取今日新基金或摘牌基金列表失败</font>**'
        else:
            if new_funds:
                markdown_content += f'\n>新基金({len(new_funds)}): <font color=\"info\">{new_funds}</font>'
            else:
                markdown_content += f'\n>无新基金'
            if new_delisted_funds:
                markdown_content += f'\n\n>摘牌基金({len(new_delisted_funds)}): <font color=\"info\">{new_delisted_funds}</font>'
            else:
                markdown_content += f'\n\n>无摘牌基金'
        if indexes_that_become_invalid is not None and indexes_that_become_invalid:
            markdown_content += f'\n\n\n>**失效指数({len(indexes_that_become_invalid)}, 请注意处理!!): <font color=\"warning\">{indexes_that_become_invalid}</font>**'
        self.send(markdown_content)

    def send_fund_list_that_set_end_date_failed(self, dt, fund_list: List[str]):
        markdown_content = f'#### {dt} <font color=\"warning\">设置下列基金摘牌日期失败，请手工修改</font>'
        markdown_content += f'\n>**{fund_list}**'
        self.send(markdown_content)

    def send_untreated_new_fund_list(self, dt, fund_list: List[str]):
        markdown_content = f'#### {dt}'
        if fund_list:
            markdown_content += f'\n>**本周累计有下列新基金未处理其 FundInfo & FundBenchmark({len(fund_list)}): <font color=\"warning\">{fund_list}</font>**'
        else:
            markdown_content += f'\n><font color=\"info\">本周无未处理其 FundInfo & FundBenchmark 的新基金</font>'
        self.send(markdown_content)

    def send_dump_to_s3_result(self, dt, failed_tables: List[str], failed_dfs: List[str]):
        markdown_content = f'#### {dt}'
        if failed_dfs:
            markdown_content += f'\n>**同步下列df失败: <font color=\"warning\">{failed_dfs}</font>**'
        else:
            markdown_content += f'\n><font color=\"info\">同步所有df成功</font>'
        if failed_tables:
            markdown_content += f'\n>**同步下列table失败: <font color=\"warning\">{failed_tables}</font>**'
        else:
            markdown_content += f'\n><font color=\"info\">同步所有table成功</font>'
        self.send(markdown_content)

    def send_update_factor_result(self, dt, tag, failed_factors: List[str]):
        markdown_content = f'#### {dt}'
        if failed_factors:
            markdown_content += f'\n>**下列{tag} factor更新失败: <font color=\"warning\">{failed_factors}</font>**'
        else:
            markdown_content += f'\n><font color=\"info\">所有{tag} factor更新成功</font>'
        self.send(markdown_content)

    def send_hedge_fund_nav_update(self, df: pd.DataFrame):
        markdown_content = '#### <font color=\"info\">以下产品净值数据更新成功</font>'
        markdown_content += f'\n>{df.to_markdown()}'
        self.send(markdown_content)

    def send_hedge_fund_nav_update_failed(self, err_msg: str):
        markdown_content = '#### <font color=\"warning\">产品净值数据更新错误！！</font>'
        markdown_content += f'\n>**err msg:** {err_msg}'
        self.send(markdown_content, webhook=self._wechat_err_msg_webhook)

    def send_hedge_fund_info(self, fof_id: str, fund_id: str, fund_name: str, latest_nav_date: datetime.date, fund_data, holding_data, ret_data_with_last_date, ret_date_with_last_pub):
        _FUND_DATA_NAME_DICT = {
            'start_date': '成立日期',
            'days': '成立天数',
            'nav': '最新净值',
            'total_ret': '成立以来收益率',
            'annualized_ret': '年化收益率',
            'annualized_vol': '年化波动率',
            'mdd': '最大回撤',
            'sharpe': '夏普比率',
        }
        _HOLDING_DATA_NAME_DICT = {
            'start_date': '首次买入日期',
            'days': '持有天数',
            'mv': '最新市值',
            'avg_cost': '平均成本',
            'v_nav': '虚拟净值',
            'total_ret': '持仓收益率',
            'annualized_ret': '年化收益率',
            'annualized_vol': '年化波动率',
            'mdd': '最大回撤',
            'sharpe': '夏普比率',
        }

        markdown_content = f'### <font color=\"warning\">{fund_name}</font>({fund_id}) <font color=\"comment\">{latest_nav_date}</font>'
        for k, v in fund_data.items():
            markdown_content += f'\n><font color=\"info\">{_FUND_DATA_NAME_DICT[k]}: </font>**{v}**'
        if ret_data_with_last_date:
            markdown_content += f'\n><font color=\"info\">相对上一个基准日期({ret_data_with_last_date["date"]})收益率: </font>**{ret_data_with_last_date["rr"]}**'
        if ret_date_with_last_pub:
            markdown_content += f'\n><font color=\"info\">相对上一个净值日期({ret_date_with_last_pub["date"]})收益率: </font>**{ret_date_with_last_pub["rr"]}**'
        markdown_content += f'\n>'
        markdown_content += f'\n>**<font color=\"comment\">持仓信息(FOF {fof_id})</font>**'
        for k, v in holding_data.items():
            markdown_content += f'\n><font color=\"info\">{_HOLDING_DATA_NAME_DICT[k]}: </font>**{v}**'
        self.send(markdown_content)

    def send_hedge_fund_info_failed(self, fof_id: str, fund_id: str, err_msg: str):
        markdown_content = f'#### <font color=\"warning\">计算 {fund_id} 信息(FOF: {fof_id})失败</font>'
        markdown_content += f'\n>**err msg:** {err_msg}'
        self.send(markdown_content)

    def send_fof_nav_update(self, df):
        markdown_content = f'#### <font color=\"info\">FOF净值数据更新</font>'
        markdown_content += f'\n>**{df.to_markdown()}**'
        self.send(markdown_content)

    def send_fof_nav_update_failed(self, fof_id: str, err_msg: str):
        markdown_content = f'#### <font color=\"info\">{fof_id}净值数据更新失败！！</font>'
        markdown_content += f'\n>**err msg:** {err_msg}'
        self.send(markdown_content)

    def send_fof_info(self, fof_id: str, latest_nav_date: datetime.date, fund_data):
        _FUND_DATA_NAME_DICT = {
            'start_date': '成立日期',
            'days': '成立天数',
            'mv': '最新市值',
            'nav': '最新净值',
            'total_ret': '成立以来收益率',
            'annualized_ret': '年化收益率',
            'annualized_vol': '年化波动率',
            'mdd': '最大回撤',
            'sharpe': '夏普比率',
        }

        markdown_content = f'### FOF <font color=\"warning\">{fof_id}</font> <font color=\"comment\">{latest_nav_date}</font>'
        # markdown_content += '\n#### <font color=\"comment\">成立以来</font>'
        for k, v in fund_data.items():
            markdown_content += f'\n><font color=\"info\">{_FUND_DATA_NAME_DICT[k]}: </font>**{v}**'
        self.send(markdown_content)

    def send_fof_info_failed(self, fof_id: str, err_msg: str):
        markdown_content = f'#### <font color=\"warning\">计算FOF {fof_id} 信息失败</font>'
        markdown_content += f'\n>**err msg:** {err_msg}'
        self.send(markdown_content)

    def send_hedge_and_product_nav_update(self, manager_id: str, r1: pd.DataFrame, r2: pd.DataFrame):
        if r1 is not None:
            markdown_content = f'#### <font color=\"warning\">{manager_id} 底层资产净值更新</font>'
            markdown_content += r1.to_markdown(tablefmt="grid")
            self.send(markdown_content, webhook=self._wechat_err_msg_webhook)
        if r2 is not None:
            markdown_content = f'#### <font color=\"warning\">{manager_id} 产品净值更新</font>'
            markdown_content += r2.to_markdown(tablefmt="grid")
            self.send(markdown_content, webhook=self._wechat_err_msg_webhook)

    def send_research_data_update(self, tag: str, datas: Dict[str, int]):
        markdown_content = f'#### 研究数据({tag})更新成功({len(datas.keys())})'
        for k, v in datas.items():
            markdown_content += f'\n><font color=\"info\">{k}: </font>**{v}**'
        self.send(markdown_content)

    def send_refinancing_key_info(self, dt, stocks, key):
        if stocks:
            markdown_content = f'#### {dt}'
            markdown_content += f'\n下列上市公司发布再融资预案，发行对象中包括 **<font color=\"warning\">{key}</font>**'
            markdown_content += f'\n>**<font color=\"info\">{stocks}</font>**'
            self.send(markdown_content)

    def send_refinancing_impl_key_info(self, dt, stocks, key):
        if stocks:
            markdown_content = f'#### {dt}'
            markdown_content += f'\n下列上市公司发布再融资实施公告，获配对象中包括 **<font color=\"warning\">{key}</font>**'
            markdown_content += f'\n>**<font color=\"info\">{stocks}</font>**'
            self.send(markdown_content)
