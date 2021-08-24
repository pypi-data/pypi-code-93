# -*- coding: utf-8 -*-

"""
Funções para auxiliarem no desenvolvimento
"""

import os
import time
import re
import json
import md5
import datetime
from dateutil.relativedelta import relativedelta
from unicodedata import normalize
from functools import wraps

import logging
LOGGER = logging.getLogger()


def tente_outra_vez(excecoes, tentativas=4, tempo_espera=3, multiplicador_espera=1):
    """
    Escuta pelas exceções especificadas e refaz a chamada para o método.
    :param excecoes: As exceções que devem ser escutadas
    :type excecoes: Exception or tuple
    :param tentativas: Número de vezes que deve ser chamado o método
    :type tentativas: int
    :param tempo_espera: Tempo inicial de espera em segundos entre as tentativas
    :type tempo_espera: int
    :param multiplicador_espera: Multiplicador para o tempo de espera nas chamadas subsequentes.
    :type multiplicador_espera: int
    """
    def deco_tente_outra_vez(funcao):
        """
        Decorator para tente_outra_vez
        """
        @wraps(funcao)
        def funcao_tente_outra_vez(*args, **kwargs):
            """
            Tratamento de decorator para tente_outra_vez
            """
            _tentativas, _tempo_espera = tentativas, tempo_espera
            while _tentativas > 1:
                try:
                    return funcao(*args, **kwargs)
                except excecoes, exc:
                    msg = "{}, Reconectando in {} segundos...".format(str(exc), _tempo_espera)
                    if LOGGER:
                        LOGGER.warning(msg)
                    time.sleep(_tempo_espera)
                    _tentativas -= 1
                    _tempo_espera *= multiplicador_espera
            return funcao(*args, **kwargs)
        return funcao_tente_outra_vez
    return deco_tente_outra_vez


def remover_acentos(value):
    """Normalize the values."""
    try:
        return normalize('NFKD', value.decode('utf-8')).encode('ASCII', 'ignore')
    except UnicodeEncodeError:
        return normalize('NFKD', value).encode('ASCII', 'ignore')


def pegar_versao_git():
    """
    pegar_versao_git
    :return: git version
    """
    import subprocess

    version = None

    # 1. Tenta buscar a versao do GIT
    try:
        version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
        version = version.replace("\n","")
    except subprocess.CalledProcessError:
        if os.path.isfile('VERSION') is True:
            with open('VERSION','r') as f:
                version = f.read()
            version = version.replace("\n","")

    # 2. Busca o nome da Aplicacao ou o Deploy ID no Beanstalk
    if not version:
        try:
            file = open('/opt/elasticbeanstalk/deploy/manifest','r')
            json_dict = json.loads(file)
            version = json_dict.get('VersionLabel', None)

            if not version:
                version = json_dict.get('DeploymentId')
        except:
            pass

    # 3. Usa a variável de ambiente
    if not version:
        version = os.environ.get('HOSTNAME')

    # Retorna o hash
    if version:
        try:
            version = md5.new(str(version)).hexdigest()[:7]
        except:
            pass

    return version or '0'


def send_email(template_file=None, context=None,
               contrato_id=None, conta_id=None, usuario_id=None, cliente_id=None, pedido_venda_id=None,
               salva_evidencia=True, to_email=None, reply_to=None, countdown=0):
    """
    send_email
    :param template_file: template_file
    :param context: context
    :param contrato_id: contrato_id
    :param conta_id: conta_id
    :param usuario_id: usuario_id
    :param cliente_id: cliente_id
    :param pedido_venda_id: pedido_venda_id
    :param salva_evidencia: salva_evidencia
    :param to_email: to_email
    :return: None
    """
    from li_common.conexoes.worker import WorkerConnect

    args = {
        "template_file": template_file,
        "context": context,
        "contrato_id": contrato_id,
        "conta_id": conta_id,
        "usuario_id": usuario_id,
        "cliente_id": cliente_id,
        "pedido_venda_id": pedido_venda_id,
        "salva_evidencia": salva_evidencia,
        "to_email": to_email,
        "reply_to": reply_to
    }

    WorkerConnect().execute('async.utils.send_email_template', args=args, countdown=countdown)


def send_email_sem_template(from_email=None, to_email=None, reply_to=None, subject=None,
            html_message=None, text_message=None, countdown=0, salva_evidencia=True
):
    """
    send_email_sem_template
    :param from_email: from_email
    :param to_email: to_email
    :param reply_to: reply_to
    :param subject: subject
    :param content: content
    :param countdown: countdown
    :return: None
    """
    from li_common.conexoes.worker import WorkerConnect

    args = {
        "from_email": from_email,
        "to_email": to_email,
        "reply_to": reply_to,
        "subject": subject,
        "html_message": html_message,
        "text_message": text_message,
        "salva_evidencia": salva_evidencia
    }

    WorkerConnect().execute('async.utils.send_email', args=args, countdown=countdown)


def carregar_env(caminho_arquivo=None):
    if not caminho_arquivo:
        caminho_arquivo = '/etc/profile.d/env.sh'
    if not os.path.exists(caminho_arquivo):
        return 'ARQUIVO NAO EXISTE'
    try:
        arquivo = open(caminho_arquivo)
        for linha in arquivo:
            linha = linha.replace('\n', '').replace('export ', '')
            if not linha or '=' not in linha:
                continue
            chave, valor = linha.split('=')
            try:
                os.environ[chave.strip()] = valor.strip().strip('"').strip("'")
            except Exception, e:
                print '{} - ERRO: {}'.format(linha, str(e))
        arquivo.close()
    except Exception, e:
        print str(e)


def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + "".join(x.title() for x in components[1:])


def to_underscore_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_current_month_cycle(initial_date, final_date):
    """
    Descobre e retorna o ciclo mensal atual para assinaturas com período maior que 1 mes
    :param initial_date: date
    :param final_date: date
    :return: dict
    """
    today = datetime.date.today()
    total_months = (final_date.year - initial_date.year) * 12 + (final_date.month - initial_date.month)
    # Se o ciclo tiver apenas 1 mes nao precisa calcular nada
    if total_months in {0,1}:
        return { "initial": initial_date, "final": final_date }

    cycle = { "initial": None, "final": None }
    for month in range(total_months):
        cycle['initial'] = cycle['final'] + relativedelta(days=1) if cycle['initial'] is not None else initial_date
        # Ultimo mes deve acabar no final do ciclo assinado
        if month < 11:
            cycle['final'] = cycle['initial'] + relativedelta(months=1)
            if cycle['initial'].day == cycle['final'].day:
                cycle['final'] = cycle['final'] - relativedelta(days=1)
        else:
            cycle['final'] = final_date
        # Chegamos ao ciclo que corresponde ao atual
        if today >= cycle['initial'] and today <= cycle['final']:
            break

    return cycle
