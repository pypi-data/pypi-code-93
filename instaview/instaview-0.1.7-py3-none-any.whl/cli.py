import fire
from importlib.metadata import metadata
from .scraper import InstaViewer


class Cmd:
    __doc__ = metadata("instaview").get("Summary")

    def __init__(self, username) -> None:
        self._instaviewer = InstaViewer(username)

    def stories(self):
        """Get user stories in JSON format"""
        data = self._instaviewer.get_stories(format="json")
        print(data)

    def posts(self):
        """Get user posts in JSON format"""
        data = self._instaviewer.get_posts(format="json")
        print(data)


def cli():
    fire.Fire(Cmd)


if __name__ == "__main__":
    print("hey!")
    cli()