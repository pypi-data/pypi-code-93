from mysql import MySQLConnection

db_conf = {"host": "5slive.com", "user": "test", "pwd": "Hammer123_test_AM_#", "db_name": "admin"}

with MySQLConnection(**db_conf) as db:
    rs = db.select_dict_list(sql="select * from ct_task")
    print(rs)


