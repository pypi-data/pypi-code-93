import monocypher


class EncChaCha20:
    def __init__(self, key: bytes) -> None:
        self.key = key
        self.nonce = b'l0n0lnat'

    def encode(self, data: bytes) -> bytearray:
        return monocypher.chacha20(self.key, self.nonce, data)

    def decode(self, data: bytes) -> bytearray:
        return monocypher.chacha20(self.key, self.nonce, data)
