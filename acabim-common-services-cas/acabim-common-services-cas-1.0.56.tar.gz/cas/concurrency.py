import logging
import threading

_LOGGER = logging.getLogger('cas.model.concurrency')


class ResultThread(threading.Thread):

    @property
    def result(self):
        return self.__result

    def __init__(self, target, *args, **kwargs):
        if not callable(target):
            raise TypeError('expected callable function, not {0}'.format(type(target)))

        super(ResultThread, self).__init__(target=self.execute)
        self.__args = args
        self.__kwargs = kwargs
        self.__exec_method = target
        self.__result = None

    def execute(self):
        self.__result = self.__exec_method(*self.__args, **self.__kwargs)


class RetryThread(ResultThread):

    def __init__(self, target, retry_callback=None, retry_count=5, *args, **kwargs):
        if not callable(target):
            raise TypeError('expected callable function, not {0}'.format(type(target)))

        if retry_callback is not None and not callable(retry_callback):
            raise TypeError('expected callable function, not {0}'.format(type(retry_callback)))

        super(RetryThread, self).__init__(target, *args, **kwargs)
        self.__retry_callback = retry_callback
        self.__current_attempt = 0
        self.__max_retry = retry_count + 1

    def execute(self):
        while self.__current_attempt < self.__max_retry:
            try:
                _LOGGER.debug(f'Retry attempt {self.__current_attempt}')
                super(RetryThread, self).execute()
                if hasattr(self, '_RetryThread__current_exception'):
                    del self.__current_exception

                break
            except Exception as e:
                _LOGGER.exception(f'Retry Thread {threading.current_thread().name} Failed - '
                                  f'Attempt {self.__current_attempt}', exc_info=e)

                # noinspection PyAttributeOutsideInit
                self.__current_exception = e
                if self.__retry_callback is not None:
                    self.__retry_callback(self.__current_attempt, e)

                self.__current_attempt += 1
                continue

        if hasattr(self, '_RetryThread__current_exception'):
            raise self.__current_exception


class CallBackThread(RetryThread):

    def __init__(self, target, *args, callback=None, exception_callback=None, retry_callback=None, retry_count=5,
                 **kwargs):
        if callback is not None and not callable(callback):
            raise TypeError('expected callable function, not {0}'.format(type(callback)))

        if exception_callback is not None and not callable(exception_callback):
            raise TypeError('expected callable function, not {0}'.format(type(exception_callback)))

        super(CallBackThread, self).__init__(target, retry_callback, retry_count,
                                             *args, **kwargs)
        self.__callback = callback
        self.__exception_callback = exception_callback

    def execute(self):
        try:
            super(CallBackThread, self).execute()
            if self.__callback is not None:
                self.__callback(self.result)
        except Exception as e:
            if self.__exception_callback is not None:
                self.__exception_callback(e)
            else:
                raise e


# class CallBackThread(threading.Thread):
#     """A thread that contains a callback when the thread has finished running"""
#
#     def __init__(self, target, *args, callback=None, exception_callback=None, retry_callback=None, retry_count=5,
#                  **kwargs):
#         if not callable(target):
#             raise TypeError('expected callable function, not {0}'.format(type(target)))
#
#         if callback is not None and not callable(callback):
#             raise TypeError('expected callable function, not {0}'.format(type(callback)))
#
#         if exception_callback is not None and not callable(exception_callback):
#             raise TypeError('expected callable function, not {0}'.format(type(exception_callback)))
#
#         if retry_callback is not None and not callable(retry_callback):
#             raise TypeError('expected callable function, not {0}'.format(type(retry_callback)))
#
#         super(CallBackThread, self).__init__(target=self.__callback_target)
#         self.__args = args
#         self.__kwargs = kwargs
#         self.__callback = callback
#         self.__exception_callback = exception_callback
#         self.__retry_callback = retry_callback
#         self.__exec_method = target
#         self.__current_attempt = 0
#         self.__max_retry = retry_count + 1
#
#     def __callback_target(self):
#
#         while self.__current_attempt < self.__max_retry:
#             try:
#                 _LOGGER.debug(f'Retry attempt {self.__current_attempt}')
#                 self.__exec_method(*self.__args, **self.__kwargs)
#                 if hasattr(self, '_CallBackThread__current_exception'):
#                     del self.__current_exception
#                 if self.__callback is not None:
#                     self.__callback()
#
#                 break
#             except Exception as e:
#                 _LOGGER.exception(f'Callback Thread {threading.current_thread().name} Failed - '
#                                   f'Attempt {self.__current_attempt}', exc_info=e)
#
#                 self.__current_exception = e
#                 if self.__retry_callback is not None:
#                     self.__retry_callback(self.__current_attempt, e)
#
#                 self.__current_attempt += 1
#                 continue
#
#         if hasattr(self, '_CallBackThread__current_exception'):
#             if self.__exception_callback is not None:
#                 self.__exception_callback(self.__current_exception)
#             else:
#                 raise self.__current_exception

if __name__ == '__main__':
    a = -1


    def call():
        global a
        a = a + 1
        if a == 0:
            raise ValueError('')
        return 'Hello'


    c = CallBackThread(call)
    c.start()
    c.join()
    print(c.result)
