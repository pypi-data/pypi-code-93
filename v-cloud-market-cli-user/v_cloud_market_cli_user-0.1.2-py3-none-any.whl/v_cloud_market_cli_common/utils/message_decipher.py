from nacl.public import PrivateKey, SealedBox
import base58


def decrypt_message(public_key, msg):
    private_key = PrivateKey(base58.b58decode(public_key))
    box = SealedBox(private_key)
    return box.decrypt(base58.b58decode(msg)).decode('UTF-8')
