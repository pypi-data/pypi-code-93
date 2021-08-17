from anyblok.blok import Blok
from logging import getLogger
logger = getLogger(__name__)

try:
    import anyblok_postgres
except ImportError:
    anyblok_postgres = None


def import_declaration_module(reload=None):
    if anyblok_postgres is None:
        return

    from . import document
    if reload is not None:
        reload(document)


class AttachmentPostgresBlok(Blok):
    """Customer blok
    """
    version = "0.1.0"
    author = "Jean-Sébastien Suzanne"
    required = ['attachment']

    def update(self, latest):
        if anyblok_postgres is None:
            raise ImportError(
                "You can't install the blok 'attachment-postgres' without "
                "the package 'anyblok_postgres': pip install anyblok_postgres"
            )

    @classmethod
    def import_declaration_module(cls):
        import_declaration_module()

    @classmethod
    def reload_declaration_module(cls, reload):
        import_declaration_module(reload=reload)
