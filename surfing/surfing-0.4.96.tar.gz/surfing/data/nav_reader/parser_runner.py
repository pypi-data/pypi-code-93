
from typing import Optional, List, Dict
from types import FunctionType
import os
import traceback
import re
import io
import json

import pandas as pd
import numpy as np
import pdfplumber

from ...constant import EMailParserType
from ..api.basic import BasicDataApi


EMAIL_DATA_COLUMNS_DICT = {
    '基金代码': 'fof_id',
    '产品代码': 'fof_id',
    '资产代码': 'fof_id',
    '基金名称': 'fof_name',
    '产品名称': 'fof_name',
    '资产名称': 'fof_name',
    '账套名称': 'fof_name',
    '基金份额净值': 'nav',
    '单位净值': 'nav',
    '计提前单位净值': 'nav',
    '实际净值': 'nav',
    '基金单位净值': 'nav',
    '资产份额净值(元)': 'nav',
    '本级别单位净值': 'nav',
    '今日单位净值': 'nav',
    '基金份额累计净值': 'acc_net_value',
    '累计单位净值': 'acc_net_value',
    '累计净值': 'acc_net_value',
    '资产份额累计净值(元)': 'acc_net_value',
    '本级别累计单位净值': 'acc_net_value',
    '虚拟后净值': 'v_nav',
    '虚拟净值': 'v_nav',
    '计提后单位净值': 'v_nav',
    '虚拟计提净值': 'v_nav',
    '虚拟后单位净值': 'v_nav',
    '日期': 'datetime',
    '净值日期': 'datetime',
    '业务日期': 'datetime',
    '估值日期': 'datetime',
}


class LogCollector:

    def __init__(self):
        # 暂时先简单就是个 list
        self._log_container: List[str] = []

    def log(self, content: str):
        print(content)
        self._log_container.append(content)

    def get_out(self) -> List[str]:
        return self._log_container


class ParserRunner(LogCollector):

    def __init__(self, manager_id: str, parser_type: EMailParserType):
        super().__init__()

        self._manager_id = manager_id
        self._parser_type = parser_type

        parsers_manager: Optional[pd.DataFrame] = BasicDataApi().get_email_parser_exec(manager_id)
        assert parsers_manager is not None and not parsers_manager.empty, f'get email parsers exec info of {manager_id} failed (parser_type){parser_type}'

        if parsers_manager.shape[0] > 1:
            parsers_manager = parsers_manager[parsers_manager.manager_id.notna()]

        priority_info = json.loads(parsers_manager.p_priority_info.array[0])
        assert str(parser_type) in priority_info, f'no {parser_type} exec info of {manager_id}'
        parsers_list_with_priority: List[str] = priority_info[str(parser_type)]
        print(f'(manager_id){manager_id} {parsers_list_with_priority}')

        parsers_code: Optional[pd.DataFrame] = BasicDataApi().get_email_parser_code(parsers_list_with_priority)
        assert parsers_code is not None and not parsers_code.empty, f'get email parsers code of {manager_id} failed (parser_type){parser_type}'

        self._parsers: Dict[str, str] = parsers_code.set_index('id')['p_code'].to_dict()
        self.log(f'got parsers {self._parsers.keys()} to run (parser_type){parser_type}')

    def parse_data(self, datas: io.BytesIO, file_name: str = '') -> Optional[pd.DataFrame]:
        for p_id, p_code in self._parsers.items():
            self.log(f'try to run parser {p_id}')
            try:
                # FIXME 这里这样写可能不太好
                the_parser_code = compile(p_code, '<string>', 'exec')
                if the_parser_code.co_consts[0] is None:
                    self.log(f'can not find func in parser {p_id} for {file_name}, try the next one')
                    continue
                the_parser = FunctionType(the_parser_code.co_consts[0], globals())
                if self._parser_type == EMailParserType.E_PARSER_NAV:
                    df = the_parser(datas, file_name)
                elif self._parser_type == EMailParserType.E_PARSER_VALUATION:
                    df = the_parser(datas, self._manager_id)
                else:
                    df = None
                self.log(df)
                return df
            except Exception:
                # traceback.print_exc()
                self.log(f'parse {file_name} failed with parser {p_id}, try the next one')
            else:
                self.log(f'done, parse {file_name} succeed, by parser {p_id}')
                break
        else:
            self.log(f'parse {file_name} failed finally')

    def parse_file(self, path, file_name: str) -> Optional[pd.DataFrame]:
        with open(path, 'rb') as datas:
            return self.parse_data(datas, file_name)


class ParserRunnerTest(ParserRunner):

    def __init__(self, manager_id: str, parser_type: EMailParserType, test_case_dir: str):
        super().__init__(manager_id, parser_type)

        self._test_case_dir: str = test_case_dir
        assert os.path.isdir(self._test_case_dir), f'arg test_case_dir should be a directory (now){self._test_case_dir}'

    def run(self):
        with os.scandir(self._test_case_dir) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    self.parse_file(entry.path, entry.name)


if __name__ == '__main__':
    MANAGER_ID = 'DEMO001'

    prt = ParserRunnerTest(MANAGER_ID, EMailParserType.E_PARSER_NAV, './test_parser')
    # prt.run()
