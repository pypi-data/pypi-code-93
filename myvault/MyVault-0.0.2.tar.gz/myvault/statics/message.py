from colorama import Fore, Style

from myvault.statics.formatted_enum import FormattedEnum


class Message(FormattedEnum):
    DB_CREATED = "Vault database is created `{db_path}`."

    DB_CONN_CLOSED = "Connection to the vault database is closed."

    DB_REQUIRED_WARNING = "Cannot continue without creating a vault database."

    CONFIG_KEY_WARNING = (
        "Config file is missing either a section: `cipher`, \n"
        "or the key(s): `KEY`, `SALT`, `ITERATIONS`, `CLIPBOARD_TTL`."
    )

    CONFIG_VALUE_WARNING = (
        "Values of `KEY`, `SALT`, `ITERATIONS`, and `CLIPBOARD_TTL` \n"
        "must be of type `string`, `string`, `integer` and `integer` respectively."
    )

    SECRET_INSERTED = "Secret with folder=`{folder}`, name=`{name}` is inserted."

    SECRET_UPDATED = "Secret with folder=`{folder}`, name=`{name}` is updated."

    UPDATE_ABORTED = "Update secret is aborted."

    SECRET_DELETED = "Secret with folder=`{folder}`, name=`{name}`, if exists, is deleted."

    REMOVE_ABORTED = "Delete secret is aborted."

    SECRET_NOT_FOUND = "Secret not found with folder=`{folder}`, name=`{name}`."

    SECRET_COPIED = (
        "Secret with folder=`{folder}`, name=`{name}` \n"
        "is copied to clipboard for {ttl} seconds. \n"
        "Press Ctrl+C if done early."
    )

    INVALID_CONFIG_WARNING = (
        "Could not decrypt the secret. Please confirm that the config file is correct and try again."
    )

    ENCRYPTION_UPDATED = (
        "Encryption is updated using new config file. \n"
        "A copy of vault database with old encryption config \n"
        "is saved to `{db_path}` for backup."
    )

    ENCRYPTION_UPDATE_FAILED = "Encryption update failed."

    ENCRYPTION_ABORTED = "Encryption using new config file is aborted."

    FOLDERS_NAMES_PRINT = "Folder/Names in the vault database:"

    def formatted(self, **kwargs) -> str:
        return f"\n{Fore.LIGHTBLUE_EX}>> {self.value.format(**kwargs)}{Style.RESET_ALL}"

    def __str__(self) -> str:
        return f"\n{Fore.LIGHTBLUE_EX}>> {self.value}{Style.RESET_ALL}"
