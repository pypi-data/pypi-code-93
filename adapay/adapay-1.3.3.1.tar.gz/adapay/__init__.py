from adapay_core import log_util

from adapay.payment import *
from adapay.payment_reverse import *
from adapay.payment_confrim import *

from adapay.refund import *

from adapay.member import *
from adapay.corp_member import *

from adapay.settle_account import *

from fishbase.fish_logger import set_log_file, set_log_stdout
from adapay.checkout import *
from adapay.account import *
from adapay.drawcash import *
from adapay.wallet import *
from adapay.transfer import *
from adapay.fast_pay import *
from adapay.un_freeze_account import *
from adapay.freeze_account import *

from adapay.adapay_tools import *

mer_config = {}

"""
全局的配置字典
{"member_id1":{},
 "member_id2":{},
 "member_id3":{},
   ···
}
"""


connect_timeout = 30


def init_log(console_enable=False, log_level='', log_tag='{adapay}', log_file_path=''):
    """
    :param log_tag:
    :param log_level:
    :param console_enable: 是否在控台输出日志
    :param log_file_path:
    :return:
    """
    if console_enable:
        set_log_stdout()
    if log_file_path:
        set_log_file(log_file_path)
    if log_level:
        log_util.log_level = log_level
        if log_tag:
            log_util.log_tag = log_tag


# sdk 版本
__version__ = '1.3.3.1'
