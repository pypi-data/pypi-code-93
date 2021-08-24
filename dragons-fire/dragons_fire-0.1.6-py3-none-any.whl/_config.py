import pathlib

PACKAGE_DIRECTORY = str(pathlib.Path(__file__).parent.resolve())
TEST_DATA_FOLDER = str(PACKAGE_DIRECTORY) + "/data"
PACKAGE_SECRETS_FILE = str(PACKAGE_DIRECTORY) + "/secrets.env"


class Show:
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_CYAN = '\033[96m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @classmethod
    def warning(cls, text):
        print(f'{cls.WARNING} {text}{cls.END}')

    @classmethod
    def info(cls, text):
        print(f'{cls.OK_BLUE} {text}{cls.END}')

    @classmethod
    def success(cls, text):
        print(f'{cls.BOLD}{cls.OK_GREEN} {text}{cls.END}')

    @classmethod
    def error(cls, text):
        print(f'{cls.FAIL} {text}{cls.END}')