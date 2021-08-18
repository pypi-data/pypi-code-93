from __future__ import annotations
from abc import ABC
from fileinput import FileInput

import logging
import re
from bs4 import BeautifulSoup
from subprocess import check_output
from dataclasses import dataclass, field
from pathlib import Path
from markdown import Markdown as Md
from typing import Optional, Iterator, Tuple


@dataclass
class Repository:
  path: Path
  glob: str
  include_path: str
  stem: bool
  deploy_branch: str
  user: str

  @property
  def url(self) -> str:
    return f"https://github.com/{self.user}/{self.path.name}/blob"

  def include_file(self, test: bool):
    for markdown in File.files(self):
      line2txt = {}
      logging.info("Markdown: %s", markdown.path)
      for include in Include.includes(markdown):
        logging.info("Include: %s", include.name)
        line2txt[include.line_num] = include.to_markdown()
      with FileInput(markdown.path, inplace=not test) as file:
        for i, line in enumerate(file, 1):
          if i in line2txt:
            print(line2txt[i], end="")
          else:
            print(line, end="")


@dataclass
class Gitbook(Repository):
  url_path: str
  summary: Optional[Markdown] = None
  toc: Optional[File] = None

  def __post_init__(self):
    logging.debug("__post_init__(%s)", self)
    if self.url_path == "":
      self.url_path = f"https://{self.user}.gitbook.io/{self.path.name}"

  def table_of_contents(self) -> str:
    logging.debug("generate_table_of_contents(%s)", self)
    assert self.summary and self.toc

    lines = ["# Table of Contents"]
    for markdown, nest in self.summary.extract_summary():
      logging.info("sumamry from markdown: %s", markdown)
      if markdown.path == self.toc.path:
        continue
      lines += [f"\n{'#' * (nest + 1)} {markdown.path.relative_to(self.path).name}\n"]
      lines += [markdown.table_of_contents(self.url_path)]

    return "\n".join(lines) + "\n"


@dataclass
class File:
  repo: Repository
  path: Path
  content: str = field(repr=False, default="")

  def __post_init__(self):
    logging.debug("__post_init__(%s)", self)
    if self.content == "":
      try:
        self.content = self.path.read_text()
      except UnicodeDecodeError:
        self.content = ""

  @property
  def include_path(self) -> Path:
    logging.debug("include_path(%s)", self)
    if self.repo.stem:
      include_path = self.path.parent / self.path.stem
    else:
      include_path = self.repo.path / self.repo.include_path
    if not include_path.is_dir():
      include_path.mkdir()
    return include_path

  @classmethod
  def files(cls, repo: Repository) -> list[File]:
    logging.debug("files(%s)", repo)
    if isinstance(repo, Gitbook):
      assert repo.summary
      return [Markdown(repo, repo.path / path) for path in re.findall(Markdown.RE, repo.summary.content)]
    else:
      return [File(repo, file) for file in repo.path.glob(repo.glob) if file.is_file() and file.suffix != '.png']


class Markdown(File):
  RE = r"\((.*\.md)\)"  # * [Module](cpp/module.md) -> cpp/module.md

  @staticmethod
  def normalize(st):
    return st.lower().replace(' ', '-')

  def extract_summary(self) -> Iterator[Tuple[Markdown, int]]:
    logging.debug("extract_summary(%s)", self)
    assert self.path.name == "SUMMARY.md"
    indent = "  " if "\n  *" in self.content else "    "
    for line in self.content.split("\n"):
      for path in re.findall(Markdown.RE, line):
        yield (Markdown(self.repo, self.repo.path / path), line.count(indent) + 1)

  def extract_heading(self) -> list[tuple[int, str]]:
    logging.debug("extract_markdown()")
    text = Md(extensions=['fenced_code']).convert(self.content)
    md = BeautifulSoup(text, "html.parser")
    return [(int(str(line)[2]), str(line)[4:-5]) for line in md.find_all(re.compile('^h[1-6]$'))]

  def table_of_contents(self, url_path) -> str:
    logging.debug("table_of_contents(%s, %s)", self, url_path)
    lines = []
    for level, name in self.extract_heading():
      path = str(self.path.relative_to(self.repo.path)).replace(".md", "")
      lines += [f"{'  ' * (level - 1)}* [{name}]({url_path}/{path}#{Markdown.normalize(name)})"]
    return "\n".join(lines)


@dataclass
class IInclude(ABC):
  file: File
  name: str
  line_num: int
  txt: str

  @staticmethod
  def RE() -> str:
    pass

  @property
  def path(self) -> Path:
    logging.debug("path(%s)", self)
    return self.file.include_path / self.name

  def update_link(self, text: str) -> str:
    logging.debug("update_link(%s)", text)
    prefix = self.file.include_path.relative_to(self.file.repo.path)
    text = re.sub(r"[!](\[.*\])\((?!http)(.*)\)", rf'\1({prefix}/\2)', text.strip())
    return "".join(ch for i, ch in enumerate(text) if i <= 1 or not (text[i - 1] == text[i - 2] == ch == "\n")) + "\n"


@dataclass
class Include(IInclude):
  OVERWRITE = "include"

  @classmethod
  def includes(cls, file: File) -> list[IInclude]:
    logging.debug("includes(%s)", file)
    includes = []
    for line_num, txt in enumerate(file.path.read_text().split("\n"), 1):
      for cls_ in IInclude.__subclasses__():
        match = re.match(cls_.RE(), txt)
        if not match:
          continue
        name = match.group(1)
        include = cls_(file, name, line_num, txt)
        if "|" in name and isinstance(cls_, Repo):
          name, glob = name.split("|", 1)
          name, glob = name.strip(" '\""), glob.strip(" '\"")
          include.glob = glob
        includes.append(include)
    return includes

  @staticmethod
  def RE() -> str:
    return fr'{{% {Include.OVERWRITE} [\'"](.*)[\'"] %}}'

  def to_markdown(self):
    logging.debug("to_markdown(%s)", self)
    assert self.path.is_file(), f"{self.path} is not a file"
    return self.update_link(self.path.read_text())


@dataclass
class Repo(IInclude):
  OVERWRITE = "repo"
  glob: str = "**/*"

  @staticmethod
  def RE() -> str:
    return fr'{{% {Repo.OVERWRITE} [\'"](.*)[\'"] %}}'

  def to_markdown(self):
    logging.debug("to_markdown(%s)", self)
    if self.path.is_file():
      lines = ["{% tabs %}"]
      lines += [f"{{% tab title=\'{self.path.name}\' %}}\n"]
      lines += [self.path.read_text()]
      lines += ["{% endtab %}"]
      lines += ["{% endtabs %}\n"]
      return self.update_link("\n".join(lines))
    lines = []
    ignored = [".gitignore", "images"] + check_output("git ls-files --other", text=True, shell=True).splitlines()
    for file_glob in self.glob.split("|"):
      lines += ["{% tabs %}"]
      for file in self.path.glob(file_glob):
        if not file.is_file() or file.name in ignored or file.parent.name in ignored:
          continue
        lines += [f"{{% tab title=\'{file.relative_to(self.path)}\' %}}\n"]
        suffix = file.suffix[1:]
        lines += [f"````{suffix if suffix else 'txt'}"]
        try:
          lines += [file.read_text()]
        except UnicodeDecodeError:
          raise Exception("Please do not include binary files")
        lines += ["````\n"]
        lines += ["{% endtab %}"]
      lines += ["{% endtabs %}\n"]
    return self.update_link("\n".join(lines))


@dataclass
class Link(IInclude):
  OVERWRITE = "link"

  @staticmethod
  def RE() -> str:
    return fr'{{% {Link.OVERWRITE} [\'"](.*)[\'"] %}}'

  def to_markdown(self):
    logging.debug("to_markdown(%s)", self.path)
    repo = self.file.repo
    return f"[{self.path.name}]({repo.url}/{repo.deploy_branch}/{self.path.relative_to(repo.path)})\n"


@dataclass
class Image(IInclude):
  OVERWRITE = "images"

  @property
  def path(self) -> Path:
    logging.debug("path(%s)", self)
    return self.file.include_path.parent / Image.OVERWRITE / self.name

  @staticmethod
  def RE() -> str:
    return rf".*!\[.*\]\(.*{Image.OVERWRITE}/(.*.png)\)"

  def to_markdown(self):
    logging.debug("to_markdown(%s)", self)
    return self.txt + "\n"
