from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError
import re
from .exceptions import InvalidURL, UnsupportedURL


class GitFiler:
    def __init__(self, url: str) -> None:
        self.allowed_domains = ["github.com", "gitlab.com"]
        self.base_url = url
        self.final_url = self.convert_url(self.base_url)
        try:
            with urlopen(self.final_url) as req:
                self.text = str(req.read(), encoding="utf-8")
        except HTTPError as e:
            error_code = e.code
            if error_code == 404:
                raise InvalidURL("Site/file does not exists")

    @property
    def url_domain(self) -> str:
        return re.sub(r"^https?://", "", self.base_url).split("/")[0]

    @property
    def is_domain_allowed(self) -> bool:
        return True if self.url_domain in self.allowed_domains else False

    def validate_url(self, url: str) -> str:
        result = urlparse(url)
        if (
            all([result.scheme, result.netloc])
            and re.search(r"^https?://", url) is not None
        ):
            if self.is_domain_allowed:
                return url
            else:
                raise UnsupportedURL(f"URL not in {self.allowed_domains}")
        else:
            raise InvalidURL("Specified string is not valid URL")

    def convert_url(self, url: str) -> str:
        url = self.validate_url(url)
        domain = self.url_domain
        if domain == "github.com":
            converted_str = url.replace(
                "github.com", "raw.githubusercontent.com"
            ).replace("/blob/", "/")
        elif domain == "gitlab.com":
            converted_str = url.replace("/blob/", "/raw/")
        return converted_str
