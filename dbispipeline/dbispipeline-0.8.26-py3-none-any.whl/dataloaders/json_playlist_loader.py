"""Module containing JSON playlist dataloader."""
import json

from ..base import Loader


class JsonPlaylistLoader(Loader):
    """Loads playlist from a json file."""

    def __init__(self, path):
        """
        Creates a new instance.

        Args:
            path: the path to the playlists dataset json file.
        """
        self.path = path

    def load(self):
        """
        Returns a tuple containing data and lables.

        Both data and labels are list-like if the labels argument is set.
        Ohterwise, the labels are None.
        """
        with open(self.path) as json_file:
            dataset = json.load(json_file)

            return dataset['data'], None

        return None, None

    def dataset_info(self):
        """Returns meta info on the dataset."""
        with open(self.path) as json_file:
            dataset = json.load(json_file)

            return dataset['info']

        return None

    @property
    def configuration(self):
        """Returns a dict-like representation of the configuration."""
        return {
            'path': self.path,
        }
