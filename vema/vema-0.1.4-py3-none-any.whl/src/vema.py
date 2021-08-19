from flask import Flask
from flask_frozen import Freezer

class Vema(Flask):
    def __init__(self, domain="https://vema.es"):
        super().__init__(__name__, template_folder="../../static");

        self.config["DOMAIN"] = domain;
        self.config["FREEZER_DESTINATION"] = "../../build";

        self.freezer = Freezer(self);

        import routers
        routers.load_routers(self);

    def compile(self):
        """
        Congela las páginas webs
        """
        self.freezer.freeze();
