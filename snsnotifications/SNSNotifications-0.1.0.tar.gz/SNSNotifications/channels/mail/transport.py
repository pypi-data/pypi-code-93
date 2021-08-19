from .mailable import Mailable


class Transport:

    def send(self, mailable: Mailable):
        raise NotImplementedError()
