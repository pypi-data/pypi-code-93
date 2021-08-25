class Logger:

    @staticmethod
    def log(message):
        print(f'Log - {message}')

    @staticmethod
    def error(message):
        print(f'Error - {message}')

    @staticmethod
    def debug(message):
        print(f'debug - {message}')
