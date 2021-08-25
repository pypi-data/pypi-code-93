# from feapder.utils import tools
# #
# EMAIL_SENDER = "feapder@163.com"  # 发件人
# EMAIL_PASSWORD = "YPVZHXFVVDPCJGTH"  # 授权码
# EMAIL_RECEIVER = "564773807@qq.com"  # 收件人 支持列表，可指定多个
# # 时间间隔
# WARNING_INTERVAL = 3600  # 相同报警的报警时间间隔，防止刷屏
# WARNING_LEVEL = "DEBUG"  # 报警级别， DEBUG / ERROR
# EMAIL_SMTPSERVER="smtp.163.com"
#
#
# tools.email_warning(
#     message="test3",
#     title="feapder:test",
#     message_prefix=None,
#     email_sender=EMAIL_SENDER,
#     email_password=EMAIL_PASSWORD,
#     email_receiver=EMAIL_RECEIVER,
#     rate_limit=WARNING_INTERVAL,
#     email_smtpserver=EMAIL_SMTPSERVER
# )
#
# # from feapder.utils.tools import make_update_sql, make_insert_sql
# #
# #
# # if __name__ == "__main__":
# #     data = {
# #         "name": '''do"nt't''',
# #         "name2": "呵呵哒"
# #     }
# #     sql = make_insert_sql("test1", data)
# #     print(sql)
# #
# #     sql = make_update_sql("test1", data, condition="id=''1'")
# #     print(sql)

from feapder.utils.tools import reach_freq_limit
import time

print(reach_freq_limit(3, "a"))
print(reach_freq_limit(3, "a"))
time.sleep(3)
print(reach_freq_limit(3, "a"))
print(reach_freq_limit(3, "a"))