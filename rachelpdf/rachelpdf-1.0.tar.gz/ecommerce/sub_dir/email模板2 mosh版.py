from email.mime.multipart import MIMEMultipart
#从email包中（子文件夹）的mine包（Multi-purpose Internet Mail Extensions 是一个定义邮件信息的格式标准）的multipart多方模块，引入MIMEMultipart 类 用这个类可以 发送HTML和TEXT的电子邮件信息

message=MIMEMultipart()  #调用这个类
message["from"]="rachelhanlj@outlook.com"
message["to"]="rachelhanlj@163.com"
message["subject"]="This is a good test"


from pathlib import Path
from email.mime.image import MIMEImage    #如果想发送图片
message.attach(MIMEImage(Path("IMG_0576.JPG").read_bytes()))

from email.mime.text import MIMEText   #如果想发送文字信息
message.attach(MIMEText("Body,Hello World"))

from string import Template  #如果想发送模板   注意：如果同时有多行message.attach(MIMEText()会变成附件，不要这样(最好都写在模板里)
template=Template(Path("template.html").read_text())
message.attach(MIMEText(template.substitute({"name":"Rachel","times":2,}),"html")) 
#这个HTML不写，信息就会变成和模板编辑器里一样的东西，要写上才会变成正常文字格式


import smtplib
with smtplib.SMTP('smtp.office365.com',587) as smtp:
    smtp.ehlo()     #和服务器打招呼
    smtp.starttls()   #把smtp放在tls模式下 transport layer security。和服务器打完招呼后发送安全协议  因为这个括号debug了一整天

    smtp.login("rachelhanlj@outlook.com","Anhan12!")
    smtp.send_message(message)
    print("sent")      #为了确认是否发送（程序运转是否正常）可以不写

