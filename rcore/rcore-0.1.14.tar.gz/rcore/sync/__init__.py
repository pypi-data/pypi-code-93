""" Модуль для асинхронного выполнения неких действий """

from . import process, thread


class OnAsyncMixin(thread.OnThreadMixin, process.OnProcessMixin):
    """ Слияние миксинов OnThreadMixin и OnProcessMixin """
    