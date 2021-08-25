import magic
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class MimeTypeValidator:
    """
    mimetype are defined in /usr/share/file/magic.mgc
    """

    message = _(
        "File mimetype “%(mimetype)s” is not allowed. "
        "Allowed mimetypes are: %(allowed_mimetypes)s."
    )
    code = "invalid_mimetype"

    def __init__(self, allowed_mimetypes=None, message=None, code=None):
        if allowed_mimetypes is not None:
            allowed_mimetypes = [
                allowed_mimetypes.lower() for allowed_mimetypes in allowed_mimetypes
            ]
        self.allowed_mimetypes = allowed_mimetypes
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        mimetype = magic.from_buffer(value.read(4096), mime=True)
        value.seek(0)
        if (
            self.allowed_mimetypes is not None
            and mimetype not in self.allowed_mimetypes
        ):
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    "mimetype": mimetype,
                    "allowed_mimetypes": ", ".join(self.allowed_mimetypes),
                },
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.allowed_mimetypes == other.allowed_mimetypes
            and self.message == other.message
            and self.code == other.code
        )
