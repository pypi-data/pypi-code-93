import os
from datetime import datetime
from time import sleep

from divinegift.config import Settings
from divinegift.logger import set_loglevel, log_info, log_warning, log_err
from divinegift.main import get_args, get_log_param


class Application:
    def __init__(self):
        self.st = datetime.now()
        self.sp = datetime.now()
        self.args = get_args()
        self.lp = get_log_param(self.args)
        set_loglevel(self.lp.get('log_level'), self.lp.get('log_name'), self.lp.get('log_dir'))

        self.settings = Settings()
        self.settings_edited_at = None
        self.conf_file_path = self.args.get('c', 'settings.ini')
        self.cipher_key_path = self.args.get('ck', 'key.ck')

        self.print_intro()

        log_info(f'{"=" * 20} START {"=" * 20}')

    def __repr__(self):
        return f'Application()'

    def run(self):
        settings_edited_at = os.path.getmtime(self.conf_file_path)
        if settings_edited_at != self.settings_edited_at:
            self.set_settings()

    def run_service(self):
        while True:
            self.run()
            sleep(self.get_settings('service_wait', 5))

    def set_settings(self):
        self.settings.parse_settings(self.conf_file_path, self.cipher_key_path, ignore_parse_cnt=True)
        self.settings_edited_at = os.path.getmtime(self.conf_file_path)

        self.init_config()

    def init_config(self):
        if not os.path.exists('key.ck'):
            self.settings.initialize_cipher()
            self.encrypt_password('email_conf', 'pwd')
            self.settings.save_settings(self.conf_file_path)

    def encrypt_password(self, connection_name: str, pass_field: str = 'db_pass'):
        try:
            self.settings.encrypt_password(connection_name, pass_field)  # Change it for your config
        except Exception as ex:
            log_err(f'Could not encrypt password: {ex}')

    def get_settings(self, param=None, default=None):
        return self.settings.get_settings(param, default)

    def print_intro(self):
        print(f'Process {self.args.get("name")} started!')
        log_place = os.path.join(self.lp.get("log_dir"), self.lp.get("log_name")) if self.lp.get(
            "log_name") else "ON SCREEN"
        print(f'Log will be here: {log_place}')
