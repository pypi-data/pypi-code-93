import os
import smtplib
from email.message import EmailMessage as em



def success_mail(to_mail,info,from_mail=os.environ.get('python_sender'),from_pass=os.environ.get('python_sender_pass')):
	
	msg = em()

	msg['From'] = from_mail
	msg['To'] = to_mail
	msg['Subject'] = 'Python automatic script notification: Success!'
	msg.set_content(f'The script finished succesfully, here are some informations:\n\n + Script name: {os.path.basename(__file__)}\n + {info}')
	
	with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
		smtp.login(from_mail, from_pass)
		smtp.send_message(msg)
	print('Notification mail send')

def error_mail(to_mail,info,from_mail=os.environ.get('python_sender'),from_pass=os.environ.get('python_sender_pass'))):
	
	msg = em()

	msg['From'] = from_mail
	msg['To'] = to_mail
	msg['Subject'] = 'Python automatics script notification: Error!'
	msg.set_content(f'An error occured, here are some informations:\n\n + Script name: {os.path.basename(__file__)}\n + {info}')
	
	with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
		smtp.login(from_mail, from_pass)
		smtp.send_message(msg)


def half_way(to_mail,text,from_mail=os.environ.get('python_sender'),from_pass=os.environ.get('python_sender_pass')):
	msg = em()

	msg['From'] = from_mail
	msg['To'] = to_mail
	msg['Subject'] = 'Python automatic script notification: In progress'
	msg.set_content(f'The script {os.path.basename(__file__)} is still running.')
	
	with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
		smtp.login(from_mail, from_pass)
		smtp.send_message(msg)

