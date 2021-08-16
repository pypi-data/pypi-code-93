#
# Copyright (c) 2020, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#
import pyaudio
import sys
import wave
from gettext import gettext as _
from os.path import exists
from threading import Thread
from time import time, sleep


class StreamIO:
    mode = '+'

    def __init__(self):
        self.data = []

    def write(self, content):
        self.data.append(content)

    def read(self, size=-1):
        raise NotImplementedError

    def readline(self, size=-1):
        pause = 0.2
        total = 30 / pause
        n = 0
        data = self.data
        while not data and n < total:
            sleep(pause)
            n += 1
        if not data:
            return ''
        return data.pop(0)

    def flush(self):
        pass

    def close(self):
        pass


class DummyAsterisk:

    AUDIO_CHUNK_SIZE = 1024
    READ_COMMAND_TIMEOUT = 0.2
    commands = (
        'GET VARIABLE', 'SET VARIABLE', 'VERBOSE', 'STREAM FILE', 'EXEC')
    stream = None
    is_stopped = False

    def __init__(self, agi_request=None, model='', workdir='',
                 stdin=None, stdout=None):
        if stdin is None:
            stdin = StreamIO()
        if stdout is None:
            stdout = StreamIO()
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = sys.stderr

        agi_args = [
            ('agi_request', agi_request or __file__),
            ('agi_channel', 'PJSIP/001-00000001'),
            ('agi_language', 'ru'),
            ('agi_type', 'PJSIP'),
            ('agi_uniqueid', str(round(time(), 2))),
            ('agi_version', '0.0.1'),
            ('agi_callerid', '001'),
            ('agi_calleridname', 'test'),
            ('agi_callingpres', '0'),
            ('agi_callingani2', '0'),
            ('agi_callington', '0'),
            ('agi_callingtns', '0'),
            ('agi_dnid', '1000'),
            ('agi_rdnis', 'unknown'),
            ('agi_context', 'from-internal'),
            ('agi_extension', '1000'),
            ('agi_priority', '4'),
            ('agi_enhanced', '1.0'),
            ('agi_accountcode', ''),
            ('agi_threadid', id(self)),
        ]
        if workdir:
            agi_args += [
                ('agi_arg_1', model),
                ('agi_arg_2', workdir),
            ]
        elif model:
            agi_args += [
                ('agi_arg_1', model),
            ]
        write = self.stdout.write
        for name, value in agi_args:
            # Передаём приложению.
            write('%s:%s\n' % (name, value))
        write('\n')
        self.stdout.flush()

        self.agi_args = agi_args
        self.variables = {}
        self.playlist = []

        self.audio = pyaudio.PyAudio()
        self._playback_process = None
        self._playback_args = None
        self._playback_cancel = False

    def parse_command(self, line):
        for command in self.commands:
            cmd = command + ' '
            if line.startswith(cmd) or line.startswith(cmd.lower()):
                method_name = 'command_' + command.replace(' ', '_').lower()
                method = getattr(self, method_name, None)
                if method:
                    start_string = False
                    args = []
                    for s in line[len(cmd):].split(' '):
                        start_quote = s.startswith('"')
                        end_quote = s.endswith('"')
                        if start_quote and end_quote and s != '"':
                            args.append(s.strip('"'))
                            start_string = False
                        elif start_quote and not start_string:
                            args.append(s[1:])
                            start_string = True
                        elif end_quote and start_string:
                            args[-1] += ' ' + s[:-1]
                            start_string = False
                        elif start_string:
                            args[-1] += ' ' + s
                        else:
                            args.append(s)
                    return method, args
        return None, ()

    def send_result(self, result, code=200):
        msg = '%d result=%s' % (code, result)
        self.stdout.write(msg + '\n')
        self.stdout.flush()
        # self.display('self.stdout.write(%r)' % msg)

    def display(self, *messages):
        write = self.stderr.write
        for m in messages:
            write(m + '\n')
        self.stderr.flush()

    def stop_record_audio(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            msg = _('Остановлен поток записи: %s') % self.stream
            self.display(msg)

    def start_record_audio(self):
        self.stop_record_audio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            rate=8000,
            channels=1,
            input=True,
            frames_per_buffer=self.AUDIO_CHUNK_SIZE
        )
        msg = _('Создан поток записи: %s') % self.stream
        self.display(msg)

    def stop_playback(self, clear=False, digit='0'):
        if clear:
            self.playlist.clear()
        self._playback_cancel = digit
        # Дожидаемся отключения процесса.
        while self._playback_process:
            self.display(_('Дожидаемся отключения старого процесса '
                           'проигрывания аудио.'))
            sleep(0.5)
            if not self._playback_process:
                self.display(_('Cтарый процесс проигрывания аудио завершён.'))
        # Оставшийся плейлист продолжается.
        if self.playlist:
            self.start_playback()
        return True

    def start_playback(self):

        def playback():
            self.display(_('Начинается плейлист.'))
            while self.playlist:
                filename, args = self.playlist.pop(0)
                self.display(
                    _('Проигрываем %s с агрументами %s') % (filename, args))
                self._playback_args = args
                try:
                    wfile = wave.open(filename, 'rb')
                except IOError:
                    self.display(_('Файл %s не найден.') % filename)
                    continue
                p = self.audio
                try:
                    stream = p.open(
                        format=p.get_format_from_width(wfile.getsampwidth()),
                        channels=wfile.getnchannels(),
                        rate=wfile.getframerate(),
                        output=True
                    )
                    chunk_size = self.AUDIO_CHUNK_SIZE
                    data = wfile.readframes(chunk_size)
                    while data and not self._playback_cancel:
                        stream.write(data)
                        data = wfile.readframes(chunk_size)
                    if not self._playback_cancel:
                        # Когда воспроизведение не было прервано.
                        self.variables['PLAYBACKSTATUS'] = 'SUCCESS'
                        self.send_result('0')
                    else:
                        self.send_result(self._playback_cancel)
                        self.display(_('Воспроизведение прервано.'))
                    sleep(0.5)
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    self.display(str(e))
            self._playback_process = None
            self._playback_args = None
            self.display(_('Плейлист окончен.'))

        if self._playback_process is None:
            self._playback_args = None
            self._playback_cancel = False
            self._playback_process = Thread(target=playback, daemon=True)
            self._playback_process.start()

    def play_audio(self, filename, *args, clear=False):
        if clear:
            self.stop_playback(clear)
        if exists(filename):
            pass
        elif exists(filename + '.wav'):
            filename += '.wav'
        # elif exists(filename + '.ogg'):
        #     filename += '.ogg'
        self.playlist.append([filename, args])
        self.start_playback()

    def start(self):
        readline = self.stdin.readline
        parse_command = self.parse_command
        while True:
            if self.is_stopped:
                break
            try:
                line = readline().strip()
            except KeyboardInterrupt:
                self.stop()
                break
            # self.display('line=%r' % line)
            if line and line in ('exit', 'quit'):
                self.stop()
                break
            elif line:
                method, args = parse_command(line)
                if method:
                    try:
                        method(*args)
                    except Exception as e:
                        self.display(str(e))
                else:
                    self.display(_('Метод не найден.'))
            else:
                sleep(self.READ_COMMAND_TIMEOUT)
        self.display(_('Сервер остановлен.'))

    def stop(self):
        self.display(_('Сервер останавливается.'))
        self.is_stopped = True
        # self.stdin.write('\n')
        self.stop_record_audio()
        self.stop_playback(clear=True)
        self.stdin.close()
        self.stdout.close()
        self.stderr.close()
        self.audio.terminate()
        self.display(_('Сервер остановлен.'))

    def command_get_variable(self, name: str):
        """
        GET VARIABLE VARIABLENAME
        Returns 0 if variablename is not set. Returns 1 if variablename is set
        and returns the variable in parentheses. Example return code:
        200 result=1 (testvariable)
        """
        if name not in self.variables:
            value = '0'
        else:
            value = '1 (%s)' % self.variables[name]
        self.send_result(value)

    def command_set_variable(self, name: str, value: str):
        """
        SET VARIABLE VARIABLENAME VALUE
        Sets a variable to the current channel.
        """
        self.variables[name] = value
        self.display('command_set_variable(%r, %r)' % (name, value))

    def command_verbose(self, message: str, level: str):
        """
        VERBOSE MESSAGE LEVEL
        Sends message to the console via verbose message system. Level is the
        verbose level (1-4). Always returns 1.
        """
        if level not in ('1', '2', '3', '4'):
            raise ValueError(
                _('Уровень должен быть от 1 до 4, level == %r') % level)
        self.display('command_verbose(%r, %r)' % (message, level))

    def command_stream_file(self, filename: str, escape_digits: str, sample_offset: str):
        """
        STREAM FILE FILENAME ESCAPE_DIGITS SAMPLE OFFSET
        Send the given file, allowing playback to be interrupted by the given
        digits, if any. Returns 0 if playback completes without a digit being
        pressed, or the ASCII numerical value of the digit if one was pressed,
        or -1 on error or if the channel was disconnected. If musiconhold is
        playing before calling stream file it will be automatically stopped
        and will not be restarted after completion.
        It sets the following channel variables upon completion:
        PLAYBACKSTATUS - The status of the playback attempt as a text string.
        SUCCESS
        FAILED
        """
        if escape_digits and not escape_digits.isdigit():
            raise ValueError(
                _('escape_digits должны быть цифрами, а не %r') % escape_digits)
        self.play_audio(filename, escape_digits, sample_offset, clear=True)
        self.display('command_stream_file(%r, %r, %r)' % (
            filename, escape_digits, sample_offset))

    def command_exec(self, application: str, options: str):
        """
        EXEC APPLICATION OPTIONS
        Executes application with given options.
        Returns whatever the application returns, or -2 on failure to
        find application.
        """
        self.display('command_exec(%r, %r)' % (application, options))
        if application.lower() == 'senddtmf':
            opts = [s.strip() for s in options.split(',')]
            if opts and opts[0].isdigit():
                digit = opts[0][0]
                args = self._playback_args
                if args and digit in args[0]:
                    self.display('_playback_args: %s' % str(args))
                    # Останавливаем текущее воспроизведение.
                    self.stop_playback(digit)
                    self.display(_('Отправлено нажатие %s.') % digit)
                return
        self.send_result('-2')


if __name__ == "__main__":
    server = DummyAsterisk(stdin=sys.stdin, stdout=sys.stdout)
    server.start()
