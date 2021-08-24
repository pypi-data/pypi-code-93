import sqlalchemy
# IN BUILT package
import pandas as pd
import time 
from datetime import datetime
# USER DEFINED package
current_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

# __CONNECTIONS
conn1 = "postgresql://imrul:1mRul%!$@#@192.168.168.50:5432/postgres" 
conn2 = "mysql://imrul:I@H^ft*&h2021@10.9.0.40:3306/"                       

# __DB ENGINES
db_engine = {
    '192.168.168.50'    : sqlalchemy.create_engine(conn1),  # OLAP  -   POSTGRESQL  -   SURECASH [:50]
    '10.9.0.40'         : sqlalchemy.create_engine(conn2),  # OLTP  -   MYSQL       -   NOBOPAY  [:40]
}

def load_data():
    # WRITE THE QUERY HERE ....
    query = f'''
                select * from training.ih_test_218576 limit 100;
            '''   
    # LOAD INTO PANDAS DATA FRAME    
    df = pd.read_sql(query, db_engine['192.168.168.50']) 
    # WRITE IN EXCEL
    df.to_excel("output/output  "+current_time+".xlsx",sheet_name='output',index=False)  

if __name__ == "__main__":
    load_data()
    
'''
    _____________________________
    Load DB Table Data to Excel
    _____________________________
    Developed By    :   Md. Imrul Hasan 
'''


