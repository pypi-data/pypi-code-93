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
from gslocalizator.string_file import SaveFormat
from typing import Dict


class WordsParser:
    def __init__(self, data_dict: Dict, tasks: _SheetTranTask):

        self.tasks = tasks

        value_ranges = data_dict['valueRanges']
        for value_range in value_ranges:
            sheetRange = value_range['range']
            current_tran_task = self._get_tran_task_by_range(sheetRange)
            if current_tran_task == None:
                continue

            rows = value_range['values']
            current_tran_task.update_rows(rows)

    def _get_tran_task_by_range(self, valueRange: str) -> _SheetTranTask:

        for task in self.tasks:
            if task.is_my_sheet_range(valueRange):
                return task

        return None

    def save(self, format: SaveFormat):
        for task in self.tasks:
            task.save(format)
