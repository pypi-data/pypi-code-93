import logging
from georgstage.controller import Controller

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    app = Controller()
    app.main()
