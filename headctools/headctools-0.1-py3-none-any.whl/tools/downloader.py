import os
import tempfile
from distutils.dir_util import copy_tree
from zipfile import ZipFile

import pandas as pd
import requests
from .. import utilities as utils

from ..assets.download import DPATH


class Downloader:
    def __init__(self, asset_to_download, workspace_path=None):
        """ Download a predefined asset (model/atlas) and save it in the
        workspace folder.

        The files that will be downloaded are listed in .csv files located in
        the assets/download folder. They contain a URL of a compressed .zip
        file of the asset, and the filename of the file contained.

        IMPORTANT: The csv's path field will only be used for checking previous
        download. The filenames/folder structure will be determined by the .zip
        extracted files.

        :param asset_to_download: String of the asset to download. (UNetSP).
        :param workspace_path: Workspace path.
        """
        self.asset = asset_to_download  # Name (without extension) of the asset

        # Set workspace path and expand folder.
        wksp = workspace_path if workspace_path else '~/headctools'
        self.workspace = os.path.expanduser(wksp) if wksp[0] == '~' else wksp

        self.download()  # Download all the listed files.

    def download(self):
        df = self.get_assets_per_name(self.asset)

        # List of tuples in the form (url,path)
        files_to_download = [tuple(row) for row in df.values]

        print(f"Downloading {self.asset}...")
        for i, file in enumerate(files_to_download):
            url, path = file
            folder, f_name = os.path.split(path)

            # Paths including the workspace
            file_wspace = os.path.join(self.workspace, path)

            print(f"[{i + 1}/{len(files_to_download)}] {f_name}...")

            if os.path.exists(os.path.expanduser(file_wspace)):
                print(f"  file already downloaded {file_wspace} (skipping).")
                continue

            print(f"  Getting file from {url}...")
            r = requests.get(url, allow_redirects=True)
            print("  Extracting file...")
            zip_path = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
            with open(zip_path.name, 'wb') as f:
                f.write(r.content)

            print("  Copying file to workspace...")
            tmp_folder = os.path.join(os.path.split(zip_path.name)[0],
                                      f'headctools-{self.asset}')
            utils.veri_folder(tmp_folder)
            utils.veri_folder(self.workspace)

            with ZipFile(zip_path, 'r') as zip_obj:
                zip_obj.extractall(tmp_folder)

            copy_tree(tmp_folder, os.path.expanduser(self.workspace))
        print("all done!")

    @staticmethod
    def get_assets_per_name(asset, skip_validation=False):
        """ From an asset string name, get the csv data as dataframe if exists.

        It will receive a string that could be a downloaded model (e.g. UNet)
        and it will provide a pandas dataframe with the content of the
        corresponding csv, if it exists.


        :param asset: Name of the asset to download.
        :return: Pandas dataframe containing the csv contents (asset path +
        location inside the workspace).
        """
        if not os.path.exists(DPATH):  # Check DPATH
            raise FileNotFoundError(f"DPATH does not exist.")

        csv_file = os.path.join(DPATH, asset + '.csv')  # Tentative csv file
        if not os.path.exists(csv_file):
            avaiable = [f.replace('.csv', '') for f in os.listdir(DPATH) if
                        f.endswith('csv')]
            avaiable_str = ', '.join(avaiable)

            raise AttributeError(f"The model you want to download is not "
                                 f"valid ({asset}.).\nAvailable models are: "
                                 f"{avaiable_str}.")

        df = pd.read_csv(csv_file, delimiter=',')  # Read the csv

        if not skip_validation:
            Downloader.check_csv_fields(df)

        return df

    @staticmethod
    def check_csv_fields(data):
        """ Check if the provided dataframe contains the url and path fields.

        It will raise an Exception in case the header doesn't match the
        desired one.

        :param data: Pandas dataframe listing the data.
        """
        if list(data.columns) != ['url', 'path']:
            raise AttributeError("The csv file does not contain the required "
                                 "fields (url, path).")


