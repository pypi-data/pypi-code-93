"""Development of the understory."""

from understory import indieweb, kv, sql, web
from understory.web import tx


def set_data_sources(handler, app):
    """Set the request's data sources."""
    tx.host.db = sql.db("understory-stream.db")
    tx.host.cache = web.cache(db=tx.host.db)
    tx.host.kv = kv.db("understory-stream", ":", {"jobs": "list"})
    yield


app = web.application(
    "understory.stream",
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
    """Track the development of the understory."""

    def get(self):
        """Return the index."""
        return templates.index()
