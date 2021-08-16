#  Copyright (c) 2020. Cortex Intelligence.
#  Developed by Enderson Menezes

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pycortexintelligence.core import messages


def send_email_function(server, port, user_from, password, message_text, subject, user_to):
    """
    :param server: Servidor SMTP para Envio de E-mails
    :param port: Porta de Conexão SMTP
    :param user_from: Login/Usuário Remetente
    :param password: Senha de acesso do SMTP
    :param message_text: Mensagem a ser enviada
    :param subject: Assunto
    :param user_to: Destinatário
    :return: Não retorna nada, é um procedimento.
    """
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = user_from
    message["To"] = user_to
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(message_text, "plain"))

    # Message to Text
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(server, port, context=context) as server:
        server.login(user_from, password)
        server.sendmail(user_from, user_to, text)


def error_message(message_text, os_params):
    """
    Utilize o seguinte exemplo para enviar uma mensagem de erro:
    error_message('Tivemos problema ao enviar e-mail', OS_PARAMS)
    """
    send_email_function(
        server=os_params['email_smtp'],
        port=os_params['email_port'],
        user_from=os_params['email_user'],
        user_to=os_params['email_to_error'],
        password=os_params['email_password'],
        subject=messages.EMAIL_PROJECT_ERROR_SUBJECT.format(os_params['project_name']),
        message_text=message_text,
    )