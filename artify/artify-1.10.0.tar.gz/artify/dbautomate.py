import __main__

def create_service():
    pass

def create_database(py):
    """
    sqlcmd --app test

    sqlcmd -S <Computer Name>\<Instance>

    sqlcmd -S IDN-20B\SQLEXPRESS -q "CREATE DATABASE TEST_AUTOMATE";

    sqlcmd -S IDN-20B\SQLEXPRESS -q "USE IdentityServerNew ; SELECT * FROM AspNetUsers";

    python -m artify -c database -h IDN-20B -i SQLEXPRESS -t MSSQL -n TEST_DB
    python -m artify --command database --host IDN-20B --instance SQLEXPRESS --type MSSQL --name TEST_DB

    Confirm settings:
     - db_name: testdb
     - storage: 100
     - db_instance_class: db.t2.medium
     - db_instance_id: testdb20210709
    """
    db_cmd = "sqlcmd "
    pass