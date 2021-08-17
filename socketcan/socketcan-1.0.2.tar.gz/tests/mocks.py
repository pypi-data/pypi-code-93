""" mock objects for socketcan

(c) Patrick Menschel 2021

"""


class MockSocket:

    def recv(self, bufsize):
        return bytes(100)

    def close(self):
        return
