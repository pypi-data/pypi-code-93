# url path 统一管理 花括号中变量代表待替换值

from adapay_core import ApiRequest
import adapay
pay_message_token = '/v1/token/apply'

# ----------payment 对象----------
payment_create = '/v1/payments'
payment_query = '/v1/payments/{payment_id}'
payment_close = '/v1/payments/{payment_id}/close'
payment_list = '/v1/payments/list'

# ----------confirm 对象----------
confirm_create = '/v1/payments/confirm'
confirm_query = '/v1/payments/confirm/{payment_confirm_id}'
confirm_query_list = '/v1/payments/confirm/list'

# ----------reverse 对象----------
reverse_create = '/v1/payments/reverse'
reverse_query = '/v1/payments/reverse/{reverse_id}'
reverse_query_list = '/v1/payments/reverse/list'

# ----------refund 对象----------
refund_create = '/v1/payments/{id}/refunds'
refund_query = '/v1/payments/refunds'

# ----------member 对象 ----------
member_create = '/v1/members'
member_query = '/v1/members/{member_id}'
member_query_list = '/v1/members/list'
member_update = '/v1/members/update'

# ----------corp_member 对象----------
corp_member_create = '/v1/corp_members'
corp_member_query = '/v1/corp_members/{member_id}'

# ----------settle_account 对象 ----------
settle_account_create = '/v1/settle_accounts'
settle_account_modify = '/v1/settle_accounts/modify'
settle_account_query = '/v1/settle_accounts/{settle_account_id}'
settle_account_delete = '/v1/settle_accounts/delete'
settle_account_detail_query = '/v1/settle_accounts/settle_details'
settle_account_balance_query = '/v1/settle_accounts/balance'

# 查询服务商分账对象列表
settle_account_commissions_list = '/v1/settle_accounts/commissions/list'

# 创建服务商分账对象
settle_account_commissions_create = '/v1/settle_accounts/commissions'

transfer_create = '/v1/settle_accounts/transfer'
list_transfer = '/v1/settle_accounts/transfer/list'

# ----------Drawcash 对象 ----------
cash_draw_create = '/v1/cashs'
cash_draw_status = '/v1/cashs/stat'

# ----------云闪付用户id ----------
query_identity = '/v1/union/user_identity'

# ----------bill 账单----------
bill_download = '/v1/bill/download'

# ----------wallet 对象 ----------
wallet_login = '/v1/walletLogin'

# ----------Account 对象 ----------
account_pay = '/v1/account/payment'

# ----------checkout 对象 ----------
checkout_create = '/v1/checkout'
checkout_list = '/v1/checkout/list'

freeze_account_create = '/v1/settle_accounts/freeze'
freeze_account_query_list = '/v1/settle_accounts/freeze/list'

un_freeze_account_create = '/v1/settle_accounts/unfreeze'
un_freeze_account_query_list = '/v1/settle_accounts/unfreeze/list'

# ----------快捷绑卡 对象 ----------
fast_pay_card_bind = '/v1/fast_card/apply'
fast_pay_card_bind_confirm = '/v1/fast_card/confirm'
fast_pay_card_bind_list = '/v1/fast_card/list'

# ----------快捷支付确认 ----------
fast_pay_confirm = '/v1/fast_pay/confirm'
fast_pay_sms_code = '/v1/fast_pay/sms_code'


# ----------支付系统 ----------
pay_base_url = 'https://api.adapay.tech'

# ----------钱包系统 ----------
page_base_url = 'https://page.adapay.tech'

# ----------Adapay 公钥 ----------
public_key = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCwN6xgd6Ad8v2hIIsQVnbt8a3JituR8o4Tc3B5WlcFR55bz4OMqrG/356Ur3cPb' \
             'c2Fe8ArNd/0gZbC9q56Eb16JTkVNA/fye4SXznWxdyBPR7+guuJZHc/VW2fKH2lfZ2P3Tt0QkKZZoawYOGSMdIvO+WqK44updya' \
             'x0ikK6JlNQIDAQAB'


# 这里外部传入url，目前存在多个base_url
def __request_init(url, request_params, base_url):
    mer_key = request_params.pop('mer_key', None)
    config_info = adapay.mer_config[mer_key]
    ApiRequest.base_url = base_url if base_url else pay_base_url
    ApiRequest.build(config_info["api_key"], config_info['private_key'], public_key, url,
                     request_params, adapay.__version__, adapay.connect_timeout)


def request_post(url, request_params, files=None, base_url=''):
    __request_init(url, request_params, base_url)
    return ApiRequest.post(files)


def request_get(url, request_params, base_url=''):
    __request_init(url, request_params, base_url)
    return ApiRequest.get()
