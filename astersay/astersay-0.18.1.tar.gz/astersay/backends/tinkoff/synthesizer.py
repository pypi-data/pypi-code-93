#
#  Copyright (c) 2021. Egor Demushin.
#  All rights reserved.
#  This file is distributed under the same license as the current project.
#

import grpc
from gettext import gettext as _

from astersay.backends.tinkoff.base import TinkoffBaseBackend
from astersay.backends.tinkoff.proto import tts_pb2_grpc, tts_pb2
from astersay.utils import make_voice


class TinkoffSynthesizer(TinkoffBaseBackend):
    HOST = 'tts.tinkoff.ru:443'
    LANGUAGES = ('ru-RU',)
    VOICES = {
        'ru-RU': ('alyona', 'maxim'),
    }
    AUDIO_FORMATS = ('lpcm', 'oggopus')
    HERTZ_LIST = (8000, 16000, 32000, 48000)

    def __init__(self, settings):
        TinkoffBaseBackend.__init__(self)
        self.set_token_manager(settings)

        conf = settings.tinkoff

        synthesizer = conf['synthesizer']
        self.storage_path = synthesizer['storage']
        self.convertor = synthesizer['convertor']

        language = synthesizer['lang']
        assert language in self.LANGUAGES
        self.language = language

        voice = synthesizer['voice']
        assert voice in self.VOICES[language]
        self.voice = voice

        speed = synthesizer['speed']
        assert 0.1 <= speed <= 3.0
        self.speed = speed

        audio_format = synthesizer['format']
        assert audio_format in self.AUDIO_FORMATS
        self.audio_format = audio_format

        sample_rate_hertz = synthesizer['sample_rate_hertz']
        assert sample_rate_hertz in self.HERTZ_LIST
        self.sample_rate_hertz = sample_rate_hertz

        self._credentials = grpc.ssl_channel_credentials()

    @property
    def message_params(self):
        return {
            'synthesizer': 'tinkoff',
            'lang': self.language,
            'voice': self.voice,
            'speed': self.speed,
            'sample_rate': self.sample_rate_hertz,
        }

    @property
    def _audio_config(self):
        return tts_pb2.AudioConfig(
            audio_encoding=tts_pb2.LINEAR16,
            sample_rate_hertz=self.sample_rate_hertz,
            speaking_rate=self.speed
        )

    @property
    def _voice_config(self):
        return tts_pb2.VoiceSelectionParams(
            name=self.voice,
            language_code=self.language
        )

    def build_request(self, text=''):
        return tts_pb2.SynthesizeSpeechRequest(
            input=tts_pb2.SynthesisInput(text=text),
            audio_config=self._audio_config,
            voice=self._voice_config
        )

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

        stub = tts_pb2_grpc.TextToSpeechStub(
            grpc.secure_channel(self.HOST, self._credentials))
        request = self.build_request(text=message['text'])
        metadata = self.token_manager.get_metadata()
        try:
            response = stub.Synthesize(request, metadata=metadata)
            return response.audio_content
        except Exception as e:
            self.logger.warning(_('Ошибка синтеза речи. %s'), e)

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
