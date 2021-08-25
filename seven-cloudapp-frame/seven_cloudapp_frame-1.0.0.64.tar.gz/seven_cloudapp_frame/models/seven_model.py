# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-02 15:17:41
@LastEditTime: 2021-07-26 16:31:17
@LastEditors: HuangJianYi
:description: 自定义实体
"""

class InvokeResult():
    """
    :description: 接口返回实体
    :param {type} 
    :return: InvokeResult
    :last_editors: HuangJingCan
    """
    def __init__(self):
        self.success = True
        self.data = InvokeResultData().__dict__


class InvokeResultData():
    """
    :description: 接口返回实体
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    def __init__(self):
        self.success = True
        self.data = None
        self.error_code = ""
        self.error_message = ""


class FileUploadInfo():
    """
    :description: 文件上传信息实体
    :param {type} 
    :return: FileUploadInfo
    :last_editors: HuangJingCan
    """
    def __init__(self):
        # 检查值
        self.md5_value = ""
        # 上传路经
        self.resource_path = ""
        # 原文件名
        self.original_name = ""
        # 文件路经
        self.file_path = ""
        # 图片宽度
        self.image_width = 0
        # 图片高度
        self.image_height = 0


class PageInfo():
    """
    :description: 分页列表实体
    :param page_index：当前索引号
    :param page_size：页大小
    :param record_count：总记录数
    :param data：数据
    :return: PageInfo
    :last_editors: HuangJingCan
    """
    def __init__(self, page_index=0, page_size=10, record_count=0, data=None):
        """
        :description: 分页列表实体
        :param page_index：当前索引号
        :param page_size：页大小
        :param record_count：总记录数
        :param data：数据
        :return: PageInfo
        :last_editors: HuangJingCan
        """
        # 数据
        self.data = data
        # 当前索引号
        self.page_index = page_index
        # 页大小
        self.page_size = page_size
        # 总记录数
        self.record_count = record_count

        # 页数
        self.page_count = record_count / page_size + 1
        if page_size == 0:
            self.page_count = 0
        if record_count % page_size == 0:
            self.page_count = record_count / page_size
        self.page_count = int(self.page_count)

        # 当前页号
        self.page_no = page_index + 1

        # 上一页索引
        self.previous_index = page_index - 1 if page_index > 0 else 0

        # 下一页索引
        self.next_index = page_index + 1
        if self.page_count == 0:
            self.next_index = 0
        if self.page_no >= self.page_count:
            self.next_index = self.page_index

        # 是否下一页
        self.is_next = True
        if self.page_count == 0:
            self.is_next = False
        if self.page_no >= self.page_count:
            self.is_next = False

        # 是否上一页
        self.is_previous = True
        if page_index == 0:
            self.is_previous = False


class TaoBaoParam():
    """
    :description: 淘宝参数实体
    :last_editors: HuangJingCan
    """
    def __init__(self):
        # 商家应用的appKey
        self.app_key = ""
        # 当前登录用户的昵称(需要用户授权)
        self.user_nick = ""
        # 当前登录用户的openId
        self.open_id = ""
        # 当前云应用调用环境，入参为：test或者online，对应在云开发中绑定的云容器的测试环境和正式环境。在发布上线的前注意调整env为online，调用正式环境。
        self.env = ""
        # 运行时使用的小程序ID，
        # 1,如果是BC模式，那么这里是B端小程序ID;
        # 2,如果是模板开发模式，这里是模板小程序ID;
        # 3,如果是插件开发模式，这里是宿主小程序的小程序ID;
        self.mini_app_id = ""
        # 当前登录用户的授权token，也是sessionkey（需要用户授权）
        self.access_token = ""
        # 使用当前小程序appkey和secret进行对参数进行加签后的签名
        self.sign = ""
        # 当前登录用户的混淆nick
        self.mix_nick = ""
        # 当前登录用户的userId，仅对老应用迁移生效
        self.user_id = ""
        # 主账号userId，千牛子账号登录授权后可与获取，仅对老应用迁移生效
        self.main_user_id = ""
        # 当前调用小程序的小程序ID
        # 1,如果是BC模式，那么这里是C端小程序ID;
        # 2,如果是模板开发模式，这里是实例化小程序ID;
        # 3,如果是插件开发模式，这里是插件的小程序ID;
        self.source_app_id = ""
        # request_id
        self.request_id = ""