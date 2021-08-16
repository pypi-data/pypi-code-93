#
# Copyright (c) 2020, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#
import requests
from gettext import gettext as _

from astersay.backends.yandex.base import YandexBaseBackend
from astersay.utils import make_voice


class YandexSynthesizer(YandexBaseBackend):
    URL = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    LANGUAGES = ('ru-RU', 'en-US', 'tr-TR')
    VOICES = {
        'ru-RU': ('oksana', 'jane', 'omazh', 'zahar', 'ermil',
                  'alena', 'filipp'),
        'tr-TR': ('silaerkan', 'erkanyavas'),
        'en-US': ('alyss', 'nick'),
    }
    EMOTIONS = ('good', 'evil', 'neutral')
    AUDIO_FORMATS = ('lpcm', 'oggopus')
    HERTZ_LIST = (48000, 16000, 8000)

    def __init__(self, settings):
        YandexBaseBackend.__init__(self)
        self.set_token_manager(settings)

        conf = settings.yandex
        self.folder_id = conf['auth']['folder_id']

        synthesizer = conf['synthesizer']
        self.storage_path = synthesizer['storage']
        self.convertor = synthesizer['convertor']

        language = synthesizer['lang']
        assert language in self.LANGUAGES
        self.language = language

        voice = synthesizer['voice']
        assert voice in self.VOICES[language]
        self.voice = voice

        emotion = synthesizer['emotion']
        assert emotion in self.EMOTIONS
        self.emotion = emotion

        speed = synthesizer['speed']
        assert 0.1 <= speed <= 3.0
        self.speed = speed

        audio_format = synthesizer['format']
        assert audio_format in self.AUDIO_FORMATS
        self.audio_format = audio_format

        sample_rate_hertz = synthesizer['sample_rate_hertz']
        assert sample_rate_hertz in self.HERTZ_LIST
        self.sample_rate_hertz = sample_rate_hertz

    @property
    def message_params(self):
        return {
            'lang': self.language,
            'voice': self.voice,
            'emotion': self.emotion,
            'speed': self.speed,
            'folderId': self.folder_id,
            'format': self.audio_format,
            'sampleRateHertz': self.sample_rate_hertz,
        }

    def make_message(self, text):
        """
        Создаёт полное сообщение для отправки на сервер и записи в
        спецификацию голосового файла.
        """
        assert len(text) <= 5000
        message = self.message_params
        message['text'] = text
        return message

    def synthesize(self, message):
        """
        Делает запрос сообщения на сервер и возвращает чистые audio-данные
        ответа или None.
        """
        assert isinstance(message, dict)
        self.token_manager.update_token()
        logger_debug = self.logger.debug

        headers = self.token_manager.get_headers()
        logger_debug(_('Заголовки синтеза речи: %s'), headers)
        logger_debug(_('Параметры синтеза речи: %s'), message)
        response = requests.post(self.URL, data=message, headers=headers)
        if response.ok:
            logger_debug(_('Синтез речи выполнен.'))
            # Возвращаем данные полученного файла.
            return response.content
        self.logger.warning(
            _('Ошибка синтеза речи. Сервер вернул код, отличный от 200. %s'),
            response.text,
        )

    def make_voice(self, text, early=False):
        """
        Ищет или создаёт голосовой файл для переданного текста,
        сохраняет его на диск и возвращает в виде пути без расширения,
        пригодного для передачи Астериску.
        """
        return make_voice(
            logger=self.logger,
            convertor=self.convertor,
            synthesize=self.synthesize,
            make_message=self.make_message,
            storage_path=self.storage_path,
            text=text,
            early=early
        )
