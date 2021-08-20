'''
example
{'spreadsheetId': '1Awgq6-tal1Nn6EazoSe3392HrNRUryyHlwLtsSwu_jY',
 'valueRanges': [{'majorDimension': 'ROWS',
                  'range': 'bizA!A1:Z999',
                  'values': [['key', 'zh-Hans', 'zh-Hant', 'en', 'ja'],
                             ['Download', '下载', '下載', 'Download', 'ダウンロード'],
                             ['Comment', '评论', '留言', 'Comment', 'コメント']]},
                 {'majorDimension': 'ROWS',
                  'range': 'main!A1:Z999',
                  'values': [['key', 'zh-Hans', 'zh-Hant', 'en', 'ja'],
                             ['Copy', '复制', '複製', 'Copy', 'コピー'],
                             ['Delete', '删除', '刪除', 'Delete', '削除']]}]}

'''

from gslocalizator.sheet_tran_task import _SheetTranTask
from typing import Dict, List


class WordsParser:
    def __init__(self, data_dict: Dict, tasks: _SheetTranTask):

        self.tasks = tasks

        value_ranges = data_dict['valueRanges']
        for value_range in value_ranges:
            sheetRange = value_range['range']
            current_tran_task = self._get_tran_task_by_range(sheetRange)
            if current_tran_task == None:
                continue

            current_tran_task.update_rows(value_range['values'])

    def _get_tran_task_by_range(self, valueRange: str) -> _SheetTranTask:

        for task in self.tasks:
            if task.is_my_sheet_range(valueRange):
                return task

        return None

    def save(self, format: str):
        print(f'saving:{format}')
        for task in self.tasks:
            task.save(format)
        print(f'saved:{format}')
