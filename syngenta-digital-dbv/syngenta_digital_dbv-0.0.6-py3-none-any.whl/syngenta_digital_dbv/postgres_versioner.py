from psycopg2.extensions import AsIs

from syngenta_digital_dbv.common.config import Config
from syngenta_digital_dbv.common.directory_scanner import DirectoryScanner
from syngenta_digital_dbv.common.sql_connector import SQLConnector


class PostgresVersioner:

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)
        self.version_scanner = DirectoryScanner(directory=kwargs['versions_directory'], extension='.sql')
        self.seed_scanner = DirectoryScanner(directory=kwargs.get('seed_directory'), extension='.sql')
        self.cursor = None

    def version(self):
        config = self.config.get_config()
        self.__get_connection_cursor(**config)
        files = self.version_scanner.get_files()
        applied = self.__get_applied_versions()
        new_versions = self.version_scanner.sort_files(list(set(files) - set(applied)))
        self.__apply_versions(new_versions)
        self.__seed_data()
        self.config.upload_config()
        self.__reset_password()

    def __get_connection_cursor(self, **config):
        connector = SQLConnector(**config)
        connector.connect()
        self.cursor = connector.cursor()

    def __get_applied_versions(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS __versions (version_file character varying(255) PRIMARY KEY)')
        self.cursor.execute('SELECT * FROM __versions')
        versions = []
        for version in self.cursor.fetchall():
            versions.append(version['version_file'])
        return versions

    def __apply_versions(self, new_versions, seed=False):
        outputs = self.__get_outputs(seed)
        for version in new_versions:
            print(f"{outputs['intent']} {version}")
            try:
                self.cursor.execute(open(version, 'r').read())
                self.__remember_version(version, seed)
            except Exception as error:
                print(f'ERROR WITH {version}', error)
        print(f"{outputs['happened']} {len(new_versions)} {outputs['item']}")

    def __get_outputs(self, seed):
        return {
            'intent': 'APPLYING' if not seed else 'SEEDING',
            'happened': 'APPLIED' if not seed else 'SEEDED',
            'item': 'NEW VERSION(S)' if not seed else 'DATA FILE(S)'
        }

    def __remember_version(self, version, seed=False):
        if not seed:
            query = 'INSERT INTO __versions(%(columns)s) VALUES %(values)s'
            params = {
                'table': AsIs('__versions'),
                'columns': AsIs(', '.join(['version_file'])),
                'values': tuple([version])
            }
            self.cursor.execute(query, params)

    def __seed_data(self):
        if self.config.seed:
            files = self.seed_scanner.get_files()
            self.__apply_versions(files, True)

    def __reset_password(self):
        if self.config.reset_root and not self.config.param_found and self.config.ssm_param:
            print(f'PRINTING PASSWORD (just in case) {self.config.random_password}')
            query = "ALTER ROLE %(user_name)s WITH PASSWORD '%(new_password)s'"
            params = {
                'user_name': AsIs(self.config.user),
                'new_password': AsIs(self.config.random_password),
            }
            self.cursor.execute(query, params)
