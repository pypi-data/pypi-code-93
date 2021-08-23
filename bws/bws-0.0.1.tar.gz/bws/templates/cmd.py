template="""
from app import app, cmd
from bws.admin.bootstrap import bootstrap


bootstrap(app, None, ["cmd"])


if __name__== '__main__':
    cmd.run()

"""
