import configparser
import shutil
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Tuple

import pyperclip

from myvault.statics import ExitCode, Message, Prompt, Query
from myvault.utils import AESEncryption, Database


class Vault(AESEncryption):
    def __init__(self, db_path: Path, config_path: Path):
        key, salt, iterations, clipboard_ttl = self.__get_cipher_params(config_path=config_path)
        super().__init__(key=key, salt=salt, iterations=iterations)
        self.__set_db(db_path=db_path)
        self.__config_path = config_path
        self.clipboard_ttl = clipboard_ttl

    def __enter__(self):
        return self

    @staticmethod
    def __get_cipher_params(config_path: Path) -> Tuple[str, str, int, int]:
        config = configparser.ConfigParser()
        config.read(filenames=config_path, encoding="utf-8")
        try:
            return (
                config["cipher"]["key"],
                config["cipher"]["salt"],
                int(config["cipher"]["iterations"]),
                int(config["cipher"]["clipboard_ttl"]),
            )
        except KeyError:
            print(Message.CONFIG_KEY_WARNING)
            sys.exit(ExitCode.INVALID_KEY)
        except ValueError:
            print(Message.CONFIG_VALUE_WARNING)
            sys.exit(ExitCode.INVALID_VALUE)

    def __set_db(self, db_path: Path):
        if db_path.is_file() is False:
            create = input(Prompt.CREATE_SQLITE_DB_CONFIRM.formatted())
            if create != "yes":
                print(Message.DB_REQUIRED_WARNING)
                sys.exit(0)

            db_path.parent.mkdir(exist_ok=True)
            print(Message.DB_CREATED.formatted(db_path=db_path))
        else:
            pass
        self.db = Database(db_path=db_path)
        self.__db_path = db_path

    def upsert(self, folder: str, name: str, secret: str):
        secret_encrypted = self.encrypt(plaintext=secret)
        try:
            self.db.insert_secret(folder=folder, name=name, secret=secret_encrypted)
            print(Message.SECRET_INSERTED.formatted(folder=folder, name=name))
        except sqlite3.IntegrityError:
            update = input(Prompt.UPDATE_SECRET_CONFIRM.formatted(folder=folder, name=name))
            if update != "yes":
                print(Message.UPDATE_ABORTED)
                sys.exit(0)

            self.db.update_secret(folder=folder, name=name, new_secret=secret_encrypted)
            print(Message.SECRET_UPDATED.formatted(folder=folder, name=name))

    def list_(self):
        print(Message.FOLDERS_NAMES_PRINT)
        for (folder, name) in self.db.select_folder_and_names():
            print(f"{folder}/{name}")

    def copy(self, folder: str, name: str, get: bool = False):
        secret_encrypted = self.db.select_secret(folder=folder, name=name)
        if secret_encrypted is None:
            print(Message.SECRET_NOT_FOUND.formatted(folder=folder, name=name))
            sys.exit(ExitCode.SECRET_NOT_FOUND)
        else:
            try:
                secret_decrypted = self.decrypt(ciphertext=secret_encrypted)
            except UnicodeDecodeError:
                print(Message.INVALID_CONFIG_WARNING)
                sys.exit(ExitCode.INVALID_CONFIG)

            if get is True:
                return secret_encrypted
            else:
                print(Message.SECRET_COPIED.formatted(folder=folder, name=name, ttl=self.clipboard_ttl))
                self.__clipboard_copy(text=secret_decrypted, ttl_secs=self.clipboard_ttl)

    @staticmethod
    def __clipboard_copy(text: str, ttl_secs: int = 10):
        pyperclip.copy(text)
        try:
            time.sleep(ttl_secs)
        except KeyboardInterrupt:
            pass
        finally:
            pyperclip.copy("")

    def update_encryption(self, new_config_path: Path):
        update = input(
            Prompt.ENCRYPTION_UPDATE_CONFIRM.formatted(
                db_path=self.__db_path, config_path=self.__config_path, new_config_path=new_config_path
            )
        )
        if update != "yes":
            print(Message.ENCRYPTION_ABORTED)
            sys.exit(0)

        update_params = list()
        key, salt, iterations, _ = self.__get_cipher_params(config_path=new_config_path)
        new_cipher = AESEncryption(key=key, salt=salt, iterations=iterations)
        for (folder, name, secret_encrypted) in self.db.select_all():
            time_now = datetime.now()
            secret_decrypted = self.decrypt(secret_encrypted)
            new_secret_encrypted = new_cipher.encrypt(plaintext=secret_decrypted)
            update_params.append((new_secret_encrypted, time_now, folder, name))

        backup_db_path = self.__backup_db()
        try:
            self.db.execute_many(Query.UPDATE_SECRET.formatted(), update_params)
            print(Message.ENCRYPTION_UPDATED.formatted(db_path=backup_db_path))
        except Exception:
            print(Message.ENCRYPTION_UPDATE_FAILED)
            backup_db_path.unlink()

    def __backup_db(self) -> Path:
        time_now = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = self.__db_path.suffix
        new_path = self.__db_path.with_suffix(f".backup_{time_now}{extension}")
        shutil.copy2(self.__db_path, new_path)
        return new_path

    def remove(self, folder: str, name: str):
        remove = input(Prompt.REMOVE_SECRET_CONFIRM.formatted(folder=folder, name=name))
        if remove != "yes":
            print(Message.REMOVE_ABORTED)
            sys.exit(0)

        self.db.delete_secret(folder=folder, name=name)
        print(Message.SECRET_DELETED.formatted(folder=folder, name=name))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(self.db, Database):
            self.db.close()
            print(Message.DB_CONN_CLOSED)
