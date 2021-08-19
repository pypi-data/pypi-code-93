# This file is part of the
#   headctools Project (https://gitlab.com/matzkin/headctools).
# Copyright (c) 2021, Franco Matzkin
# License: MIT
#   Full Text: https://gitlab.com/matzkin/headctools/-/blob/master/LICENSE

"""headctools Command Line Interface."""

import os
from inspect import ismethod

import typer
from ctunet.pytorch.train_test import Model

from .Preprocessor import prep_img_s, prep_img_cr
from .antspyregistration import register_folder_flirt, register_antspy
from .tools.downloader import Downloader
from .tools.flap_reconstruction import FlapReconstruction
from .tools.offline_augmentation import simulate_cr_images
from .utilities import simple_csv

__version__ = "0.2"
VERSION = __version__


class CLI:
    """headctools console client."""

    footnotes = "\n".join(
        [
            "MIT License.",
            "Copyright (c) 2020.",
            "Franco Matzkin.",
        ]
    )

    def get_commands(self):
        """Return CLI commands.

        Returns
        -------
        Typer
            Typer app with the valid CLI commands
        """
        app = typer.Typer()
        for k in dir(self):
            if k.startswith("_"):
                continue
            v = getattr(self, k)
            if ismethod(v) and k != "get_commands":
                decorator = app.command()
                decorator(v)
        return app

    def version(self):
        """Print headctools version."""
        print(VERSION)

    def register(
            self,
            input_ff="",
            atlas_path="",
            mask_id=None,
            overwrite_files=False,
    ):
        """Register a file or pred_folder.

        Parameters
        ----------
        input_ff: str
            File or pred_folder to register.
        atlas_path: str
            Path of the atlas for registering.
        mask_id: str
            If given, it will register the files with that identificator
            with the same transformation as the file without the id.
        overwrite_files: bool
            Overwrite files in case of existing.
        """

        if not os.path.exists(input_ff):
            raise typer.BadParameter(
                "The input file/pred_folder wasn't found ({})".format(input_ff)
            )

        if os.path.isdir(input_ff):
            register_folder_flirt(
                input_ff, atlas_path, mask_id, overwrite=overwrite_files
            )
        elif os.path.isfile(input_ff):
            register_antspy(
                input_ff,
                atlas_path,
                transformation="rigid",
                interp="nearestneighbour",
                overwrite=overwrite_files,
            )

    def preprocess(
            self,
            input_ff="",
            prep_type="",
            image_id=None,
            mask_id=None,
            overwrite=False,
            output_folder=None,
    ):
        valid_types = ["segmentation", "reconstruction"]
        if prep_type not in valid_types:
            if prep_type == '':
                raise typer.BadParameter(
                    "You should specify a preprocessing type ({})".format(
                        ", ".join(valid_types)
                    )
                )
            else:
                raise typer.BadParameter(
                    "'{}' does not correspond to a valid prep_type ("
                    "{})".format(prep_type, ", ".join(valid_types))
                )
        if not os.path.isdir(input_ff):
            raise typer.BadParameter(
                "The input pred_folder does not exists ({})".format(input_ff)
            )
        if prep_type == "segmentation":
            prep_img_s(
                input_ff, output_folder, image_id, mask_id, True, overwrite
            )
        elif prep_type == "reconstruction":
            prep_img_cr(
                input_ff, output_folder, image_id, mask_id, True, overwrite
            )

    def model(self, ini_file):
        """ Run CT-UNet with the configuration set in the ini file.

        :param ini_file: ini file with the training / test parameters.
        :return:
        """
        Model(ini_file)

    def flaprec(self, input_ff, out_path=None, model='UNetSP',
                show_intermediate: bool = typer.Option(False,
                                                      "--show_intermediate"),
                skip_prepr: bool = typer.Option(False, "--skip_prepr")):
        """ Preprocess the image, predict the bone flap and sum the flap to
        the preprocessed skull.

        :param input_ff: Input file or pred_folder.
        :param out_path: Output file or pred_folder path.
        :param model: Trained model name (see which are available trough the
        download option). Default: UNetSP.
        :param show_intermediate: Use SimpleITK for showing intermediate
        :param skip_prepr: If the images in the folder are already
        preprocessed, set this flag to True.
        images.
        :return:
        """
        FlapReconstruction(input_ff, out_path, model,
                           show_intermediate=show_intermediate,
                           skip_prep=skip_prepr)

    def gen_defects(self, input_ff, out_folder, n_reps=10, image_id='image'):
        """ Generate defects of the input file/pred_folder.

        :param input_ff: Input file or pred_folder
        :param out_folder: Output file or pred_folder path.
        :param n_reps: Amount of times that the augmentation will be done.
        :param image_id: Image identification (only generate defects to imgs
        with this ID).
        :return:
        """
        simulate_cr_images(input_ff, n_reps, image_id, out_folder)

    def download(self, model_name, workspace_path='~/headctools'):
        """ Downlaod a previously trained model.

        Download one of the built-in trained models. Currently, the UNetSP
        model for flap/skull reconstruction is available.

        :param model_name: Model name.
        :param workspace_path: Workspace path. By default it will be the
        headctools folder in the user OS folder.
        """
        Downloader(model_name, workspace_path)

    def gen_csv(self, input_folder, csv_name='files.csv', ext='nii.gz'):
        """ Generate a CSV file of the files in a folder.

        :param input_folder: Input folder.
        :param csv_name: Output filename.
        :param ext: File extension.
        """
        simple_csv(input_folder, csv_name, ext)


def main():
    """Run the headctools CLI interface."""
    cli = CLI()
    app = cli.get_commands()
    app()


if __name__ == "__main__":
    main()
