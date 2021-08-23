template="""
from app import app, migrate
from bws.admin.bootstrap import bootstrap


bootstrap(app, None, ["migrations"])


if __name__== '__main__':
    migrate.run()

"""
