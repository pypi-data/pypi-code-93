from Crypto.Cipher import AES
from Crypto.Hash import keccak, BLAKE2b, SHA256
from Crypto import Random
from base64 import b64encode, b64decode
from base58 import b58encode
from hashlib import pbkdf2_hmac
from market_place_cli.v_cloud_market_cli_common.config.wallet_config import WORD_LIST
from market_place_cli.v_cloud_market_cli_common.utils.vsyschain.error import throw_error
from market_place_cli.v_cloud_market_cli_common.utils.service_error import WalletDecryptionException, WalletEncryptionException
import axolotl_curve25519 as curve

class WalletCipher:

    def __init__(self, password):
        self.keyLength = 256
        self.hashingIterations = 9999
        self.encoding = "utf-8"
        self.keySalt = "0ba950e1-828b-4bae-9e06-faf078eb33ec"
        self.key = self.__hash_password(password)

    def encrypt(self, infoStr):
        try:
            raw = self.__pad(infoStr)
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(self.key[:32], AES.MODE_CBC, iv)
            return str(b64encode(iv + cipher.encrypt(raw)), encoding=self.encoding)
        except:
            msg = 'Fail to encrypt info string'
            throw_error(msg, WalletEncryptionException)

    def decrypt(self, raw):
        if raw is None:
            return None
        try:
            enc = b64decode(raw)
            iv = enc[:16]
            enc = enc[16:]
            cipher = AES.new(self.key[:32], AES.MODE_CBC, iv)
            return str(cipher.decrypt(enc), encoding = self.encoding).replace("\0", "")
        except:
            msg = "Failed to decrypt info string"
            throw_error(msg, WalletDecryptionException)

    def __hash_password(self, password):
        return pbkdf2_hmac("sha512", password.encode("utf-8"), self.keySalt.encode(self.encoding), self.hashingIterations, self.keyLength)

    def __pad(self, inStr):
        while len(inStr.encode(self.encoding)) % 16 != 0:
            inStr += "\0"
        return inStr.encode(self.encoding)

    @staticmethod
    def generate_phrase():
        wordCount = 2048
        phrase = ""
        ind_1 = ind_2 = ind_3 = 0
        x = int(0)
        for i in range(5):
            r = Random.get_random_bytes(4)
            x = (r[3] & 0xff) + \
                ((r[2] & 0xff) << 8) + \
                ((r[1] & 0xff) << 16) + \
                ((r[0] & 0xff) << 24)
            ind_1 = int(x % wordCount)
            ind_2 = int(((int(x / wordCount) >> 0) + ind_1) % wordCount)
            ind_3 = int(((int((int(x / wordCount) >> 0) / wordCount) >> 0) + ind_2) % wordCount)
            phrase += WORD_LIST[ind_1] + " "
            phrase += WORD_LIST[ind_2] + " "
            phrase += WORD_LIST[ind_3] + " "
        return phrase.strip(" ")

    @staticmethod
    def hash_chain(noncedSeed):
        """
        noncedSeed: bytes object
        return: bytes object
        """
        keccak_hash = keccak.new(digest_bits=256)
        blake_hash = BLAKE2b.new(digest_bits=256)
        tmp = blake_hash.update(noncedSeed).digest()
        result = keccak_hash.update(tmp).digest()
        return result

    @staticmethod
    def generate_keypair(seed):
        """
        seed: bytes object
        return: bytes object
        """
        sha256 = SHA256.new()
        sha256.update(seed)
        privateKey = curve.generatePrivateKey(sha256.digest())
        publicKey = curve.generatePublicKey(privateKey)
        return privateKey, publicKey

    @staticmethod
    def generate_address(pubKey, net="T"):
        """
        pubKey: bytes object
        return: bytes object
        """
        addrVer = bytes([5])
        chainId = bytes(net, "ascii")
        unchecksumedAddress = addrVer + chainId + WalletCipher.hash_chain(pubKey)[:20]
        address = b58encode(unchecksumedAddress + WalletCipher.hash_chain(unchecksumedAddress)[:4])
        return address

    @staticmethod
    def generate_account_info(seed, net='T', nonce=0):
        accSeed = WalletCipher.hash_chain((str(nonce) + seed).encode('utf-8'))
        priv, pub = WalletCipher.generate_keypair(accSeed)
        addr = WalletCipher.generate_address(pub, net).decode('utf-8')
        return {'nonce': nonce, 'accSeed': accSeed, 'priv': priv, 'pub': pub, 'addr': addr}
