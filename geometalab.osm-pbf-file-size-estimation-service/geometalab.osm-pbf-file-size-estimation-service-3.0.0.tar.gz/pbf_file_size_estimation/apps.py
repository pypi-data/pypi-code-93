from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PBFFileSizeEstimationConfig(AppConfig):
    name = "pbf_file_size_estimation"
    verbose_name = _("PBF File Size Estimation")
