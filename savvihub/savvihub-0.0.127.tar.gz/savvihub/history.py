from datetime import datetime
from typing import Dict, List

from openapi_client import ProtoExperimentPlotMetric, ProtoExperimentPlotFile
from savvihub.cli.commands.volume import volume_file_copy_local_to_remote
from savvihub.constants import SAVVIHUB_IMAGES, SAVVIHUB_PLOTS_FILETYPE_IMAGE
from savvihub.exceptions import ArgumentException


class History:
    def __init__(self, experiment):
        self.experiment = experiment
        self.rows = []
        self.images = []

    def update_metrics(self, client, row, step):
        """
        Update row in history
        """
        plot_metrics: Dict[str, List[ProtoExperimentPlotMetric]] = {}
        for k, v in row.items():
            if k in plot_metrics:
                plot_metrics[k].append(ProtoExperimentPlotMetric(
                    step=step,
                    timestamp=datetime.utcnow().timestamp(),
                    value=float(v),
                ))
            else:
                plot_metrics[k] = [ProtoExperimentPlotMetric(
                    step=step,
                    timestamp=datetime.utcnow().timestamp(),
                    value=float(v),
                )]

        self.rows.append(row)
        client.experiment_plots_metrics_update(self.experiment.id, plot_metrics)

    def update_images(self, client, row):
        """
        Update images in history
        """
        if not self.experiment.get_plot_volume_id():
            raise ArgumentException("Experiment plot volume id is not set")

        source_path = SAVVIHUB_IMAGES + '/'
        dest_volume_id = self.experiment.get_plot_volume_id()
        dest_path = source_path

        path_to_caption = {}
        images = row.values()
        for images in images:
            self.images = self.images + images
            for image in images:
                path_to_caption[image.get_path()] = image.get_caption()

        responses = volume_file_copy_local_to_remote(
            client,
            source_path=source_path,
            dest_volume_id=dest_volume_id,
            dest_path=dest_path,
            recursive=True
        )

        plot_files = []
        for response in responses:
            plot_files.append(ProtoExperimentPlotFile(
                step=None,
                path=response.path,
                caption=path_to_caption[response.path],
                timestamp=datetime.utcnow().timestamp(),
            ))

        client.experiment_plots_files_update(self.experiment.id, plot_files, SAVVIHUB_PLOTS_FILETYPE_IMAGE)

        for image in images:
            image.flush()
