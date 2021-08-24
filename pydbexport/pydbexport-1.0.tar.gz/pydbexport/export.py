import sqlalchemy
import pandas as pd
import time 
from datetime import datetime
current_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

def export_data(db,db_name,user,password,ip,port, schema, table):
   
    if db == 'postgresql':
        conn = f"{db}://{user}:{password}@{ip}:{port}/{db_name}" 
    elif db == 'mysql':
        conn = f"{db}://{user}:{password}@{ip}:{port}/"                       
         
    db_engine = sqlalchemy.create_engine(conn)  
    
    query = f'''
                select * from {schema}.{table} limit 100;
            ''' 
    df = pd.read_sql(query, db_engine)
    df.to_excel("output/output  "+current_time+".xlsx",sheet_name='output',index=False)  

    

# if __name__ == "__main__":
    
#     db = 'postgresql'
#     db_name = 'postgres'
#     user = 'imrul'
#     password = '1mRul%!$@#'
#     ip = '192.168.168.50'
#     port = 5432
#     schema = 'training'
#     table = 'ih_test_218576'
    
#     export_data(db,db_name,user,password,ip,port, schema, table)
    
    
    


