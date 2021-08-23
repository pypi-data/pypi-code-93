from django.db import models
from edc_constants.choices import YES_NO_NA, YES_NO_NOT_EXAMINED
from edc_constants.constants import NOT_APPLICABLE, NOT_EXAMINED
from edc_model import models as edc_models

from .choices import (
    ANKLE_REFLEX_CHOICES,
    MONOFILAMENT_CHOICES,
    ULCERATION_CHOICES,
    VIBRATION_PERCEPTION_CHOICES,
)


def foot_exam_model_mixin_factory(
    foot_choice, abnormal_foot_appearance_observations_model=None
):
    """Returns an abstract model mixin"""

    class AbstractModel(models.Model):
        class Meta:
            abstract = True

    yes_no__na_options = dict(
        max_length=15,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
    )
    yes_no_not_examined_options = dict(
        max_length=15,
        choices=YES_NO_NOT_EXAMINED,
        default=NOT_EXAMINED,
        help_text=(
            f"If the assessment was not performed or this "
            "foot was not examined, respond with `not examined`."
        ),
    )

    not_examined_options = dict(
        max_length=35,
        default=NOT_EXAMINED,
        help_text=(
            f"If the assessment was not performed or this "
            "foot was not examined, respond with `not examined`."
        ),
    )

    attrs = {
        f"examined_{foot_choice}_foot": models.CharField(
            verbose_name=f"Was the {foot_choice.upper()} foot examined?",
            help_text="If the assessment was not performed, respond with `not applicable`.",
            **yes_no__na_options,
        ),
        f"normal_appearance_{foot_choice}_foot": models.CharField(
            verbose_name=f"Does {foot_choice.upper()} foot appear normal?",
            **yes_no_not_examined_options,
        ),
        f"abnormal_obs_{foot_choice}_foot": models.ManyToManyField(
            abnormal_foot_appearance_observations_model,
            related_name=f"abnormal_obs_{foot_choice}_foot",
            verbose_name=f"If NO, check all that apply to {foot_choice.upper()} foot?",
            blank=True,
        ),
        f"abnormal_obs_{foot_choice}_foot_other": edc_models.OtherCharField(
            verbose_name=(
                "If other abnormality observed on "
                f"{foot_choice.upper()} foot, please specify ..."
            ),
        ),
        f"ulceration_{foot_choice}_foot": models.CharField(
            verbose_name=f"Ulceration, {foot_choice.upper()} foot?",
            choices=ULCERATION_CHOICES,
            **not_examined_options,
        ),
        f"ankle_reflexes_{foot_choice}_foot": models.CharField(
            verbose_name=f"Ankle reflexes, {foot_choice.upper()} foot?",
            choices=ANKLE_REFLEX_CHOICES,
            **not_examined_options,
        ),
        f"vibration_perception_{foot_choice}_toe": models.CharField(
            verbose_name=f"Vibration perception at great toe, {foot_choice.upper()} foot?",
            choices=VIBRATION_PERCEPTION_CHOICES,
            **not_examined_options,
        ),
        f"monofilament_{foot_choice}_foot": models.CharField(
            verbose_name=f"Monofilament, {foot_choice.upper()} foot?",
            choices=MONOFILAMENT_CHOICES,
            **not_examined_options,
        ),
    }
    for name, fld_cls in attrs.items():
        AbstractModel.add_to_class(name, fld_cls)
    return AbstractModel
