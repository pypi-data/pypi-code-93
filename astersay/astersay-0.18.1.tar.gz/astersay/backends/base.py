#
# Copyright (c) 2020, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#
import json
from audioop import rms
from gettext import gettext as _
from logging import getLogger
from os.path import exists
from time import time

from astersay.exceptions import TokenError


class Listener:
    chunk_size = 4000
    # Максимальный размер потокового файла для Яндекса - 10 мегабайт.
    max_size = 10485760
    amplitude_size = 2
    sample_width = 2
    total_size = 0
    _continue = True
    logger = getLogger('astersay.backends.Listener')

    def __init__(self, stream, amplitude=None):
        """
        :param stream: файлоподобный обЪект потока голоса.
        :param amplitude: список (пустой) для записи результатов посекундного
                          анализа потока.
        :type amplitude: list
        """
        self._stream = stream
        if amplitude is None:
            amplitude = []
        self.amplitude = amplitude

    def has_continue(self):
        return self._continue and (
            self.total_size + self.chunk_size < self.max_size)

    def listen(self):
        chunk_size = self.chunk_size
        stream_read = self._stream.read
        logger_debug = self.logger.debug

        amplitude = self.amplitude
        amplitude_size = self.amplitude_size
        sample_width = self.sample_width
        chunk_number = 0
        sample = b''
        sample_second = int(time())
        while self.has_continue():
            chunk_number += 1
            chunk_second = int(time())
            chunk = stream_read(chunk_size)
            length = len(chunk)
            if sample_second < chunk_second:
                rms_value = rms(sample, sample_width)
                # logger_debug('rms=%d', rms_value)
                amplitude.append((sample_second, rms_value))
                if len(amplitude) > amplitude_size:
                    amplitude.pop(0)
                sample = b''
                sample_second = chunk_second
            sample += chunk
            # logger_debug('chunck %d length is %d', chunk_number, length)
            if length == 0:
                self.stop()
            self.total_size += length
            yield chunk
        logger_debug('listener ended, total size %d', self.total_size)

    def stop(self):
        self._continue = False
        self.logger.debug('listener stopped')


class BaseBackend:

    def __init__(self):
        cls = self.__class__
        name = '%s.%s' % (cls.__module__, cls.__name__)
        self.logger = getLogger(name)

    def __str__(self):
        return str(self.__class__)[8:-2]


class BaseToken:
    min_length = 32

    def __init__(self, key, expiration):
        self.key = str(key)
        self.expiration = float(expiration)

    def __str__(self):
        valid = 'Valid Token' if self.is_valid else 'Invalid Token'
        if self.is_expired:
            seconds = '(EXPIRED)'
        else:
            seconds = '(%d seconds)' % (self.expiration - time())
        return '%s "%s" %s' % (valid, self.display, seconds)

    @property
    def display(self):
        key = self.key
        if key:
            return '%s...%s' % (key[:8], key[-8:])
        return 'invalid'

    def expires_less_than(self, seconds=0):
        """
        Возвращает True если токен истекает менее чем через N секунд.
        """
        return self.expiration - seconds < time()

    @property
    def is_expired(self):
        return self.expires_less_than(0)

    @property
    def is_valid(self):
        return len(self.key) >= self.min_length


class BaseTokenManager:
    ALLOWED_ALGORITHMS = (
        'HS256',
        'HS384',
        'HS512',
        'RS256',
        'RS384',
        'RS512',
        'PS256',
    )
    token = None
    token_class = BaseToken
    token_filename = None

    def __init__(self, logger=None, **kwargs):
        if not logger:
            logger = getLogger(self.__class__.__module__)
        self.logger = logger

    def generate_token(self):
        """
        Переопределите этот метод в вашем классе. Он должен
        генерировать и возвращать экземпляр токена.
        """
        raise NotImplementedError

    def update_token(self):
        if not self.token:
            self.load_token()
        token = self.token
        if token and token.is_valid and not token.expires_less_than(360):
            self.logger.info(_('Время обновления токена ещё не подошло.'))
            return token
        self.logger.debug(_('Старый токен нужно обновить: %s'), token)
        try:
            self.token = self.generate_token()
        except ConnectionError as e:
            self.logger.critical(
                _('Ошибка во время обновления токена.'), exc_info=e)
        else:
            self.logger.info(_('Токен обновлен.'))
            self.save_token()
        return self.token

    def load_token(self):
        """Загружает токен из файла."""
        filename = self.token_filename
        assert filename
        if exists(filename):
            self.logger.debug(_('Файл токена существует.'))
            try:
                data = json.load(open(filename))
                self.token = self.token_class(data['key'], data['expiration'])
            except (ValueError, KeyError) as e:
                # Перезаписываем его.
                self.logger.error(_('Ошибка в файле токена: %s'), e)
                self.token = self.token_class('', 0)
                self.save_token()
        else:
            self.logger.debug(_('Файла токена не существует.'))

        self.logger.debug(_('Загрузка токена завершена: %s'), self.token)
        return self.token

    def save_token(self):
        token = self.token
        assert token
        filename = self.token_filename
        assert filename
        data = {'key': token.key, 'expiration': token.expiration}
        json.dump(data, open(filename, 'w'), indent=4)
        self.logger.info(_('Токен сохранён в файл: %s'), filename)
        return data

    def validate(self):
        token = self.token
        if not token:
            raise TokenError(_('Токен не установлен.'))
        if not token.is_expired:
            raise TokenError(_('Токен устарел.'))
        if not token.is_valid:
            raise TokenError(_('Токен недействителен.'))
        self.logger.debug(_('Токен находится в актуальном состоянии.'))

    def get_headers(self):
        assert self.token
        headers = {
            'Authorization': 'Bearer %s' % self.token.key,
        }
        return headers

    def get_metadata(self):
        assert self.token
        metadata = (
            ('authorization', 'Bearer %s' % self.token.key),
        )
        return metadata
