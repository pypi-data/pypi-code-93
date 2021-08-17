"""A decentralized social network."""

from understory import indieweb, web
from understory.web import tx

app = indieweb.site("Canopy")
templates = web.templates(__name__)


def template(handler, app):
    """Wrap the response in the final template."""
    yield
    if (
        tx.response.headers.content_type == "text/html"
        and not tx.response.naked
        and tx.host.owner
    ):
        tx.response.body = templates.template(tx.host.owner, tx.response.body)


app.wrappers.insert(2, template)


@app.route(r"settings")
class Settings:
    """."""

    def get(self):
        return templates.settings()

    def post(self):
        form = web.form("theme")
        print(form.theme)
        raise web.SeeOther("/settings")


# @app.route(r"")
# class Home:
#     """."""
#
#     def get(self):
#         """."""
#         return tmpl.home()


# TODO XXX tmpl.about()


# @app.route(r"now")
# class Now:
#     """."""
#
#     def get(self):
#         try:
#             now = tx.pub.read("now")["resource"]
#         except IndexError:
#             tx.pub.create(
#                 "now", mood={"start": [0, 0, 0], "end": [0, 0, 0]}, browsing=[]
#             )
#             now = tx.pub.read("now")["resource"]
#         return tmpl.now(now)
#
#
# @app.route(r"now/peers")
# class NowPeers:
#     """Firehose of peers' /now braids."""
#
#     def subscribe(self):
#         return web.multi_subscribe("alice.com/now", "bob.com/now")
#         # for patch in web.multi_subscribe(*peers):
#         #     yield bytes(f"proxying: {patch.decode()}", "utf-8")


# @app.route(r"{year}")
# class ArchiveYear:
#     """Resources from given year."""
#
#     def get(self):
#         return tmpl.archive.year(self.year, tx.pub.get_year(self.year))
#
#
# @app.route(r"{year}/{month}")
# class ArchiveMonth:
#     """Resources from given month."""
#
#     def get(self):
#         return tmpl.archive.month()
#
#
# @app.route(r"{year}/{month}/{day}")
# class ArchiveDay:
#     """Resources from given day."""
#
#     def get(self):
#         return tmpl.archive.day()
#
#
# @app.route(r"tracks")
# class Tracks:
#     """GPS coords."""
#
#     def post(self):
#         import json
#         import pprint
#
#         pprint.pprint(json.loads(web.form()))


# @app.route(r"{year}/{month}/{day}/{seconds}(/{slug})?")
# class Entry:
#     """An individual entry."""
#
#     def get(self):
#         resource = tx.pub.read(tx.request.uri.path)["resource"]
#         if resource["visibility"] == "private" and not tx.user.session:
#             raise web.Unauthorized(f"/auth?return_to={tx.request.uri.path}")
#         mentions = web.indie.webmention.get_mentions(str(tx.request.uri))
#         return tmpl.entry(resource, mentions)


# @app.route(r"icon-editor")
# class IconEditor:
#     """An icon editor."""
#
#     def get(self):
#         icons = {
#             "bookmark": (
#                 576,
#                 512,
#                 """
#             M 144,32
#             C 136,32 128,40 128,48
#             L 128,480
#             L 288,384
#             L 448,480
#             L 448,48
#             C 448,40 440,32 432,32
#             Z""",
#             )
#         }
#         return tmpl.icon_editor(icons)


# @app.route(r"initialize")
# class Initialize:
#     """."""
#
#     def post(self):
#         uid, passphrase = web.indieauth.init_owner(web.form("name").name)
#         return tmpl.welcome(passphrase)


# app.mount(indieweb.cache_app)
# TODO app.mount(web.debug_app)
# app.mount(indieweb.indieauth.client)
# app.mount(indieweb.indieauth.server)
# app.mount(indieweb.indieauth.root)
# app.mount(indieweb.indieauth.profile)  # NOTE defines the root, should be last
# app.mount(web.micropub.server)
# app.mount(web.microsub.server)
# app.mount(web.webmention.receiver)
# app.mount(web.websub.hub)
# app.mount(web.micropub.content)


# def contextualize(handler, app):
#     """Contextualize this thread based upon the host of the request."""
#     # host = tx.request.uri.host
#     # tx.app.name = host
#     # db = sql.db(f"{host}.db")
#     # db.define("sessions", **web.session_table_sql)
#     # web.add_job_tables(db)
#     # tx.host.db = db
#     # tx.host.cache = web.cache(db=db)
#     # tx.host.kv = kv.db(host, ":", {"jobs": "list"})
#     yield


# app.wrap(web.resume_session)
# app.wrap(indieweb.indieauth.wrap_server)
# app.wrap(indieweb.indieauth.wrap_client)
# app.wrap(web.braidify)


# app.wrap(web.micropub.wrap_server, "post")
# app.wrap(web.webmention.wrap, "post")
# app.wrap(web.microsub.wrap_server, "post")
# app.wrap(web.websub.wrap, "post")
# app.wrap(web.micropub.route_unrouted, "post")
