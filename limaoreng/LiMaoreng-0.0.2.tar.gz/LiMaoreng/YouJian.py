

"""默认使用网易邮箱发送邮件，默认了发件人和收件人"""


import smtplib
from email.mime.text import MIMEText  # 负责构造文本。
from email.mime.image import MIMEImage  # 负责构造图片。
from email.mime.multipart import MIMEMultipart  # 负责将多个对象集合起来。
from email.header import Header
from email.utils import parseaddr, formataddr  # 美化收发件人格式，使之可以显示收发件人昵称。


def format_addr(name_email):  # 将带昵称的邮件地址设置成符合邮件发送的格式
    name, addr = parseaddr(name_email)  # name昵称，addr是纯Email地址。
    e = formataddr((Header(name, 'utf-8').encode(), addr))  # formataddr函数将name和addr转换成标准Email地址格式
    return e


"""由于收件人默认为一个，‘处理多个收件人’功能暂时取消"""
# def receiver_names(mail_receivers):  # 处理多个收件人
#     txt=''
#     for i in range(0, len(mail_receivers)):
#         txt+="receiver_" + str(i+1) + "_name<" + mail_receivers[i] + '>,'
#     return txt[:-1]


def xie_you_jian(subject_content="在下肝阴阳师遇阻，速来相助！！！",  # 邮件主题
                 body_content='我反正处理不了了，你自己看着办吧~',  # 邮件正文内容
                 tu_pian='',
                 from_='肝帝李茂仍',
                 mail_sender="13736200754@163.com",
                 to_='摸鱼李茂仍',
                 mail_receivers="2324412934@qq.com"):
    # 默认了发件人和收件人
    message = MIMEMultipart("related")
    # 构造一个MIMEMultipart对象代表邮件本身。related 表示使用内嵌资源的形式将邮件发送给对方
    ''''''
    message["From"] = format_addr(from_ +"<"+ mail_sender + ">")  # 设置发送者，注意严格遵守格式
    message["To"] = format_addr(to_ +"<" + mail_receivers + ">")  # 多个收件人功能暂时取消receiver_names(mail_receivers)
    message["Subject"] = Header(subject_content, 'utf-8')  # 设置邮件主题
    ''''''
    message_text = MIMEText(body_content, "plain", "utf-8")  # 构造文本,参数1：正文内容，参数2：文本格式，参数3：编码方式
    message.attach(message_text)  # 向MIMEMultipart对象中添加文本对象
    ''''''
    if tu_pian !='':
        image_data = open(tu_pian, 'rb')  # 二进制读取图片
        message_image = MIMEImage(image_data.read())  # 设置读取获取的二进制数据
        message_image['Content-Disposition']='attachment; filename="'+tu_pian+'"'
        image_data.close()  # 关闭刚才打开的文件
        message.attach(message_image)  # 添加图片文件到邮件信息中去
    ''''''
    return message


def fa_song_you_jian(message, mail_license,
                     mail_host="smtp.163.com",
                     mail_sender="13736200754@163.com",
                     mail_receivers="2324412934@qq.com"):  # 收件人不能设定为列表，列表可变，容易出错。
    # 除了邮件、邮箱授权码是输入，其余都是默认值。
    try:
        stp = smtplib.SMTP()  # 创建SMTP对象
        stp.connect(mail_host, 25)  # 设置发件人邮箱的域名和端口，端口地址为25
        # stp.set_debuglevel(1)  # set_debuglevel(1)可以打印出和SMTP服务器交互的所有信息
        stp.login(mail_sender, mail_license)  # 登录邮箱。参数1：邮箱地址，参数2：邮箱授权码
        stp.sendmail(mail_sender, mail_receivers, message.as_string())
        # 发送邮件。参数1：发件人邮箱地址，参数2：收件人邮箱地址，参数3：把邮件内容格式改为str
        print("邮件发送成功~")
        stp.quit()  # 关闭SMTP对象
    except Exception as e:
        """被Pycharm提示的原因是没有指定错误，except的范围太广了。"""
        print('邮件发送失败！------'+str(e))
