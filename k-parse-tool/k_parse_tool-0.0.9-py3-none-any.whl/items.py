# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WebincrementcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    navig_url = scrapy.Field()  # 导航页url
    navig_title = scrapy.Field()  # 列表页标题
    navig_date = scrapy.Field()  # 列表页时间
    navig_dept = scrapy.Field()  # 列表页部门
    navig_text_number = scrapy.Field()  # 列表页发文字号
    navig_punished_parties = scrapy.Field()  # 列表页处罚对象
    navig_punished_people = scrapy.Field()  # 列表页处罚对象(负责人)
    navig_lawAccording = scrapy.Field()  # 列表页法律依据
    navig_penaltyAccording = scrapy.Field()  # 列表页处罚依据
    navig_punishment_measures = scrapy.Field()  # 列表页处罚结果

    detail_page_url = scrapy.Field()  # 详情页url
    detail_page_title = scrapy.Field()  # 详情页标题
    detail_page_dept = scrapy.Field()  # 详情页发文部门
    detail_page_date = scrapy.Field()  # 详情页发文时间
    detail_page_text_number = scrapy.Field()  # 详情页发文字号
    detail_page_punished_parties = scrapy.Field()  # 详情页处罚对象
    detail_page_punished_people = scrapy.Field()  # 详情页处罚对象(负责人)
    detail_page_lawAccording = scrapy.Field()  # 详情页法律依据
    detail_page_penaltyAccording = scrapy.Field()  # 详情页处罚依据
    detail_page_punishment_measures = scrapy.Field()  # 详情页处罚结果
    detail_page_body_code = scrapy.Field()  # 详情页正文
    detail_page_body_is_table = scrapy.Field()  # 详情页正文是否是表格,1、True是表格,2、False是文本
    detail_page_source_code = scrapy.Field()  # 详情页源码

    file_urls = scrapy.Field()  # 附件url列表
    file_names = scrapy.Field()  # 附件展示名称
    files = scrapy.Field()  # 附件下载路径、下载的url和文件的校验码
    files_body_is_down = scrapy.Field()  # 附件处理方式,1、下载,2、解析内容,3、解析内容并提供下载
    files_body_is_table = scrapy.Field()  # 附件是否是表格

    files_title = scrapy.Field()
    files_date = scrapy.Field()
    files_dept = scrapy.Field()
    files_text_number = scrapy.Field()
    files_punished_parties = scrapy.Field()
    files_punished_people = scrapy.Field()
    files_lawAccording = scrapy.Field()
    files_penaltyAccording = scrapy.Field()
    files_punishment_measures = scrapy.Field()
    files_body_code = scrapy.Field()

    task_code = scrapy.Field()  # 任务码
    collection_date = scrapy.Field()  # 采集时间
    admin_penalty_case_ID = scrapy.Field  # 行政处罚id
    is_allow_issued = scrapy.Field  # 是否允许发布
