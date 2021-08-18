from typing import Optional, Type

from django.core.validators import MinValueValidator
from django.db import models
from edc_constants.choices import GRADING_SCALE_WITH_NOT_GRADED, YES_NO
from edc_reportable.choices import REPORTABLE


def get_field_attrs(
    utest_id: str,
    units_choices: tuple,
    default_units: Optional[str] = None,
    verbose_name: Optional[str] = None,
    decimal_places: Optional[int] = None,
    max_digits: Optional[int] = None,
    validators: Optional[list] = None,
) -> dict:
    """Returns a dictionary of field classes for the model"""
    value_options = dict(
        verbose_name=verbose_name or utest_id.upper(),
        decimal_places=decimal_places or 2,
        max_digits=max_digits or 6,
        validators=validators or [MinValueValidator(0.00)],
        null=True,
        blank=True,
    )
    units_options = dict(
        verbose_name="units",
        max_length=15,
        choices=units_choices,
        null=True,
        blank=True,
    )
    if default_units:
        units_options.update(default=default_units)

    return {
        f"{utest_id}_value": models.DecimalField(**value_options),
        f"{utest_id}_units": models.CharField(**units_options),
        f"{utest_id}_abnormal": models.CharField(
            verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
        ),
        f"{utest_id}_reportable": models.CharField(
            verbose_name="reportable",
            choices=REPORTABLE,
            max_length=25,
            null=True,
            blank=True,
        ),
        f"{utest_id}_grade": models.IntegerField(
            verbose_name="Grade",
            choices=GRADING_SCALE_WITH_NOT_GRADED,
            null=True,
            blank=True,
        ),
        f"{utest_id}_grade_description": models.CharField(
            verbose_name="Grade description",
            max_length=250,
            null=True,
            blank=True,
        ),
    }


def blood_results_model_mixin_factory(
    utest_id: str,
    units_choices: tuple,
    default_units: Optional[str] = None,
    verbose_name: Optional[str] = None,
    decimal_places: Optional[int] = None,
    max_digits: Optional[int] = None,
    validators: Optional[list] = None,
) -> Type[models.Model]:
    """Returns an abstract model class"""

    class AbstractModel(models.Model):
        class Meta:
            abstract = True

    for name, fld_cls in get_field_attrs(
        utest_id,
        units_choices,
        default_units,
        verbose_name,
        decimal_places,
        max_digits,
        validators,
    ).items():
        AbstractModel.add_to_class(name, fld_cls)
    return AbstractModel
