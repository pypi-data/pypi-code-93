"""
This file will contain all constants needed throughout the rest of this project.
"""

# Python
from pathlib import Path


# Paths
# Single constants
PATH_APP_DATA = Path.home().joinpath(".algotides/")
_filename_contacts_jpickle = Path("./contacts.jpickle")
_filename_settings_jpickle = Path("./settings.jpickle")
_folder_thumbnails = Path("./thumbnails/")

# Composite constants
PATH_CONTACTS_JPICKLE = PATH_APP_DATA.joinpath(_filename_contacts_jpickle)
PATH_SETTINGS_JPICKLE = PATH_APP_DATA.joinpath(_filename_settings_jpickle)
PATH_THUMBNAILS = PATH_APP_DATA.joinpath(_folder_thumbnails)
