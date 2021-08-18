import psycopg2 as pg2

from utils import logger, now


def db_establish_connection(user: str = 'postgres', password: str = 'password', database=None) -> 'pg2.cursor':
    """:description: Establishing connection to PostgresDB"""

    try:
        conn = pg2.connect(user=user, password=password, database=database)
        conn.autocommit = True
        cur = conn.cursor()
    except Exception as e:
        logger.fatal(e, exc_info=True)
        raise Exception(
            "It seems like you have some problem with your database, please proceed reading the log for farther understading")
    finally:
        logger.info("db_establish_connection status: Done!")

    return cur


def db_create_database(cur: 'pg2.cursor') -> None:
    """:description: Creating 'parkinglot' database if not exist"""

    try:
        cur.execute("SELECT datname FROM pg_database;")
        if 'parkinglot' not in sum(cur.fetchall(), ()):
            cur.execute(
                """
                CREATE DATABASE parkinglot
                WITH
                    ENCODING = 'UTF8'
                    CONNECTION LIMIT = 100
                    ALLOW_CONNECTIONS = true;
                """)
            logger.info("Database 'parkinglot' was created successfully!")
        else:
            logger.info("Database 'parkinglot' already exist")

    except Exception as e:
        logger.fatal(e, exc_info=True)
        raise Exception(
            "It seems like you have some problem with your database, please proceed reading the log for farther understading")

    finally:
        logger.info('db_create_database status: Done!')
        cur.close()


def db_create_table(user: str = 'postgres', password: str = 'password', database=None) -> None:
    """:description: Creating 'entrances' table if not exist"""

    # Establish connection with relevant database
    cur = db_establish_connection(user, password, database)

    try:
        cur.execute(
            """
            SELECT tablename FROM pg_catalog.pg_tables
            WHERE schemaname = 'public';
            """)

        if 'entrances' not in sum(cur.fetchall(), ()):
            cur.execute(
                """
                CREATE TABLE entrances(
                    id SERIAL PRIMARY KEY,
                    license_number VARCHAR(255) NOT NULL,
                    is_allowed VARCHAR(255) NOT NULL,
                    time TIMESTAMP NOT NULL
                );
                """
            )
            logger.info("Table 'entrances' was created successfully!")
        else:
            logger.info("Table 'entrances' already exist")

    except Exception as e:
        logger.fatal(e, exc_info=True)
        raise Exception(
            "It seems like you have some problem with your database, please proceed reading the log for farther understading")

    finally:
        logger.info('db_create_table status: Done!')
        cur.close()


def db_insert(liscense: str, status: str) -> None:
    """:description: Inserting values to DB"""

    # Establish connection with relevant database
    cur = db_establish_connection(database='parkinglot')

    try:
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
            "It seems like you have some problem with your database, please proceed reading the log for farther understading")

    finally:
        logger.info("db_insert status: Done!")
        cur.close()


def main():
    pass


if __name__ == '__main__':
    main()
