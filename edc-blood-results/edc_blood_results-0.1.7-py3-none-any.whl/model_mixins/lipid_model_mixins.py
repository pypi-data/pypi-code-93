from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_reportable.units import MILLIMOLES_PER_LITER

from .factory import blood_results_model_mixin_factory


class CholModelMixin(
    blood_results_model_mixin_factory(
        utest_id="chol",
        verbose_name="Total Cholesterol",
        decimal_places=2,
        max_digits=8,
        units_choices=((MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER),),
        validators=[MinValueValidator(0.0), MaxValueValidator(999.0)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class HdlModelMixin(
    blood_results_model_mixin_factory(
        utest_id="hdl",
        decimal_places=2,
        max_digits=8,
        units_choices=((MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER),),
        validators=[MinValueValidator(0.0), MaxValueValidator(999.0)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class LdlModelMixin(
    blood_results_model_mixin_factory(
        utest_id="ldl",
        decimal_places=2,
        max_digits=8,
        units_choices=((MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER),),
        validators=[MinValueValidator(0.0), MaxValueValidator(999.0)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class TrigModelMixin(
    blood_results_model_mixin_factory(
        utest_id="trig",
        decimal_places=2,
        max_digits=8,
        units_choices=((MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER),),
        validators=[MinValueValidator(0.0), MaxValueValidator(999.0)],
        verbose_name="Triglycerides",
    ),
    models.Model,
):
    class Meta:
        abstract = True
