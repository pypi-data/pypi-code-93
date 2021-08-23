template = """
# generado automaticamente
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname).1s %(asctime).19s] %(message)s',
    datefmt='%y-%m-%d %H:%M:%S'
)

from app import app
from bws.admin import create_admin
from bws.admin.bootstrap import bootstrap


logger = logging.getLogger("Boot Admin")

admin = create_admin(app)
bootstrap(app, admin, ["config", "api"])



if __name__ == '__main__':    
    app.run(host=app.config["HOST"], debug=True)
"""