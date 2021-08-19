import argparse
import logging
from pathlib import Path

from include_file.models import File, Gitbook, Include, Link, Markdown, Repo, Repository, Image


def get_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('-l', '--log_level', type=int, default=20)
  parser.add_argument('-t', '--test', action='store_true')

  # Flags
  parser.add_argument('-images', '--images_overwrite', default='images')
  parser.add_argument('-include', '--include_overwrite', default='include')
  parser.add_argument('-link', '--link_overwrite', default='link')
  parser.add_argument('-repo', '--repo_overwrite', default="repo")

  parser.add_argument('-g', '--glob', type=str, default="**/*")
  parser.add_argument('-p', '--path', type=Path, default=Path("."))
  parser.add_argument('-s', '--stem', action='store_true')
  parser.add_argument('-v', '--validate', action='store_true')
  parser.add_argument('-e', '--include_path', type=str, default=".include_file")
  parser.add_argument('-u', '--user', type=str, default="", help="Need in order to use link")

  # Gitbook Flags
  parser.add_argument('-y', '--summary_path', default="")
  parser.add_argument('-d', '--deploy_branch', default="deploy")
  parser.add_argument('-toc', '--table_of_contents_path', default="")
  parser.add_argument('-url', '--url_path', type=str, default="")

  return parser.parse_args()


if __name__ == "__main__":
  ag = get_parser()
  logging.basicConfig(
      format='%(asctime)s %(levelname)-6s [%(filename)s:%(lineno)d] %(message)s',
      datefmt='%H%M%S',
  )
  logging.getLogger().setLevel(ag.log_level)

  Include.OVERWRITE = ag.include_overwrite
  Link.OVERWRITE = ag.link_overwrite
  Repo.OVERWRITE = ag.repo_overwrite
  Image.OVERWRITE = ag.images_overwrite

  if ag.summary_path:
    book = Gitbook(
        ag.path.resolve(),
        ag.glob,
        ag.include_path,
        ag.stem,
        ag.deploy_branch,
        ag.user,
        ag.url_path,
    )

    book.summary = Markdown(book, book.path / ag.summary_path)

    if ag.table_of_contents_path:
      book.toc = File(book, book.path / ag.table_of_contents_path)
      table_of_contents = book.table_of_contents()
      book.toc.path.write_text(table_of_contents)

    book.include_file(ag.test)
  else:
    repo = Repository(
        ag.path,
        ag.glob,
        ag.include_path,
        ag.stem,
        ag.deploy_branch,
        ag.user,
    )
    repo.include_file(ag.test)
