"""
doc.py MySQL数据库文档生成
By IT小强xqitw.cn <mail@xqitw.cn>
At 2/4/21 3:42 PM
"""

from ..base import doc


class Doc(doc.Doc):
    """
    MySQL数据库文档生成
    """

    COLUMNS_SQL = 'SHOW FULL COLUMNS FROM `{table_name}`'

    def get_db_fields_info(self, table_name, cur_fields):
        """
        获取数据库中的字段信息
        :param table_name:
        :param cur_fields:
        :return:
        """

        sql = self.COLUMNS_SQL.format(table_name=table_name)
        self.cursor.execute(sql)
        for filed_info in self.cursor.fetchall():
            filed_name = filed_info[0]
            # db_default_value = filed_info[5]
            # default_value = cur_fields[filed_name]['default']
            # comment = cur_fields[filed_name]['comment']

            cur_filed_info = {
                'field': filed_name,
                'type': filed_info[1],
                'collation': filed_info[2],
                'null': filed_info[3],
                'key': filed_info[4],
                # 'default': db_default_value if db_default_value else default_value,
                'extra': filed_info[6],
                'privileges': filed_info[7],
                # 'comment': comment if comment else filed_info[8]
            }
            cur_fields[filed_name].update(cur_filed_info)
        return cur_fields
