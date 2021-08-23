import argparse
import sys
from . import gitfiler
from .exceptions import InvalidURL, UnsupportedURL

parser = argparse.ArgumentParser(
    prog="gitfiler",
    description="GitHub/GitLab single file downloader.",
    allow_abbrev=False,
)
parser.add_argument(dest="URL")
args = parser.parse_args()

try:
    file_ = gitfiler(args.URL)
    file_content = file_.text
    print(file_content)
except (InvalidURL, UnsupportedURL) as e:
    print(f"{parser.prog}: error: {e}")
    sys.exit(1)
