"""These are some methods that I was commonly putting in classes I wrote that interacted with databases"""
from abc import ABC
from datetime import date, datetime, timedelta
from typing import Union

from loguru import logger
from sqlalchemy.orm import Session  # type: ignore
from sqlalchemy.orm.decl_api import DeclarativeMeta  # type: ignore
from sqlalchemy.exc import IntegrityError  # type: ignore
from sqlalchemy.sql import text  # type: ignore
from sqlalchemy import column, inspect as sqlalchemyinspect  # type: ignore


class DatabaseBaseClass(ABC):
    """
    Base class that handles some common database tasks

    expects derivative classes to define self.engine - sqlalchemy engine
    """
    def get_dates_to_process(self, start_date: date, end_date: date, column: column,
                             force: bool = False) -> list:
        """

        :param start_date: First date (inclusive) to write to the database
        :param end_date: Last date (inclusive) to write to the database
        :param column: sqlalchemy date column to search for matching dates to skip
        :param force: Regenerate the data for the date range. By default, it skips dates with existing data.
        """
        def _convert_to_date(dte: Union[date, datetime]):
            if isinstance(dte, datetime):
                try:
                    return dte.date()
                except AttributeError:
                    pass
            if isinstance(dte, date):
                return dte
            raise AssertionError("Unknown type of date: {}".format(dte))
        with Session(bind=self.engine, future=True) as session:
            if not force:
                existing_dates = set(_convert_to_date(i[0]) for i in session.query(column).all())
            else:
                existing_dates = set()

            expected_dates = {start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)}
            dates_to_process = list(expected_dates - existing_dates)
            dates_to_process.sort(reverse=True)

            return dates_to_process

    def _insert_or_update(self, insert_obj: DeclarativeMeta, identity_insert=False) -> None:
        """
        A safe way for the sqlalchemy to insert if the record doesn't exist, or update if it does. Copied from
        trafficstat.crash_data_ingester
        :param insert_obj:
        :param identity_insert:
        :return:
        """
        session = Session(bind=self.engine, future=True)
        if identity_insert:
            session.execute(text('SET IDENTITY_INSERT {} ON'.format(insert_obj.__tablename__)))

        session.add(insert_obj)
        try:
            session.commit()
            logger.debug('Successfully inserted object: {}', insert_obj)
        except IntegrityError as insert_err:
            session.rollback()

            if '(544)' in insert_err.args[0]:
                # This is a workaround for an issue with sqlalchemy not properly setting IDENTITY_INSERT on for SQL
                # Server before we insert values in the primary key. The error is:
                # (pyodbc.IntegrityError) ('23000', "[23000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]
                # Cannot insert explicit value for identity column in table <table name> when IDENTITY_INSERT is set to
                # OFF. (544) (SQLExecDirectW)")
                self._insert_or_update(insert_obj, True)

            elif '(2627)' in insert_err.args[0] or 'UNIQUE constraint failed' in insert_err.args[0]:
                # Error 2627 is the Sql Server error for inserting when the primary key already exists. 'UNIQUE
                # constraint failed' is the same for Sqlite
                cls_type = type(insert_obj)

                qry = session.query(cls_type)

                primary_keys = [i.key for i in sqlalchemyinspect(cls_type).primary_key]
                for primary_key in primary_keys:
                    qry = qry.filter(cls_type.__dict__[primary_key] == insert_obj.__dict__[primary_key])

                update_vals = {k: v for k, v in insert_obj.__dict__.items()
                               if not k.startswith('_') and k not in primary_keys}
                if update_vals:
                    qry.update(update_vals)
                    try:
                        session.commit()
                        logger.debug('Successfully inserted object: {}', insert_obj)
                    except IntegrityError as update_err:
                        logger.error('Unable to insert object: {}\nError: {}', insert_obj, update_err)

            else:
                raise AssertionError('Expected error 2627 or "UNIQUE constraint failed". Got {}'.format(insert_err)) \
                    from insert_err
        finally:
            if identity_insert:
                session.execute(text('SET IDENTITY_INSERT {} OFF'.format(insert_obj.__tablename__)))
            session.close()
