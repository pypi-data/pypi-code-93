#
# Copyright (c) 2020, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#
import grpc
import threading
from gettext import gettext as _

from astersay.backends.base import Listener
from astersay.backends.yandex.base import YandexBaseBackend
# from yandex.cloud.ai.stt.v2.stt_service_pb2 (
#     RecognitionSpec, RecognitionConfig, StreamingRecognitionReques
# )
# from yandex.cloud.ai.stt.v2.stt_service_pb2_grpc import SttServiceStub
from astersay.backends.yandex.proto.stt_service_pb2 import (
    RecognitionSpec, RecognitionConfig, StreamingRecognitionRequest,
)
from astersay.backends.yandex.proto.stt_service_pb2_grpc import SttServiceStub


class YandexRecognizer(YandexBaseBackend):
    pause = True
    HOST = 'stt.api.cloud.yandex.net:443'
    LANGUAGES = ('ru-RU', 'en-US', 'tr-TR')
    MODELS = {
        'ru-RU': ('general', 'general:rc'),
        'tr-TR': ('general', 'maps'),
        'en-US': ('general', 'maps'),
    }
    AUDIO_ENCODINGS = ('LINEAR16_PCM', 'OGG_OPUS')
    HERTZ_LIST = (48000, 16000, 8000)
    # Счётчик текущих предварительных результатов. Сбрасывается финальным.
    partials_counter = 0

    def __init__(self, settings):
        YandexBaseBackend.__init__(self)
        self.set_token_manager(settings)

        conf = settings.yandex
        self.folder_id = conf['auth']['folder_id']

        recognizer = conf['recognizer']

        language = recognizer['language_code']
        assert language in self.LANGUAGES
        self.language = language

        model = recognizer['model']
        assert model in self.MODELS[language]
        self.model = model

        self.profanity_filter = bool(recognizer['profanity_filter'])
        self.partial_results = bool(recognizer['partial_results'])
        self.single_utterance = bool(recognizer['single_utterance'])
        self.raw_results = bool(recognizer['raw_results'])

        audio_encoding = recognizer['audio_encoding']
        assert audio_encoding in self.AUDIO_ENCODINGS
        self.audio_encoding = audio_encoding

        sample_rate_hertz = recognizer['sample_rate_hertz']
        assert sample_rate_hertz in self.HERTZ_LIST
        self.sample_rate_hertz = sample_rate_hertz

        chunk_size = recognizer['chunk_size']
        assert 1024 <= chunk_size <= 4000 and chunk_size % 2 == 0
        self.chunk_size = chunk_size

        self._credentials = grpc.ssl_channel_credentials()

    def _recognize(self, listener):
        """Возвращает итератор ответов Яндекса."""
        self.token_manager.update_token()

        # Задаём настройки распознавания.
        specification = RecognitionSpec(
            language_code=self.language,
            model=self.model,
            profanity_filter=self.profanity_filter,
            partial_results=self.partial_results,
            single_utterance=self.single_utterance,
            # raw_results=self.raw_results,  # TODO: Не работает, починить.
            audio_encoding=self.audio_encoding,
            sample_rate_hertz=self.sample_rate_hertz
        )
        streaming_config = RecognitionConfig(
            specification=specification, folder_id=self.folder_id)

        def get_request_iter():
            # Отправляется сообщение с настройками распознавания.
            yield StreamingRecognitionRequest(config=streaming_config)
            for chunk in listener.listen():
                if self.pause:
                    chunk = b''
                yield StreamingRecognitionRequest(audio_content=chunk)

        # Установить соединение с сервером.
        channel = grpc.secure_channel(self.HOST, self._credentials)
        stub = SttServiceStub(channel)
        metadata = self.token_manager.get_metadata()
        iter = stub.StreamingRecognize(get_request_iter(), metadata=metadata)
        try:
            for value in iter:
                yield value
        except grpc._channel._MultiThreadedRendezvous as e:
            self.logger.warning(
                'Stop iteration by _MultiThreadedRendezvous.code=%s.',
                e._state.code)
        except Exception as e:
            self.logger.critical(str(e), exc_info=e)

    def listen(self, dialog):
        """
        Распознавание текста для диалога производится вплоть до его завершения
        или превышения объёма стрима. Возвращает итератор текста.
        """
        logger_debug = self.logger.debug
        logger_info = self.logger.info
        logger_info(_('Начинается распознавание речи для диалога.'))

        listener = Listener(dialog.stream, dialog.amplitude)
        self.listener = listener
        # Максимальный размер потокового файла для Яндекса - 10 мегабайт.
        listener.max_size = 10485760
        listener.chunk_size = self.chunk_size

        text_to_text_buffer = dialog.text_to_text_buffer
        get_text_buffer = dialog.get_last_text_buffer

        # Максимальное время потока для Яндекса - 5 минут.
        timer = threading.Timer(300, listener.stop)
        timer.start()
        self.partials_counter = 0
        text_buffer = None
        for answer in self._recognize(listener):
            # Каждый раз получаем самый последний буфер, т.к. он может быть
            # создан в процессе работы. Но для сохранения финальных результатов
            # используем запомненный.
            if text_buffer is None:
                text_buffer = get_text_buffer()
                logger_info(_('Работаем с буфером %s'), text_buffer.key)
            chunk = answer.chunks[0]
            alternatives = chunk.alternatives
            text = alternatives[0].text
            logger_debug(_('Ответ Яндекса: %s'), text)
            if chunk.final:
                logger_info(
                    _('Финальный текст в буфер %(buffer)s: %(text)s'),
                    {'text': text, 'buffer': text_buffer.key}
                )
                text_to_text_buffer(text, fixed=True, text_buffer=text_buffer)
                self.partials_counter = 0
                # После каждого финального текста сбрасываем привязку к буферу.
                text_buffer = None
            else:
                logger_debug(
                    _('Предварительный текст в буфер %(buffer)s: %(text)s'),
                    {'text': text, 'buffer': text_buffer.key}
                )
                alt = '\n'.join([a.text for a in alternatives if a.text])
                text_to_text_buffer(alt, fixed=False, text_buffer=text_buffer)
                self.partials_counter += 1
            if dialog.is_closed:
                listener.stop()
                logger_debug(_('Диалог прекратился и слушатель тоже.'))
                break
        logger_debug(_('Цикл завершён.'))
        timer.cancel()
        dialog.stream_size += listener.total_size
