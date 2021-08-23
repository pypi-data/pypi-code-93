
from flask import Flask
# from bws_daemon import DaemonManager, bws_daemon_cli
from bws_daemon import DaemonManager

class Config:
    """App configuration."""

    USER = "Jose Angel Delgado Super Sayayin 1" 
    DAEMON_BIN = "app.py"


app = Flask(__name__)
app.config.from_object(Config())
dm = DaemonManager(app)
# dm.init_app(app)

