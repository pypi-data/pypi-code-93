"""Navigate the various projects tangential to the understory."""

from understory import indieweb, kv, sql, web
from understory.web import tx


def set_data_sources(handler, app):
    """Set the request's data sources."""
    tx.host.db = sql.db("understory-cloud.db")
    tx.host.cache = web.cache(db=tx.host.db)
    tx.host.kv = kv.db("understory-cloud", ":", {"jobs": "list"})
    yield


app = web.application(
    "understory.cloud",
    static=__name__,
    mounts=(indieweb.indieauth.client.app,),
    wrappers=(
        set_data_sources,
        web.resume_session,
        indieweb.indieauth.client.wrap,
    ),
)
templates = web.templates(__name__)


@app.route(r"")
class Index:
    """Full catalog of software projects."""

    def get(self):
        """Return the index."""
        return templates.index()


@app.route(r"overstory")
class Overstory:
    """."""

    def get(self):
        """."""
        return templates.overstory()


@app.route(r"canopy")
class Canopy:
    """."""

    def get(self):
        """."""
        return templates.canopy()


@app.route(r"liana")
class Liana:
    """."""

    def get(self):
        """."""
        return templates.liana()


@app.route(r"epiphytes")
class Epiphytes:
    """."""

    def get(self):
        """."""
        return templates.epiphytes()


@app.route(r"understory")
class Understory:
    """."""

    def get(self):
        """."""
        return templates.understory()


@app.route(r"gaea")
class Gaea:
    """."""

    def get(self):
        """."""
        return templates.gaea()
