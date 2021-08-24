import subprocess
import sys
import logging


class SwiftSelectelStorage:
    def __init__(self, swift_user: str, swift_password: str, sel_id: str, sel_project_id: str):
        self.region_name = 'ru-1'
        self.auth_url = 'https://api.selcdn.ru'
        self.auth_version = '2'
        self.storage_url = f'https://api.selcdn.ru/v1/SEL_{sel_id}'
        self.username = swift_user
        self.password = swift_password
        self.project_id = sel_project_id
        self.tenant_id = sel_project_id
        self.general_args = [
            'swift',
            '--auth-version', self.auth_version,
            '--os-auth-url', self.auth_url,
            '--os-region-name', self.region_name,
            '--os-storage-url', self.storage_url,
            '--os-username', self.username,
            '--os-password', self.password,
            '--os-project-id', self.project_id,
            '--os-tenant-id', self.project_id
        ]

    def upload(self, bucket: str, src_file: str, dest_file: str, split_size_bytes: int = None, ttl_sec: int = None):
        add_args_split = []
        add_args_ttl = []
        if split_size_bytes:
            add_args_split = [
                '-S', str(split_size_bytes),
                '--segment-container', f'{bucket}-segments',
                '--use-slo',
            ]
        if ttl_sec:
            add_args_ttl = ['--header', f'X-Delete-After:{ttl_sec}' ]
        cmd = self.general_args + [
            'upload',
            '--object-name', dest_file
        ]
        cmd = cmd + add_args_split + add_args_ttl
        cmd += [bucket, src_file]
        print(' '.join(cmd))
        try:
            result = subprocess.run(cmd, check=True)
            print(result)
        except subprocess.CalledProcessError as e:
            logging.error('Cant upload to bucket')
            logging.error(e)
            sys.exit(1)
