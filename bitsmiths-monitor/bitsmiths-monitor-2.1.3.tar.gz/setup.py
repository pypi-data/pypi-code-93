from setuptools import setup


def build_sql_files():
    import os

    ext_order = ['.table', '.constraint', '.index']

    for (root, dirs, files) in os.walk('../mettledb/sqldef'):
        if not files or dirs:
            continue

        sql_name  = os.path.split(root)[-1]
        dest_file = os.path.join(f'bs_monitor/sql/{sql_name}.sql')

        os.system(f'mettle-sql-build --clean {dest_file}')

        for ext in ext_order:
            for fl in files:
                if fl.endswith(ext):
                    os.system(f'mettle-sql-build --file {os.path.join(root, fl)} {dest_file}')

        init_file = os.path.join('..', 'sql', f'initdb.{sql_name}.sql')

        if os.path.exists(init_file):
            os.system(f'mettle-sql-build --file {init_file} {dest_file}')


build_sql_files()

setup()
