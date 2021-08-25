from typing import List, Dict
from coopio.IDataService import IDataService, T
import logging
import sqlalchemy as db
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
import pandas as pd
from mapper.object_mapper import ObjectMapper

def create_a_db_connection_string(server_name: str,
                                  db_name: str,
                                  trusted_connection: bool = True,
                                  driver: str = "ODBC+Driver+17+for+SQL+Server"):

    trusted_txt = 'yes' if trusted_connection else 'no'
    driver = driver.replace(" ", "+")

    return f'mssql+pyodbc://@{server_name}/{db_name}?trusted_connection={trusted_txt}&driver={driver}'

def get_sql_connection(servername: str, db_name: str, echo: bool = False):
    # Update connection to newly created db
    return db.create_engine(create_a_db_connection_string(servername, db_name)
                            , connect_args={'autocommit': True}
                            , echo=echo)

def get_session(servername: str, db_name: str):
    sqlcon = get_sql_connection(servername, db_name)

    return Session(sqlcon)

def check_for_db(servername: str, db_name: str):
    verify_db_sql = f"select * from sys.databases where name = '{db_name}'"

    # get a connection
    sqlcon = get_sql_connection(servername, "master")

    # verify the db exists
    with sqlcon.connect() as connection:
        results = connection.execute(verify_db_sql)
        rows = results.fetchall()

    if len(rows) == 1:
        return True
    return False

def check_connections_to_db(servername: str, db_name: str, kill: bool = False):

    # get connection to master
    sqlcon = get_sql_connection(servername, "master")

    with sqlcon.connect() as connection:
        sql = f"if object_id('tempdb..#TEMP') is not null drop table #TEMP;	"
        results = connection.execute(sql)
        sql =   f"\ncreate table #TEMP											"\
                f"\n(															"\
                f"\n	SPID int,												"\
                f"\n	Status nvarchar(max),									"\
                f"\n	Login nvarchar(max),									"\
                f"\n	HostName nvarchar(max),									"\
                f"\n	BlkBy nvarchar(max),									"\
                f"\n	DBName nvarchar(max),									"\
                f"\n	Command nvarchar(max),									"\
                f"\n	CPUTime int,											"\
                f"\n	DiskIO int,												"\
                f"\n	LastBatch nvarchar(max),								"\
                f"\n	ProgramName nvarchar(max),								"\
                f"\n	SPID2 int,												"\
                f"\n	REQUESTID int											"\
                f"\n);															"
        results = connection.execute(sql)
        sql =   f"\ninsert into #TEMP											"\
                f"\nexec sp_who2;												"
        results = connection.execute(sql)
        sql = f"\nselect * from #TEMP where DBName = '{db_name}';     		"
        results = connection.execute(sql)
        rows = results.fetchall()


        if kill:
            for spid in rows:
                connection.execute(f"kill {spid[0]}")

    return results

def delete_db(servername: str, db_name: str):
    # delete db string
    drop_db_sql = f"DROP DATABASE IF EXISTS {db_name};"

    # get a connection
    sqlcon = get_sql_connection(servername, "master")

    # check and kill open connections
    connections = check_connections_to_db(servername, db_name, kill=True)

    # drop db
    with sqlcon.connect() as connection:
        deb = connection.execute(drop_db_sql)

def create_db(servername: str, db_name: str, echo: bool = False):
    sqlcon = get_sql_connection(servername, "master", echo)

    create_db_sql = f"IF DB_ID('{db_name}') IS NULL" \
                     f"\nBEGIN" \
                     f"\nCREATE DATABASE {db_name};" \
                     f"\nEND\n\n"

    # run sql
    with sqlcon.connect() as connection:
        deb = connection.execute(create_db_sql)

def connect_to_db(servername: str, db_name: str, recreate_if_existing: bool, create_if_missing: bool=True, echo: bool = False):
    # check for db
    db_exists = check_for_db(servername, db_name)

    # recreate db per param
    if recreate_if_existing and db_exists:
        delete_db(servername, db_name)
        create_db(servername, db_name)

    # create db per param
    if create_if_missing and not db_exists:
        create_db(servername, db_name)

    # Update connection to newly created db
    return get_sql_connection(servername, db_name, echo)

class SqlDataService(IDataService):

    def __init__(self,
                 servername: str,
                 db_name: str,
                 base: db.orm.decl_api.DeclarativeMeta,
                 orm_obj_mapping_factory: ObjectMapper = None,
                 recreate_db_if_existing:bool=False,
                 create_if_missing: bool = True,
                 echo: bool = False):

        self.servername = servername
        self.db_name = db_name
        self.base = base
        self.orm_obj_mapping_factory = orm_obj_mapping_factory
        super().__init__()

        # connect to db
        sqlcon = connect_to_db(servername, db_name, recreate_if_existing=recreate_db_if_existing, create_if_missing=create_if_missing, echo=echo)

        # Create defined tables
        with sqlcon.connect() as connection:
            self.base.metadata.create_all(bind=connection)
            connection.close()
        sqlcon.dispose()


    @staticmethod
    def _commit(engine, session):
        try:
            try:
                session.commit()
                return True
            except db.exc.SQLAlchemyError as e:
                logging.error(e)
                session.rollback()
                return False
        except:
            engine.dispose()
            return False

    def _input_type_to_mapping(self, obj_type: T):
        # no mapper, assume working on raw ORM objects
        if self.orm_obj_mapping_factory is None:
            return obj_type

        # object not mapped, will attempt to return the object entered
        mapping = self.orm_obj_mapping_factory.mappings.get(obj_type, None)
        if mapping is None:
            return obj_type

        # has a mapping, return the mapped item type (choose first mapping in dict)
        return list(mapping.keys())[0]

    def _try_bulk_save_fail_to_individual_with_rollback(self, session, objs):
        try:
            session.add_all(objs)
        except Exception as e:
            issues = []
            for obj in objs:
                try:
                    session.add(obj)
                except Exception as iner:
                    issues.append((obj, iner))

            issues_iter = iter([f"{x[0]} -- {x[1]}" for x in issues])
            issues_txt = ("\n").join(issues_iter)

            session.rollback()
            raise Exception(f"Unable to bulk load the objects. Exception {e} was raised when bulk inserting. The issues were on"
                            f"{issues_txt}")

    def add_or_update(self, obj_type: T, objs: List[T], **kwargs) -> List[T]:

        entries_to_update = []
        entries_to_put = []


        orm_type = self._input_type_to_mapping(obj_type)
        sqlcon = get_sql_connection(self.servername, self.db_name)
        with Session(sqlcon) as session:

            # Find all objects that needs to be updated
            primary_key = inspect(orm_type).primary_key[0].name # https://stackoverflow.com/questions/6745189/how-do-i-get-the-name-of-an-sqlalchemy-objects-primary-key

            primary_identifiers = [getattr(obj, primary_key) for obj in objs]

            for each in self._try_retrieve_objs_of_type(session, orm_type, primary_key, primary_identifiers):
                # obj = objs.pop(getattr(each, primary_key))
                index = next(idx for idx in range(len(objs)) if getattr(objs[idx], primary_key) == getattr(each, primary_key))
                obj = objs.pop(index)
                entries_to_update.append(obj)

            # Bulk mappings for everything that needs to be inserted
            for obj in objs:
                entries_to_put.append(obj)

            # bulk save
            if self.orm_obj_mapping_factory is not None:
                puts = [self.orm_obj_mapping_factory.map(x) for x in entries_to_put]
                self._try_bulk_save_fail_to_individual_with_rollback(session, puts)
            else:
                self._try_bulk_save_fail_to_individual_with_rollback(session, entries_to_put)

            # merge objects that were already in db
            if self.orm_obj_mapping_factory is not None:
                updts = [self.orm_obj_mapping_factory.map(x) for x in entries_to_update]
            else:
                updts = entries_to_update
            for obj in updts:
                session.merge(obj)

            # commit
            if not (self._commit(sqlcon, session)):
                if kwargs.get('allow_partial', True) and len(objs) > 1:
                    for obj in objs:
                        self.add_or_update(obj_type, [obj], allow_partial=False)
                else:
                    obj_txt = self._lots_of_objects_to_string(objs)
                    raise Exception(f"Unable to commit the add_or_update operation for objects {obj_type}"
                                    f"\n{obj_txt}")

            # return
            return self.retrieve_objs(obj_type, [getattr(obj, primary_key) for obj in objs])

    @staticmethod
    def _lots_of_objects_to_string(objs, n_objs_to_show_start = 10, n_objs_to_show_end = 10):

        if len(objs) <= n_objs_to_show_start + n_objs_to_show_end:
            obj_txt = "\n".join(iter([str(x) for x in objs]))
        else:
            obj_txt = "\n".join(iter([str(x) for x in objs[:n_objs_to_show_start]]))
            obj_txt += f"\n...{len(objs) - n_objs_to_show_start - n_objs_to_show_end} objects omitted...\n"
            obj_txt += "\n".join(iter([str(x) for x in objs[-n_objs_to_show_end:]]))

        return obj_txt

    @staticmethod
    def _try_retrieve_objs_of_type(session, orm_type: T, key: str, ids: List[str] = None):
        def batch_them(iterable, n=1):
            l = len(iterable)
            for ndx in range(0, l, n):
                yield iterable[ndx:min(ndx + n, l)]

        try:
            if ids is not None:
                orm_results = []
                # must batch since there is a max length of 1000 on the .in_ function

                for batch in batch_them(ids, 1000):
                    batch_results = session.query(orm_type).filter(getattr(orm_type, key).in_(batch)).all()
                    orm_results += batch_results
            else:
                orm_results = session.query(orm_type).all()

            return orm_results
        except Exception as e:
            raise Exception(f"Error querying {orm_type}"
                            f"\nINNER: {type(e)}"
                            f"\n{e}")


    def retrieve_objs(self, obj_type: T, ids: List[str] = None, ret_as_orm: bool = False) -> List[T]:

        orm_type = self._input_type_to_mapping(obj_type)

        sqlcon = get_sql_connection(self.servername, self.db_name)
        with Session(sqlcon) as session:
            primary_key = inspect(orm_type).primary_key[0].name # https://stackoverflow.com/questions/6745189/how-do-i-get-the-name-of-an-sqlalchemy-objects-primary-key

            #query
            orm_results = self._try_retrieve_objs_of_type(session, orm_type, primary_key, ids)

            # map and return
            if self.orm_obj_mapping_factory is not None and not ret_as_orm:
                return [self.orm_obj_mapping_factory.map(x) for x in orm_results]
            else:
                return orm_results

    def delete(self, obj_type: T, ids: List[str] = None) -> Dict[str, bool]:
        sqlcon = get_sql_connection(self.servername, self.db_name)
        with Session(sqlcon) as session:
            objs = self.retrieve_objs(obj_type, ids, ret_as_orm=True)

            [session.delete(obj) for obj in objs]

            for obj in objs:
                session.delete(obj)

            # commit
            if not (self._commit(sqlcon, session)):
                raise Exception(f"Unable to commit the delete operation for objects {obj_type}")

            return {id: True for id in ids}

    def delete_db(self):
        delete_db(self.servername, self.db_name)

    def retrieve_as_df(self, ids: List[str] = None) -> pd.DataFrame:
        objs = self.retrieve_objs(ids)
        df = pd.DataFrame(objs)
        return df

    def translate_from_data_rows(self, obj_type: T, df: pd.DataFrame) -> List[T]:
        raise NotImplementedError()
