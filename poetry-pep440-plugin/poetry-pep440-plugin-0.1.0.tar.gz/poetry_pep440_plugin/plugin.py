from typing import TYPE_CHECKING

from poetry.plugins import ApplicationPlugin

if TYPE_CHECKING:
    from poetry.console.application import Application
    from poetry.core.version.pep440.version import PEP440Version


class Pep440Plugin(ApplicationPlugin):
    def activate(self, application: "Application") -> None:
        # The original parse method is a decorated classmethod attribute. We
        # need to unwrap it to get the underlying function, and then wrap it
        # in a classmethod again before assigning the monkey patched method.
        original_method = PEP440Version.parse.__func__

        def parse(cls, value: str) -> "PEP440Version":
            # Workaround for https://github.com/python-poetry/poetry/issues/4176.
            value = value.rstrip(".")
            return original_method(cls, value)

        PEP440Version.parse = classmethod(parse)
