from edc_model import models as edc_models

from edc_mnsi.model_mixins import MnsiModelMixin


class Mnsi(
    MnsiModelMixin,
    edc_models.BaseUuidModel,
):
    class Meta(MnsiModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        pass
