# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2021-01-26 14:51:15
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2021-03-24 22:04:43

import smtplib
import json
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from fixtureMr.base.http_request import HttpRequest
from fixtureMr.base.con_mysql import UseMysql

class SendEmail(object):
	def __init__(self):
		self.smtp = smtplib.SMTP_SSL('smtp.163.com',465)
		self.smtp.set_debuglevel(1)
		self.smtp.ehlo("smtp.163.com")
		self.smtp.login("maoyongfan@163.com","Myf68827106")
		# pass

	def sendRFReport(self):
		job_url = "http://172.17.212.83:8080/job/自动化实验室/api/python?pretty=true"
		headers = {
			"Host":"172.17.212.83:8080",
			"Accept-Encoding": "gzip, deflate",
			"Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
			"Cookie": "jenkins-timestamper-offset=-28800000; screenResolution=1366x768; JSESSIONID.d55f41ca=node01qcdvz8iykrng15i9vkpvkr6uu188.node0; ACEGI_SECURITY_HASHED_REMEMBER_ME_COOKIE=YWRtaW46MTYxNjY3MDU2NzgyNTpmZWRjZWJjNTZiOGQwZTliYmZmMTc0ZjE2YjkyY2ZhMjQ1MGQyYWI2NmVjOWNlNzZkMmQzZmI0NzJlN2RlNDQw"
		}

		toEmailList = []
		ccEmailList = []
		try:
			response = HttpRequest.get(job_url,headers=headers,returnType='text')
			response = response['result']
		
		
			buildnum = eval(response)['lastBuild']['number']

		except:
			buildnum = "x"

		if buildnum != "x":
			try:
				task_url = "http://172.17.212.83:8080/job/自动化实验室/{number}/api/python?pretty=true".format(number=buildnum)
				response = HttpRequest.get(task_url,headers=headers,returnType='text')
				print(response)
				response = response['result']
				failCount = eval(response)["actions"][1]["failCount"]
				skipCount = eval(response)["actions"][1]["skipCount"]
				totalCount = eval(response)["actions"][1]["totalCount"]
				successCount = totalCount - failCount - skipCount
				duration = int(eval(response)["duration"]/1000/60)
			except:
				failCount = "None"
				skipCount = "None"
				totalCount = "None"
				successCount = "None"
				duration = "None"

		else:
			failCount = "None"
			skipCount = "None"
			totalCount = "None"
			successCount = "None"
			duration = "None"

		print(buildnum)

		print(failCount,skipCount,totalCount,duration)

		useMysql = UseMysql()
		toEmailTuple = useMysql.getToEmail()
		ccEmailTuple = useMysql.getCcEmail()
		for loop in toEmailTuple:
			toEmailList.append(loop[0])

		toEmail = ",".join(toEmailList)

		for loop in ccEmailTuple:
			ccEmailList.append(loop[0])

		ccEmail = ",".join(ccEmailList)
		print(toEmail)


		toAdds = toEmailList + ccEmailList + ["shaohui10290@hellobike.com"]

		msg = MIMEMultipart("related")
		msg["Subject"] = "自动化实验室Pre环境 第{number}次构建报告".format(number=buildnum)
		msg["From"] = "maoyongfan@163.com"

		msg["To"] = toEmail

		msg["Cc"] = ccEmail

		msg["Bcc"] = "shaohui10290@hellobike.com"

		html = """
		<html>
		<head></head>
		<style type="text/css">
			.logo {
				float:left;
				height:50px;
				display:block;
				margin: 6px 0 0 0;
				overflow: hidden;
			}
			.p1 {
				float:left;
				height:50px;
				font:40px/44px "微软雅黑";
				color:#666;
				border-left:#f1f1f1 1px solid;
				padding: 0 10px;
				margin:25px 0 0 5px;
			}
		</style>
		<body>
			<p> Hi, all:<br>

				

				<div class="p1" style="text-align:center"> 自动化实验室Pre环境 第""" + """{number}次构建报告 </div><br/><br/><br/><br/>

				<hr/>
				(本邮件是程序自动下发的,请勿回复) <br/><br/>

				项目名称: 自动化实验室 <br/><hr/>

				构建编号: {number} <br/><hr/>

				case总数: {totalCount} <br/><hr/>

				成功总数: <font color="green"> {successCount} </font> <br/><hr/>

				失败总数: <font color="red"> {failCount} </font> <br/><hr/>

				执行时间: {duration} 分钟 <br/><hr/>

				报告地址: <b> <a href="http://172.17.212.83:8080/job/自动化实验室/{number}/robot/report/report.html"> report.html</a></b><br/><hr/>

				任务详细: <b> <a href="http://172.17.212.83:8080/job/自动化实验室/{number}/"> 任务详细 </a></b><br/><hr/>
				
				<br/>

				<p >By 两轮测试 </p><br/>
				<div>
					<h2>
						<a href="https://www.helloglobal.com/">
							<img  style="height:50px" src="https://easybike-www.oss-cn-hangzhou.aliyuncs.com/online-public/header__logo--colored.png" alt="Hellobike" border="0"/>
						</a>


					</h2>

				</div>


			</p>

		</body>
		</html>""".format(number=buildnum,totalCount=totalCount,successCount=successCount,
						failCount=failCount,duration=duration)

		msgAlternative = MIMEMultipart('alternative')
		msg.attach(msgAlternative)

		msgText = MIMEText(html,"html","utf-8")
		msgAlternative.attach(msgText)

		self.smtp.sendmail("maoyongfan@163.com",toAdds,msg.as_string())

		self.smtp.quit()







if __name__ == '__main__':
	s = SendEmail()
	s.sendRFReport()
			