from pathlib import Path
from typing import List, Optional, Tuple

import click
from tqdm import tqdm

from grid.cli import rich_click
from grid.cli.core import Artifact, Experiment, Run
from grid.cli.utilities import is_experiment
from grid.sdk.utils.downloader import DownloadableObject, Downloader


def _download_artifacts(artifacts: List[Artifact], download_dir: str, desc=None) -> None:
    """
    Downloads a set of artifacts from Grid.

    Parameters
    ----------
    artifacts: List[Artifact]
        List of Artifact objects.

    download_dir: str
        Download directory for artifacts
    """
    # Create host directory.
    Downloader.create_dir_tree(dest_dir=download_dir)

    # Create downloadable objects.
    files_to_download = []
    for artifact in artifacts:
        files_to_download.append(
            DownloadableObject(url=artifact.url, download_path=artifact.path, filename=artifact.filename)
        )

    # Start download if there are any files to download.
    if files_to_download:
        D = Downloader(downloadable_objects=files_to_download, base_dir=download_dir)
        D.download()


@rich_click.command()
@click.option(
    "--download_dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    required=False,
    default="./grid_artifacts",
    help="Download directory that will host all artifact files."
)
@rich_click.argument(
    "runs_or_experiments", type=str, required=True, nargs=-1, help="The run or experiment to download artifacts for."
)
def artifacts(runs_or_experiments: List[str], download_dir: Optional[str] = None) -> None:
    """Downloads artifacts for a given run or experiments."""
    click.echo("Downloading artifacts. This command may take a while")
    experiments: List[Tuple[Path, Experiment]] = []
    for element in runs_or_experiments:
        if is_experiment(element):
            experiment = Experiment(name=element)
            experiments.append((Path(download_dir), experiment), )
        else:
            # Runs need their own host directory to make
            # it different than experiments.
            host_path = Path(download_dir) / Path(element)
            run = Run(name=element)
            for experiment in run.experiments:
                experiments.append((host_path, experiment))
    exp_iter = tqdm(experiments, unit="experiments")
    for dir, exp in exp_iter:
        dir: Path
        exp: Experiment
        exp_iter.set_description(exp.name)
        exp.refresh()
        _download_artifacts(exp.artifacts, download_dir=str(dir))
