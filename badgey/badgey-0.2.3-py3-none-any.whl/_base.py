import abc
import inspect
import os
import xml.etree.cElementTree as ET

from collections import namedtuple
from typing import Dict

from git import Repo
from pybadges import badge

RegisterEntry = namedtuple("RegisterEntry", ["cls", "doc", "args"])

badges: Dict[str, namedtuple] = {}


class Badge(metaclass=abc.ABCMeta):
    def __init__(self):
        self.cwd = os.getcwd()

    def __init_subclass__(cls, **kwargs):
        if not (inspect.isabstract(cls)):
            args = inspect.getargspec(cls.__init__).args

            args = [arg for arg in args if not (arg == "self")]

            badges[cls.__name__] = RegisterEntry(
                cls=cls, doc=inspect.cleandoc(cls.__doc__), args=args
            )

    @property  # type: ignore
    @abc.abstractclassmethod
    def name(cls):
        raise NotImplementedError

    @abc.abstractproperty
    def right_text(self):
        raise NotImplementedError

    @property
    def left_text(self):
        return self.name

    @property
    def right_color(self):
        return "#1c7293"

    @property
    def badge(self):
        return badge(
            left_text=self.left_text,
            right_text=self.right_text,
            right_color=self.right_color,
        )

    def write(self):
        """This generates the badge and writes it to an svg file named as
        :attr:`name`
        """
        filename = os.path.join(self.cwd, f"{self.name}.svg")
        with open(filename, "w") as f:
            f.write(self.badge)


class FileParserBadge(Badge):
    """A Badge created parsing a file"""

    def __init__(self, filepath):
        super().__init__()

        self.filepath = filepath

    @abc.abstractproperty
    def content(self):
        """This method is used to retrieve the needed content from the file
        and store it in :attr:`left_text` and :attr:`right_text`
        """
        raise NotImplementedError


class XMLFileBadge(FileParserBadge):
    """A Badge created parsing an XML file"""

    def __init__(self, filepath):
        super().__init__(filepath)

    @property
    def content(self):
        return ET.parse(self.filepath)


class GitBadge(Badge):
    """A Badge created inspecting a given Git repo"""

    def __init__(self, repo_path):
        self.repo = Repo(repo_path)

        super().__init__()


class LogoBadge(Badge):
    """A Badge that uses an logo icon"""

    def __init__(self, image_path):
        self.logo = image_path

        super().__init__()

    @property
    def badge(self):
        return badge(
            left_text=self.left_text,
            right_text=self.right_text,
            right_color=self.right_color,
            logo=self.logo,
            embed_logo=True,
        )
