import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import text as sa_text
import pyodbc
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


def init_db_connect():
        try:
            SERVER = os.environ.get("SERVER_MONITORING")
            DATABASE = os.environ.get("DATABASE_MONITORING")
            DRIVER = os.environ.get("DRIVER_MONITORING")
            USERNAME = os.environ.get("USERNAME_MONITORING")
            PASSWORD = os.environ.get("PASSWORD_MONITORING")
            DATABASE_CONNECTION = f'mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}'

            engine = create_engine(DATABASE_CONNECTION)
            return engine
        except Exception as e:
            print(e)
            raise Exception('Erro inicializar conexao com banco de dados')
            
def write_to_database(table, dataframe):
        try:
            dataframe.to_sql(table, con=init_db_connect(), if_exists='append', index=False)
        except Exception as e:
            print('erro ao gravar %' % (e))
            raise Exception('Erro gravar no banco de dados')
            
def insert_to_monitoring(project_name='project_name', routing ='/lw', status = 'NA', total_amount=0, collected_quantity=0):
    try:
        df = pd.DataFrame(columns=['nm_projeto', 'nm_rota', 'status', 'qt_total', 'qt_coletada', 'dt_coleta'])
        df = df.append({'nm_projeto': str(project_name), 'nm_rota':str(routing), 'status':str(status), 'qt_total': int(total_amount), 'qt_coletada': int(collected_quantity), 'dt_coleta': datetime.now().strftime('%Y-%m-%d')},ignore_index=True)
        write_to_database('TB_ODS_INTEGRATIONS_MONITORING', df)
        print(df)
    except Exception as e:
        raise Exception('Erro ao inserir valores no frame')