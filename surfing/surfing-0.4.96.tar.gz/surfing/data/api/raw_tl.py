
import datetime
from typing import List, Tuple, Union, Optional
import pandas as pd
from sqlalchemy.sql import func
from sqlalchemy import or_
from ...util.singleton import Singleton
from ..wrapper.mysql import TLDatabaseConnector
from ..view.TL_models import *

class RawTLDataApi(metaclass=Singleton):
    def get_md_institution(self, party_ids = None):
        with TLDatabaseConnector().managed_session() as db_session:
            try:
                if (party_ids == None):
                    
                    query = db_session.query(
                        MdInstitution
                    )
                else:
                    query = db_session.query(
                        MdInstitution
                    ).filter(
                        MdInstitution.PARTY_ID.in_(party_ids)                  
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {MdInstitution.__tablename__}')
                return None
            
    def get_md_security(self, security_ids = None):
        with TLDatabaseConnector().managed_session() as db_session:
            try:
                if (security_ids == None):
                    
                    query = db_session.query(
                        MdSecurity
                    )
                else:
                    query = db_session.query(
                        MdSecurity
                    ).filter(
                        MdSecurity.SECURITY_ID.in_(security_ids)                  
                    )
                    
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {MdSecurity.__tablename__}')
                return None
            
    def get_pfund(self, pfund_ids = None):
        with TLDatabaseConnector().managed_session() as db_session:
            try:
                if (pfund_ids == None):
                    query = db_session.query(
                        Pfund
                    )
                else:
                    query = db_session.query(
                        Pfund
                    ).filter(
                        Pfund.ID.in_(pfund_ids)                  
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {Pfund.__tablename__}')
                return None

    def get_pfund_inst_info(self, pfund_ids = None):
        with TLDatabaseConnector().managed_session() as db_session:
            try:
                if (pfund_ids == None):
                    query = db_session.query(
                        PfundInstInfo
                    )
                else:
                    query = db_session.query(
                        PfundInstInfo
                    ).filter(
                        PfundInstInfo.ID.in_(pfund_ids)                  
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {PfundInstInfo.__tablename__}')
                return None

    def get_SYS_CODE(self,id=None):
        with TLDatabaseConnector().managed_session() as db_session:
            try:
                if id == None:
                    query = db_session.query(
                        SysCode
                    )
                else:
                    query = db_session.query(
                        SysCode
                    ).filter(
                        SysCode.ID.in_(id)
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {SysCode.__tablename__}')   

    def get_PFUND_NAV(self, start_time, end_time):
        with TLDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    PfundNav
                ).filter(
                    PfundNav.END_DATE <= end_time,
                    PfundNav.END_DATE >= start_time
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {PfundNav.__tablename__}')

    def get_PFUND_INST_SCALE_AMAC(self, id=None):
        with TLDatabaseConnector().managed_session() as db_session:
            try:
                if id == None:
                    query = db_session.query(
                        PfundInstScaleAmac
                        )
                else:
                    query = db_session.query(
                        PfundInstScaleAmac
                    ).filter(
                        PfundInstScaleAmac.ID.in_(id)
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {PfundInstScaleAmac.__tablename__}')

    def get_PFUND_MANAGER_INFO(self, id=None):
        with TLDatabaseConnector().managed_session() as db_session:
            try:
                if id == None:
                    query = db_session.query(
                        PfundManagerInfo
                    )
                else:
                    query = db_session.query(
                        PfundManagerInfo
                    ).filter(
                        PfundManagerInfo.ID.in_(id)
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {PfundManagerInfo.__tablename__}')
    