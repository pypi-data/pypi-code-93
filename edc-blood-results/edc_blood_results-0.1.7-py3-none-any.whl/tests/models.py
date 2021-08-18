from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_crf.crf_with_action_model_mixin import CrfWithActionModelMixin
from edc_model import models as edc_models
from edc_reportable import GRAMS_PER_DECILITER

from edc_blood_results import BLOOD_RESULTS_FBC_ACTION
from edc_blood_results.model_mixins import (
    BloodResultsModelMixin,
    HaemoglobinModelMixin,
    HctModelMixin,
    PlateletsModelMixin,
    RbcModelMixin,
    RequisitionModelMixin,
    WbcModelMixin,
)
from edc_blood_results.model_mixins.factory import blood_results_model_mixin_factory


class BloodResultsFbc(
    CrfWithActionModelMixin,
    RequisitionModelMixin,
    HaemoglobinModelMixin,
    HctModelMixin,
    RbcModelMixin,
    WbcModelMixin,
    PlateletsModelMixin,
    BloodResultsModelMixin,
    edc_models.BaseUuidModel,
):

    action_name = BLOOD_RESULTS_FBC_ACTION

    tracking_identifier_prefix = "FB"

    class Meta(CrfWithActionModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Blood Result: FBC"
        verbose_name_plural = "Blood Results: FBC"


class AbcModelMixin(
    blood_results_model_mixin_factory("hct", ((GRAMS_PER_DECILITER, GRAMS_PER_DECILITER),)),
    models.Model,
):
    # HCT
    hct_value = models.DecimalField(
        validators=[MinValueValidator(1.0), MaxValueValidator(999.0)],
        verbose_name="Hematocrit",
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
