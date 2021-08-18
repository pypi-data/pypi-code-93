
class OARepoDOIGenerator(object):
    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""

        self.init_config(app)

    def init_config(self, app):
        """
        Propagate default values to the configuration.
        :param app      the application
        """
        if 'DOI_DATACITE_PUBLISHER' not in app.config:
            app.config.setdefault("DOI_DATACITE_PUBLISHER", "CESNET")

