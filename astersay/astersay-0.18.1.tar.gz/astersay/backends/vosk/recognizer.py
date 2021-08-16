#
# Copyright (c) 2020, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#
from gettext import gettext as _
from json import loads, dumps
from threading import Timer
from websocket import create_connection

from astersay.backends.base import BaseBackend, Listener


class VoskRecognizer(BaseBackend):
    pause = True

    HERTZ_LIST = (48000, 16000, 8000)
    # Счётчик текущих предварительных результатов. Сбрасывается финальным.
    partials_counter = 0

    def __init__(self, settings):
        BaseBackend.__init__(self)

        conf = settings.vosk
        recognizer = conf['recognizer']

        sample_rate_hertz = recognizer['sample_rate_hertz']
        assert sample_rate_hertz in self.HERTZ_LIST
        self.sample_rate_hertz = sample_rate_hertz

        chunk_size = recognizer['chunk_size']
        assert chunk_size >= 1024 and chunk_size % 2 == 0
        self.chunk_size = chunk_size

        max_size = recognizer['max_size']
        assert max_size >= 1048576 and max_size % 2 == 0
        self.max_size = max_size

        max_time = recognizer['max_time']
        assert max_time >= 1
        self.max_time = max_time

        self.host = conf['connection']['host']
        self.port = conf['connection']['port']

    def create_connection(self, config=None):
        self.ws = None
        try:
            # Создаём сединение с сервером Vosk.
            ws = create_connection("ws://%s:%d" % (self.host, self.port))
        except Exception as e:
            self.logger.critical(str(e), exc_info=e)
            return
        if not ws.connected:
            self.logger.critical(_('Соединение с вэбсокетом было закрыто.'))
            return
        # TODO: сделать проверку соединения.
        # Отправляем конфигурацию, она запомнится для сокет-соединения.
        if config:
            # config = {
            #     'word_list': 'да нет наверное ага хорошо лады окей',
            #     'sample_rate': 8000,
            # }
            ws.send(dumps({'config': config}))
        self.ws = ws
        return ws

    def _recognize(self, listener):
        """Возвращает итератор ответов Vosk."""
        ws = self.ws
        send = ws.send_binary
        recv = ws.recv
        try:
            for chunk in listener.listen():
                if self.pause:
                    chunk = b''
                send(chunk)
                yield loads(recv())
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

        ws = self.create_connection()
        if not ws:
            # Мы вынуждены завершать диалог, если распознавание не работает.
            dialog.stop()
            return

        listener = Listener(dialog.stream, dialog.amplitude)
        self.listener = listener
        # Максимальный размер потокового файла для Vosk задаётся настройками.
        listener.max_size = self.max_size
        listener.chunk_size = self.chunk_size

        text_to_text_buffer = dialog.text_to_text_buffer
        get_text_buffer = dialog.get_last_text_buffer

        # Максимальное время потока для Vosk - 5 минут.
        timer = Timer(self.max_time, listener.stop)
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
            logger_debug(_('Ответ Vosk: %s'), answer)
            if 'result' in answer:
                text = answer['text']
                logger_info(
                    _('Финальный текст в буфер %(buffer)s: %(text)s'),
                    {'text': text, 'buffer': text_buffer.key}
                )
                text_to_text_buffer(text, fixed=True, text_buffer=text_buffer)
                self.partials_counter = 0
                # После каждого финального текста сбрасываем привязку к буферу.
                text_buffer = None
            elif 'partial' in answer:
                text = answer['partial']
                logger_debug(
                    _('Предварительный текст в буфер %(buffer)s: %(text)s'),
                    {'text': text, 'buffer': text_buffer.key}
                )
                text_to_text_buffer(text, fixed=False, text_buffer=text_buffer)
                self.partials_counter += 1
            if dialog.is_closed:
                listener.stop()
                logger_debug(_('Диалог прекратился и слушатель тоже.'))
                break
        logger_debug(_('Цикл завершён.'))
        timer.cancel()
        dialog.stream_size += listener.total_size
