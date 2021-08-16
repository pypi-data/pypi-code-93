#  Copyright (c) 2020. Cortex Intelligence.
#  Developed by Enderson Menezes

import os
import shutil
from pycortexintelligence.core.messages import *
from pycortexintelligence.core.funcs_mail import error_message
from pycortexintelligence.core.config import OUTPUT_FOLDER, DOWNLOADED_FOLDER, PARAMS_TO_CHECK, LOG_FILE

FOLDERS = [OUTPUT_FOLDER, DOWNLOADED_FOLDER]

FILES = [LOG_FILE]


def __delete_file(file_path, os_params):
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        except_text = 'Failed to delete %s. Reason: %s' % (file_path, e)
        error_message(except_text, os_params)
        raise 'Failed to delete %s. Reason: %s' % (file_path, e)


def load_env_to_dict(new_params_to_check: list):
    """
    Verifica as variavéis que foram colocadas como obrigatórias e cria um OS_PARAMS.
    :return: os_params um dict com variaveis de ambiente configuradas no .env
    """
    os_params = dict()
    final_check = new_params_to_check + PARAMS_TO_CHECK
    for param in final_check:
        os_params[param] = os.getenv(param)
    return os_params


def verify_env(os_params: dict, new_params_to_check: list):
    """
    :param new_params_to_check:
    :param os_params:
    :return: Sem retorno, procedimento verifica se os valores do os_params bate com o que foi desenhado.
    """
    # Argumentos Necessários
    final_check = new_params_to_check + PARAMS_TO_CHECK
    for key in final_check:
        if os_params[key] is None:
            message_text = mail_variable_error(key)
            error_message(message_text=message_text, os_params=os_params)
            raise ValueError('Não conseguimos validar a chave: {}, nas variaveis de ambiente'.format(key))


def check_dirs():
    for folder in FOLDERS:
        try:
            os.stat(folder)
        except FileNotFoundError:
            os.mkdir(folder)


def delete_temp_files(os_params):
    for folder in FOLDERS:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            __delete_file(file_path, os_params)
