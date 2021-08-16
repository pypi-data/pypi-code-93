#
# Copyright (c) 2020, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#
import logging
import re
import signal
import sys
from gettext import gettext as _

from astersay.exceptions import (
    AgiUnknownError, AgiAppError, AgiHangupError, AgiSighupError,
    AgiSigpipeError, AgiUsageError, AgiInvalidCommand
)

logger = logging.getLogger(__name__)

re_code = re.compile(r'(^\d+)\s*(.*)')
re_kv = re.compile(r'(?P<key>\w+)=(?P<value>[^\s]+)\s*(?:\((?P<data>.*)\))*')


def quote_value(string):
    if not isinstance(string, str):
        string = str(string)
    if '"' in string:
        raise ValueError(
            _('Строка %r содержит двойную кавычку.') % string)
    return '"%s"' % string


def digits_value(digits):
    if not isinstance(digits, str):
        digits = ''.join(map(str, digits))
    elif digits and not digits.isdigit():
        digits = ''.join([x for x in digits if x in x.isdigit()])
    return quote_value(digits)


class Agi:
    is_sighup = False
    is_hungup = False

    def __init__(self, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        signal.signal(signal.SIGHUP, self._handle_sighup)
        # Входящие параметры.
        self.params = {}
        # Исходящие переменные.
        self.export = {}
        self._parse_params()

    def _handle_sighup(self, signum, frame):
        """Обработка сигнала SIGHUP."""
        self.is_sighup = True

    def _parse_params(self):
        """Обработка входных параметров."""
        readline = self.stdin.readline
        params = self.params
        # Заметьте, что здесь неуместно логирование, так как, его настройки
        # ещё не переданы и в этом месте оно происходит по дефолтным настройкам.
        # Это значит, что информация не попадёт в нужный лог.
        stderr_write = self.stderr.write
        while True:
            line = readline().strip()
            if not line:
                break
            if type(line) is bytes:
                line = line.decode('utf8')
            # stderr_write('line = %r\n' % line)
            if ':' not in line:
                error = _('В строке %r нарушен параметр.') % line
                stderr_write(error + '\n')
                continue
            param = line.split(':', 1)
            key = param[0].strip()
            data = param[1].strip()
            if key != '':
                params[key] = data
                # stderr_write('param %r = %r\n' % (key, data))
            else:
                error = _('Пропуск пустого параметра.')
                stderr_write(error + '\n')

    def get_result(self):
        """Считывает результат исполнения команды в Asterisk."""
        readline = self.stdin.readline
        line = readline().strip()
        if type(line) is bytes:
            line = line.decode('utf8')
        logger.debug('RESULT_LINE: %s', line)
        # Если ответа нет совсем, то отдаём пустой результат.
        if not line:
            return
        code = 0
        result = {'result': ('', '')}
        match = re_code.search(line)
        if match:
            code, response = match.groups()
            logger.debug('code=%s, response=%s', code, response)
            code = int(code)

        if code == 200:
            for key, value, data in re_kv.findall(response):
                result[key] = (value, data)
                # If user hangs up... we get 'hangup' in the data
                if data == 'hangup':
                    self.is_hungup = True
                    raise AgiHangupError(
                        _('Абонент повесил трубку во время исполнения.'))
                if key == 'result' and value == '-1':
                    raise AgiAppError(
                        _('Ошибка выполнения в Asterisk или сброс звонка.'))
            logger.debug('RESULT_DICT: %s', result)
            return result
        elif code == 510:
            raise AgiInvalidCommand(response)
        elif code == 520:
            usage = [line]
            line = readline().strip()
            if type(line) is bytes:
                line = line.decode('utf8')
            while line[:3] != '520':
                usage.append(line)
                line = readline().strip()
                if type(line) is bytes:
                    line = line.decode('utf8')
            usage.append(line)
            usage = '%s\n' % '\n'.join(usage)
            raise AgiUsageError(usage)
        raise AgiUnknownError(_('Неопределенный код ответа: %d.') % code)

    def send_command(self, command: str, *args):
        """Отправляет команду в Asterisk."""
        command = command.strip()
        command = '%s %s' % (command, ' '.join(map(str, args)))
        command = command.strip() + '\n'
        stdout = self.stdout
        if 'b' in stdout.mode:
            command = command.encode('utf-8')
        try:
            stdout.write(command)
            stdout.flush()
        except BrokenPipeError:
            raise AgiSigpipeError(_('Ошибка в конвейере (SIGPIPE).'))
        logger.debug(_('Отправлена команда %r'), command)
        return command

    def test_hangup(self):
        """Проверка завершения разговора со стороны пользователя."""
        if self.is_sighup:
            raise AgiSighupError(
                _('Из Asterisk пришёл сигнал SIGHUP.'))
        if self.is_hungup:
            raise AgiHangupError(
                _('Абонент повесил трубку.'))
        logger.debug(_('Проверка состояния разговора прошла успешно.'))

    def execute(self, command, *args):
        self.test_hangup()
        self.send_command(command, *args)

    def set(self, variable, value):
        """
        Отправляет в Asterisk переменную без проверки состояния конвейера.
        """
        self.export[variable] = value
        self.send_command('SET VARIABLE', variable, quote_value(value))

    def verbose(self, message, level=1):
        """
        Отправляет в Asterisk команду VERBOSE без проверки состояния конвейера.
        """
        self.send_command('VERBOSE', quote_value(message), level)

    def stream_file(self, filename, escape_digits='', sample_offset=0):
        """
        Отправляет файл, позволяя прервать его цифрами, если они переданы.
        Цифры- это строка или список цифр. Если предусмотрено смещение файла,
        то воспроизведение начнётся с этого места.
        Возвращает нажатую цифру или 0, если она не была нажата.
        """
        escape_digits = digits_value(escape_digits)
        self.execute(
            'STREAM FILE', filename, escape_digits, sample_offset)

    def exec_command(self, command, *args):
        """
        Отправляет произвольную команду Asterisk с аргументами (даже команды не
        для AGI).
        """
        args = ','.join(map(str, args))
        return self.execute('EXEC', command, args)
