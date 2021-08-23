#!/usr/bin/env python

"""
usage: db_loader.py [-h] [-d XML_DATA_FILE] [-v] command db_name

synopsis:
  Tests for SQLAlchemy.

positional arguments:
  command               A command. One of: create, add, show.
  db_name               The database file name, e.g. 'test01.db'.

optional arguments:
  -h, --help            show this help message and exit
  -d XML_DATA_FILE, --xml-data-file XML_DATA_FILE
                        For command 'add', the XML data file name, e.g.
                        'mydata.xml'.
  -v, --verbose         Print messages during actions.

commands:
  create -- create the tables.
  add -- parse XML and add data to database.
  show -- (not implemented).
  delete-all -- (possibly implemented).
examples:
  python db_loader.py create test01.db
  python db_loader.py add test01.db
"""

from __future__ import print_function
import sys
import argparse
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#
# Update this to the SQLAlchemy models file to be used to create the models.
import models_sqa as mdl
#
# Update this to the gDS module to be used in export/load.
import tmp02sup as gdsmodule


#
# Global variables


#
# Private functions

def dbg_msg(options, msg):
    """Print a message if verbose is on."""
    if options.verbose:
        print(msg)


def create_sqlite_engine(file_name):
    """Create and return an sqlalchemy engine and session."""
    url = 'sqlite:///{}'.format(file_name)
    engine = create_engine(url)
    Session = sessionmaker(bind=engine)
    session = Session()
    return engine, session


def create_db_tables(options):
    """Create the SQLAlchemy database and the tables in it."""
    db_name = options.db_name
    engine, session = create_sqlite_engine(db_name)
    mdl.Base.metadata.create_all(engine)


def add_db_data(options):
    """Parse an XML instance document and add the data to the database."""
    db_name = options.db_name
    engine, session = create_sqlite_engine(db_name)
    if not options.xml_data_file:
        sys.exit('For command "add", must use option "--xml-data-file".')
    root = gdsmodule.parse(options.xml_data_file, silence=True)
    root.exportSQLAlchemy(session)
    session.commit()


def show_db(options):
    db_name = options.db_name
    engine, session = create_sqlite_engine(db_name)
    pass


def delete_all_db(options):
    db_name = options.db_name
    engine, session = create_sqlite_engine(db_name)
    change = False
    for classname in mdl.__all__:
        cls = getattr(mdl, classname, None)
        if cls is not None:
            for dbobj in session.query(cls):
                session.delete(dbobj)
                change = True
    if change:
        session.commit()


def export_json(options):
    db_name = options.db_name
    engine, session = create_sqlite_engine(db_name)
    database = {}
    users = []
    for user in session.query(mdl.User):
        user_data = {
            'name': user.name,
            'fullname': user.fullname,
            'password': user.password,
        }
        users.append(user_data)
    database['users'] = users
    addresses = []
    for address in session.query(mdl.Address):
        address_data = {
            'email_address': address.email_address,
            'user': address.user.id,
        }
        addresses.append(address_data)
    database['addresses'] = addresses
    json.dump(database, sys.stdout)
    print()


def main():
    description = """\
synopsis:
  Tests for SQLAlchemy.
"""
    epilog = """\
commands:
  create -- create the tables.
  add -- parse XML and add data to database.
  show -- (not implemented).
  delete-all -- (possibly implemented).
examples:
  python test02.py create test01.db
  python test02.py add test01.db
  python test02.py show test01.db
"""
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "command",
        help="A command.  One of: create, add, show."
    )
    parser.add_argument(
        "db_name",
        help="The database file name, e.g. 'test01.db'."
    )
    parser.add_argument(
        "-d", "--xml-data-file",
        help="For command 'add', the XML data file name, e.g. 'mydata.xml'."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print messages during actions.",
    )
    options = parser.parse_args()
    if options.command == 'create':
        create_db_tables(options)
    elif options.command == 'add':
        add_db_data(options)
    elif options.command == 'show':
        show_db(options)
    elif options.command == 'delete-all':
        delete_all_db(options)
    elif options.command == 'export-json':
        export_json(options)
    else:
        parser.error(parser.format_help())


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    #import ipdb; ipdb.set_trace()
    main()
