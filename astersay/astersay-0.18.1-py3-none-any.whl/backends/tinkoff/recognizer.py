#
#  Copyright (c) 2021. Egor Demushin.
#  All rights reserved.
#  This file is distributed under the same license as the current project.
#
import grpc
import threading
from gettext import gettext as _

from astersay.backends.base import Listener
from astersay.backends.tinkoff.base import TinkoffBaseBackend
from astersay.backends.tinkoff.proto import stt_pb2, stt_pb2_grpc


class TinkoffRecognizer(TinkoffBaseBackend):
    pause = True
    HOST = 'stt.tinkoff.ru:443'
    LANGUAGES = ('ru-RU',)
    AUDIO_ENCODINGS = ('LINEAR16', 'MULAW', 'ALAW', 'RAW_OPUS', 'MPEG_AUDIO')
    HERTZ_LIST = (8000, 16000, 32000, 48000)
    # Счётчик текущих предварительных результатов. Сбрасывается финальным.
    partials_counter = 0

    def __init__(self, settings):
        TinkoffBaseBackend.__init__(self)
        self.set_token_manager(settings)

        conf = settings.tinkoff

        recognizer = conf['recognizer']

        language = recognizer['language_code']
        assert language in self.LANGUAGES
        self.language = language

        self.profanity_filter = bool(recognizer['profanity_filter'])
        self.enable_automatic_punctuation = bool(recognizer['enable_automatic_punctuation'])

        audio_encoding = recognizer['audio_encoding']
        assert audio_encoding in self.AUDIO_ENCODINGS
        self.audio_encoding = getattr(stt_pb2.AudioEncoding, audio_encoding)

        sample_rate_hertz = recognizer['sample_rate_hertz']
        assert sample_rate_hertz in self.HERTZ_LIST
        self.sample_rate_hertz = sample_rate_hertz

        chunk_size = recognizer['chunk_size']
        assert 1024 <= chunk_size <= 4000 and chunk_size % 2 == 0
        self.chunk_size = chunk_size

        self.enable_interim_results = recognizer['enable_interim_results']
        self.interim_results_interval = recognizer['interim_results_interval']

        self._credentials = grpc.ssl_channel_credentials()

    def _build_first_request(self):
        request = stt_pb2.StreamingRecognizeRequest()
        config = request.streaming_config.config
        config.encoding = self.audio_encoding
        config.sample_rate_hertz = self.sample_rate_hertz
        config.num_channels = 1
        config.language_code = self.language
        config.profanity_filter = self.profanity_filter
        config.enable_automatic_punctuation = self.enable_automatic_punctuation
        interim_results_config = request.streaming_config.interim_results_config
        interim_results_config.enable_interim_results = self.enable_interim_results
        interim_results_config.interval = self.interim_results_interval
        return request

    def _generate_requests(self, listener):
        yield self._build_first_request()
        for chunk in listener.listen():
            if not self.pause:
                request = stt_pb2.StreamingRecognizeRequest()
                request.audio_content = chunk
                yield request

    def _recognize(self, listener):
        """Возвращает итератор ответов Тинькова."""
        self.token_manager.update_token()

        metadata = self.token_manager.get_metadata()
        try:
            stub = stt_pb2_grpc.SpeechToTextStub(
                grpc.secure_channel(self.HOST, self._credentials))
            responses = stub.StreamingRecognize(
                self._generate_requests(listener), metadata=metadata)
            for response in responses:
                for result in response.results:
                    yield result
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
        # Максимальный размер потокового файла для Тинькова не ограничен.
        # listener.max_size = 10485760
        listener.chunk_size = self.chunk_size

        text_to_text_buffer = dialog.text_to_text_buffer
        get_text_buffer = dialog.get_last_text_buffer

        # Максимальное время потока для Тинькова не ограничено.
        # Но мы ограничимся 60 минутами.
        timer = threading.Timer(3600, listener.stop)
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
            chunk = answer.recognition_result
            alternatives = chunk.alternatives
            text = alternatives[0].transcript
            logger_debug(_('Ответ Тинькова: %s'), text)
            if answer.is_final:
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
                alt = '\n'.join([a.transcript for a in alternatives if a.transcript])
                text_to_text_buffer(alt, fixed=False, text_buffer=text_buffer)
                self.partials_counter += 1
            if dialog.is_closed:
                listener.stop()
                logger_debug(_('Диалог прекратился и слушатель тоже.'))
                break
        logger_debug(_('Цикл завершён.'))
        timer.cancel()
        dialog.stream_size += listener.total_size
