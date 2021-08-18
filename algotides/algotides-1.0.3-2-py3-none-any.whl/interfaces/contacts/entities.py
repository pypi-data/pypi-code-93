# Python
from pathlib import Path
from sys import stderr


# Tides
from algotides import constants as constants


class Contact:
    """
    Object that represents a single contact in the contact list.
    """
    def __init__(self, pic_name: str, name: str, address: str):
        self.pic_name = pic_name
        self.name = name
        self.info = address

    # This is a better solution than to rename with refactoring self.info to self.address because old versions of this
    #   package serialized data with that property name. If we rename it we get into some issues when de-serializing.
    # This way we can change the code in the project to a more expressive name but we don't lose old serialized data.
    @property
    def address(self) -> str:
        return self.info

    def release(self):
        """
        Method to destroy profile picture on disk.
        """
        if self.pic_name:
            try:
                Path.joinpath(constants.PATH_THUMBNAILS, self.pic_name).unlink()
            except FileNotFoundError as e:
                if __debug__:
                    print(type(e), str(e), file=stderr)
                print(f"Could not delete profile picture for {self.name}", file=stderr)
