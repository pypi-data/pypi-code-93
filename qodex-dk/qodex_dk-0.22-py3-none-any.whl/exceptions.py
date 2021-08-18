""" Нативные исключения """


class NoSocket(Exception):
    # Исключение, возникающее при неизвестном имени терминала
    def __init__(self):
        text = 'QDK не запущен! Выполните команду make_connection.'
        super().__init__(text)
