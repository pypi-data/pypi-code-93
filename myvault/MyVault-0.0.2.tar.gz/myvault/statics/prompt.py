from colorama import Fore, Style

from myvault.statics.formatted_enum import FormattedEnum


class Prompt(FormattedEnum):
    CREATE_SQLITE_DB_CONFIRM = (
        "Vault database does not exist. \n" "Create? \n" "Only 'yes' will be accepted to approve: "
    )

    ADD_SECRET = "Secret to be added to the vault"

    UPDATE_SECRET_CONFIRM = (
        "A secret with the folder=`{folder}` and name=`{name}` already exists.\n"
        "Update its secret? \n"
        "Only 'yes' will be accepted to approve: "
    )

    REMOVE_SECRET_CONFIRM = (
        "Are you sure you want to remove the secret with the \n"
        "folder=`{folder}` and name=`{name}`? \n"
        "Only 'yes' will be accepted to approve: "
    )

    ENCRYPTION_UPDATE_CONFIRM = (
        "Are you sure you want to change the encryption configuration \n"
        "for `{db_path}` \n"
        "from `{config_path}` \n"
        "to `{new_config_path}`? \n"
        "Only 'yes' will be accepted to approve: "
    )

    def formatted(self, **kwargs) -> str:
        return f"\n{Fore.LIGHTBLUE_EX}>> {self.value.format(**kwargs)}{Style.RESET_ALL}"
