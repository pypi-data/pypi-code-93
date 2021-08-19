import psycopg2 as pg2

from .utils import logger, now

# Global variables
conn = None
cur = None


class PostDB:
    def __init__(self, user: str, password: str) -> None:
        global conn
        global cur

        # Establish first connection with default username and password
        try:
            conn = pg2.connect(user=user, password=password)
            conn.autocommit = True
            cur = conn.cursor()

        except Exception as e:
            logger.fatal(e, exc_info=True)
            raise Exception(
                'It seems like you have some problem with your database, please proceed reading the log for farther understading')

        finally:
            logger.info(
                'First connection to DB ended successfully status: Done!')

    @staticmethod
    def create_database(database: str) -> None:
        """:description: Creating a database if not exist"""

        try:
            # Looking if database 'parkinglot' is not exist
            cur.execute('SELECT datname FROM pg_database;')
            if database.lower() not in sum(cur.fetchall(), ()):
                cur.execute(
                    f"""
                    CREATE DATABASE {database}
                    WITH
                        ENCODING = 'UTF8'
                        CONNECTION LIMIT = 100
                        ALLOW_CONNECTIONS = true;
                    """)
                logger.info(
                    f'Database {database} was created successfully!')
            else:
                logger.info(f'Database {database} already exist')

        except Exception as e:
            logger.fatal(e, exc_info=True)
            raise Exception(
                'It seems like you have some problem with your database, please proceed reading the log for farther understading')

        finally:
            logger.info(f'create_database with value {database = } status: Done!')

    @staticmethod
    def create_table(table: str) -> None:
        """:description: Creating a table if not exist"""

        try:
            cur.execute(
                """
                SELECT tablename FROM pg_catalog.pg_tables
                WHERE schemaname = 'public';
                """)

            # Check if 'entrances' table is not exist in 'parkinglot' DB
            if table not in sum(cur.fetchall(), ()):
                cur.execute(
                    f"""
                    CREATE TABLE {table}(
                        id SERIAL PRIMARY KEY,
                        license_number VARCHAR(255) NOT NULL,
                        is_allowed VARCHAR(255) NOT NULL,
                        time TIMESTAMP NOT NULL
                    );
                    """
                )
                logger.info(f"Table {table} was created successfully!")
            else:
                logger.info(f"Table {table} already exist")

        except Exception as e:
            logger.fatal(e, exc_info=True)
            raise Exception(
                'It seems like you have some problem with your database, please proceed reading the log for farther understading')

        finally:
            logger.info(f'create_table with value {table = } status: Done!')

    @staticmethod
    def insert_data(liscense: str, status: str) -> None:
        """:description: Inserting values to DB"""

        try:
            # Insert relevant data to DB
            cur.execute(
                f"""
                INSERT INTO entrances(license_number, is_allowed, time)
                VALUES
                ('{liscense}', '{status}', to_timestamp('{now}', 'dd-mm-yyyy hh24:mi:ss'))
                """
            )

        except Exception as e:
            logger.fatal(e, exc_info=True)
            raise Exception(
                'It seems like you have some problem with your database, please proceed reading the log for farther understading')

        finally:
            logger.info(
                f'db_insert with value {license = } is done with {status = }')

    @staticmethod
    def switch_connection(user: str, password: str, database: str = None) -> None:
        global conn
        global cur

        # Establish first connection with default username and password
        try:
            conn = pg2.connect(user=user, password=password, database=database.lower())
            conn.autocommit = True
            cur = conn.cursor()

        except Exception as e:
            logger.fatal(e, exc_info=True)
            raise Exception(
                'It seems like you have some problem with your database, please proceed reading the log for farther understading')

        finally:
            logger.info(
                f'Switching connection to {user = }, {database.lower() = } ended')
