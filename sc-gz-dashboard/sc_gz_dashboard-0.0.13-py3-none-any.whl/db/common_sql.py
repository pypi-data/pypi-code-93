#  The MIT License (MIT)
#
#  Copyright (c) 2021. Scott Lau
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

"""
查询所有指标项目记录数
"""
SELECT_ALL_INDICATOR_ITEM_COUNT = """
select count(*)
from indicator_item ii
where %s
order by ii.id
"""

"""
查询所有指标项目记录
"""
SELECT_ALL_INDICATOR_ITEMS = """
select ii.id,
       ii.indicator_category,
       ii.indicator_type,
       ii.indicator_name,
       ii.indicator_unit,
       ii.indicator_dept
from indicator_item ii
where %s
order by ii.id
%s
"""

"""
查询所有指标项目记录(供过滤选项)
"""
SELECT_ALL_INDICATOR_ITEMS_FOR_FILTER = """
select ii.id,
       ii.indicator_category,
       ii.indicator_type,
       ii.indicator_name,
       ii.indicator_unit,
       ii.indicator_dept
from indicator_item ii
where %s
order by ii.indicator_category, ii.indicator_type, ii.indicator_name
%s
"""

"""
查询所有指标项目历史记录数
"""
SELECT_ALL_INDICATOR_HISTORY_COUNT = """
select count(*)
from indicator_history ih
         left join indicator_item ii
                   on ih.indicator_id = ii.id
where %s
"""

"""
查询所有指标项目历史记录
"""
SELECT_ALL_INDICATOR_HISTORY = """
select ih.id,
       ih.indicator_id,
       ii.indicator_name,
       ii.indicator_category,
       ii.indicator_type,
       ii.indicator_unit,
       ii.indicator_dept,
       ih.indicator_year,
       ih.indicator_month,
       ih.indicator_value,
       ih.report_time
from indicator_history ih
         left join indicator_item ii
                   on ih.indicator_id = ii.id
where %s
order by ih.indicator_id, ih.indicator_year, ih.indicator_month
%s
"""

"""
查询所有指标项目历史记录的最新更新时间和记录数，按年份分组
"""
SELECT_MAX_UPDATE_TIME_INDICATOR_HISTORY = """
select ih.indicator_year, max(update_time), max(report_time), count(*)
from indicator_history ih
group by ih.indicator_year
order by ih.indicator_year
"""

"""
查询指标历史数据，按ID分组
"""
SELECT_INDICATOR_HISTORY_GROUP_BY_ID = """
select ih.indicator_id,
       ii.indicator_category,
       GROUP_CONCAT(ih.indicator_month order by ih.indicator_month) as month_list,
       SUBSTRING_INDEX(GROUP_CONCAT(ih.indicator_month order by ih.indicator_month),',', -1) as last_month,
       GROUP_CONCAT(ih.indicator_value order by ih.indicator_month) as value_list,
       SUBSTRING_INDEX(GROUP_CONCAT(ih.indicator_value order by ih.indicator_month),',', -1) as last_indicator_value
from indicator_history ih
         left join indicator_item ii
                   on ih.indicator_id = ii.id
where %s
group by ih.indicator_id
order by ih.indicator_id
%s
"""

"""
检查指标历史记录是否存在
"""
CHECK_INDICATOR_HISTORY_EXISTENCE = """
select ih.id
from indicator_history ih
where ih.indicator_id = %s and ih.indicator_year = %s and ih.indicator_month = %s;
"""

"""
插入指标历史记录
"""
INSERT_INDICATOR_HISTORY_RECORD = """
insert into indicator_history(indicator_id, indicator_year, indicator_month, indicator_value, report_time)
values (%s, %s, %s, %s, %s);
"""

"""
更新指标历史记录
"""
UPDATE_INDICATOR_HISTORY_RECORD = """
update indicator_history
set indicator_value = %s,
    report_time = %s,
    update_time = now()
where indicator_id = %s and indicator_year = %s and indicator_month = %s;
"""

"""
删除指标历史记录
"""
DELETE_INDICATOR_HISTORY_RECORD = """
delete from indicator_history where id = %s;
"""

