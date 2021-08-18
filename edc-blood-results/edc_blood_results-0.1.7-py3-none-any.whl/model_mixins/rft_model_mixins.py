from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_reportable.units import (
    EGFR_UNITS,
    MICROMOLES_PER_LITER,
    MICROMOLES_PER_LITER_DISPLAY,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
    MILLIMOLES_PER_LITER_DISPLAY,
)

from .factory import blood_results_model_mixin_factory


class CreatinineModelMixin(
    blood_results_model_mixin_factory(
        utest_id="creatinine",
        verbose_name="Creatinine",
        units_choices=(
            (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
            (MICROMOLES_PER_LITER, MICROMOLES_PER_LITER_DISPLAY),
        ),
    ),
    models.Model,
):
    class Meta:
        abstract = True


class EgfrModelMixin(
    blood_results_model_mixin_factory(
        utest_id="egfr",
        verbose_name="eGFR",
        decimal_places=4,
        default_units=EGFR_UNITS,
        max_digits=8,
        units_choices=((EGFR_UNITS, EGFR_UNITS),),
    ),
    models.Model,
):
    class Meta:
        abstract = True


class UreaModelMixin(
    blood_results_model_mixin_factory(
        utest_id="urea",
        verbose_name="Urea (BUN)",
        units_choices=((MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),),
    ),
    models.Model,
):
    class Meta:
        abstract = True


class UricAcidModelMixin(
    blood_results_model_mixin_factory(
        utest_id="uric_acid",
        verbose_name="Uric Acid",
        decimal_places=4,
        max_digits=10,
        units_choices=(
            (MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
            (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
        ),
    ),
    models.Model,
):
    class Meta:
        abstract = True
