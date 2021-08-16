#!/usr/bin/env python3
"""
Пример плагина для Astresay. Первым аргументом для него должен выступать
путь к временному JSON-файлу с данными, полученными в процессе работы
диалога.
Плагины необходимы для переопределения или создания новых переменных, а также
для обращения к другим, например, сетевым ресурсам.
"""
import json
import sys

# Считываем файл с данными для плагина.
filename = sys.argv[1]
with open(filename) as f:
    plugin_data = json.load(f)

#######################
# Начало вашего кода. #
#######################

# Словарь plugin_data содержит:
# 'agi_params' - все переменные переданные в EAGI,
# 'work_dir' - путь к рабочему каталогу,
# 'speech' - распознанная речь текущего блок-скрипта,
# 'result': результат работы текущего блок-скрипта,
# 'variables' - словарь всех переменных определённых ранее,
# 'chain': список движения блок-скриптов с их результатами и речью,
# 'text_buffers': перечень текстовых буферов определённых ранее,

print('Получены данные для плагина.')
print('agi_params:', plugin_data['agi_params'])
print('work_dir:', plugin_data['work_dir'])
print('speech:', plugin_data['speech'])
print('result:', plugin_data['result'])
print('variables:', plugin_data['variables'])
print('chain:', plugin_data['chain'])
print('text_buffers:', plugin_data['text_buffers'])

# Производим операции с ними. Например, добавляем новую переменную:
variables = plugin_data['variables']
variables['example_plugin_var'] = 'Плагин определил свою переменную.'

# Для вывода в логи задайте сообщения списками с определёнными именами:
plugin_data['log_debug'] = [
    'Example plugin DEBUG string 1',
    'Example plugin DEBUG string 2',
]
plugin_data['log_info'] = [
    'Example plugin INFO string 1',
    'Example plugin INFO string 2',
]
plugin_data['log_warning'] = [
    'Example plugin WARNING string 1',
    'Example plugin WARNING string 2',
]
plugin_data['log_error'] = [
    'Example plugin DEBUG string 1',
    'Example plugin DEBUG string 2',
]
# Для версии 0.16 именами были: "debug", "info", "warnings" и "errors".
# Они будут вызывать "warning" с версии 0.20 и будут окончательно убраны
# в версии 0.30. Не используйте их.

# Для плагинов "plugin_before" и "plugin_after" блок-скрипта "simple_say"
# Вы можете переопределить результат выполнения блок скрипта, чтобы пойти по
# цепочке `fail`, например так:
plugin_data['result'] = False
# Для других типов блок скриптов это переопределение никак не повлияет.


######################
# Конец вашего кода. #
######################

# Перезаписываем файл с данными для возврата в диалог.
# Вы можете закомментировать этот код, если ничего не нужно сообщать диалогу,
# ни логов, ни переменных, ничего...
with open(filename, 'w') as f:
    json.dump(plugin_data, f)

# Обязательно указываем, что плагин успешно завершён, чтобы не прервать диалог.
sys.exit()
