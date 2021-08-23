from Crypto.Cipher import AES
from getpass import getpass
from pbkdf2 import PBKDF2
import base64
import os
import pickle

# Settings ###
try:
    saltSeed: str = os.environ['MIXIL_KEYS_SEED']
except KeyError:
    saltSeed: str = 'VR7g]^"^=S/76ZBU;g,'  # MAKE THIS YOUR OWN RANDOM STRING

PASSPHRASE_SIZE = 64  # 512-bit passphrase
KEY_SIZE = 32  # 256-bit key
BLOCK_SIZE = 16  # 16-bit blocks
IV_SIZE = 16  # 128-bits to initialise
SALT_SIZE = 8  # 64-bits of salt


def get_salt_for_key(key: str) -> str:
    return PBKDF2(key, saltSeed).read(SALT_SIZE)  # Salt is generated as the hash of the key with it's own salt acting like a seed value


def clear_all_keys(pass_folder=None):
    """
    Delete the files that have the keys. aka clear all the keys

    :param pass_folder: the folder where the encrypted files are stored, if None, will use $HOME
    :type pass_folder: str or None
    :return: void
    """
    if pass_folder is None:
        pass_folder = os.getenv("HOME")

    pass_phrase_file = os.path.join(pass_folder, '.secret.p')
    secret_sdb_file = os.path.join(pass_folder, '.secrets')

    if os.path.exists(pass_phrase_file):
        os.remove(pass_phrase_file)
    if os.path.exists(secret_sdb_file):
        os.remove(secret_sdb_file)


class MixilKeys:
    """
    This Class Store/retrieve usernames/passwords.
    by default it store the keys in the following files: $home/.secret.p and $home/.secrets

    you can make it more secure by setting your own Seed for the encryption, this can be done by setting the environment variable $Mixil_keys_seed


    *The code is based on the code in
    https://stackoverflow.com/questions/7014953/i-need-to-securely-store-a-username-and-password-in-python-what-are-my-options

    """

    def __init__(self, pass_folder=None):
        """

        you can make it more secure by setting your own Seed for the encryption, this can be done by setting the environment variable $Mixil_keys_seed

        :param pass_folder: the folder where the encrypted files are stored, if None, will use $HOME
        :type pass_folder: str or None
        """
        # Setup
        if pass_folder is None:
            pass_folder = os.getenv("HOME")

        self.pass_phrase_file = os.path.join(pass_folder, '.secret.p')
        self.secret_sdb_file = os.path.join(pass_folder, '.secrets')
        if os.path.isdir(self.pass_phrase_file) or os.path.isdir(self.secret_sdb_file):
            raise NameError('There is a folder with the same name, you need to remove the folders: {:s} and {:s} '
                            .format(self.pass_phrase_file, self.secret_sdb_file))
        # Acquire passphrase:
        try:
            with open(self.pass_phrase_file, 'rb') as f:
                passphrase = f.read()
            if len(passphrase) == 0:
                raise IOError
        except IOError:
            with open(self.pass_phrase_file, 'wb') as f:
                passphrase = os.urandom(PASSPHRASE_SIZE)  # Random passphrase
                f.write(base64.b64encode(passphrase))

                try:
                    os.remove(self.secret_sdb_file)  # If the passphrase has to be regenerated, then the old secrets file is irretrievable
                    # and should be removed
                except:
                    pass
        # else:
        #     passphrase = base64.b64decode(passphrase)  # Decode if loaded from already extant file

        # Load or create secrets database:
        try:
            with open(self.secret_sdb_file, 'rb') as f:
                db = pickle.load(f)
            if db == {}:
                raise IOError
        except (IOError, EOFError):
            db = {}
            with open(self.secret_sdb_file, 'wb') as f:
                pickle.dump(db, f)

    # System Functions

    def _read_passphrase(self) -> bytes:
        with open(self.pass_phrase_file, 'rb') as f:
            passphrase = f.read()
            passphrase = base64.b64decode(passphrase)
            return passphrase

    def _get_db(self) -> dict:

        with open(self.secret_sdb_file, 'rb') as f:
            db = pickle.load(f)
        return db

    def encrypt(self, plaintext: str, salt):
        """
        Pad plaintext, then encrypt it with a new, randomly initialised cipher. Will not preserve trailing whitespace in plaintext!
        """

        # Initialise Cipher Randomly
        init_vector = os.urandom(IV_SIZE)

        # Prepare cipher key:
        key = PBKDF2(self._read_passphrase(), salt).read(KEY_SIZE)

        cipher = AES.new(key, AES.MODE_CBC, init_vector)  # Create cipher

        return init_vector + cipher.encrypt(plaintext + ' ' * (BLOCK_SIZE - (len(plaintext) % BLOCK_SIZE)))  # Pad and encrypt

    def decrypt(self, ciphertext, salt):
        """ Reconstruct the cipher object and decrypt. Will not preserve trailing whitespace in the retrieved value!"""

        # Prepare cipher key:
        key = PBKDF2(self._read_passphrase(), salt).read(KEY_SIZE)

        # Extract IV:
        init_vector = ciphertext[:IV_SIZE]
        ciphertext = ciphertext[IV_SIZE:]

        cipher = AES.new(key, AES.MODE_CBC, init_vector)  # Reconstruct cipher (IV isn't needed for decryption so is set to zeros)

        return cipher.decrypt(ciphertext).rstrip(b' ')  # Decrypt and de-pad

    # User Functions ###

    def store(self, key: str, value: str):

        """
        Store key-value pair safely and save to disk.

        :param key: key name
        :param value: key value

        """
        db = self._get_db()

        db[key] = self.encrypt(value, get_salt_for_key(key))
        with open(self.secret_sdb_file, 'wb') as f:
            pickle.dump(db, f)

    def retrieve(self, key: str) -> str:
        """ Fetch key-value pair."""
        db = self._get_db()
        return self.decrypt(db[key], get_salt_for_key(key)).decode("utf-8")

    def require(self, key: str, msg=None, is_password: bool = True):
        """
        Test if key is stored, if not, prompt the user for it while hiding their input from shoulder-surfers.

        :param is_password:
        :param key: key name
        :type key: str
        :param msg: message for entering the key, if None it uses a default message
        :type msg: str or None
        """
        keys_db = self._get_db()
        if key not in keys_db:
            if msg is None:
                msg = f'Please enter a value for "{key:s}":'
            if is_password:
                self.store(key, getpass(msg))
            else:
                self.store(key, input(msg))

    def remove(self, key: str) -> bool:
        """
        Remove the key if exist
        :param key: key name
        :type key: str
        :return: True if it was removed, False else
        """
        db = self._get_db()
        if key in self._get_db():
            db.pop(key, None)
            with open(self.secret_sdb_file, 'wb') as f:
                pickle.dump(db, f)
            return True

        return False


if __name__ == '__main__':
    # Test (put your code here) ###
    mixil_keys = MixilKeys()

    mixil_keys.require('id')
    mixil_keys.require('password1')
    mixil_keys.require('password2')
    print('')
    print('Stored Data:')

    db_temp = mixil_keys._get_db()
    for key in db_temp:
        print('{:s}: {:s}'.format(key, mixil_keys.retrieve(key)))  # decode values on demand to avoid exposing the whole database in memory
