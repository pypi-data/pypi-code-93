from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_reportable import GRAMS_PER_DECILITER
from edc_reportable.units import GRAMS_PER_LITER, IU_LITER, IU_LITER_DISPLAY

from .factory import blood_results_model_mixin_factory


class AlbuminModelMixin(
    blood_results_model_mixin_factory(
        utest_id="albumin",
        verbose_name="Serum albumin",
        units_choices=(
            (GRAMS_PER_DECILITER, GRAMS_PER_DECILITER),
            (GRAMS_PER_LITER, GRAMS_PER_LITER),
        ),
        decimal_places=1,
        validators=[MinValueValidator(1.0), MaxValueValidator(999.0)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class AlpModelMixin(
    blood_results_model_mixin_factory(
        utest_id="alp",
        units_choices=((IU_LITER, IU_LITER_DISPLAY),),
        decimal_places=1,
        validators=[MinValueValidator(1.0), MaxValueValidator(999.0)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class AltModelMixin(
    blood_results_model_mixin_factory(
        utest_id="alt",
        units_choices=((IU_LITER, IU_LITER_DISPLAY),),
        decimal_places=1,
    ),
    models.Model,
):
    class Meta:
        abstract = True


class AstModelMixin(
    blood_results_model_mixin_factory(
        utest_id="ast",
        units_choices=((IU_LITER, IU_LITER_DISPLAY),),
        decimal_places=0,
        validators=[MinValueValidator(1.0), MaxValueValidator(999.0)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class AmylaseModelMixin(
    blood_results_model_mixin_factory(
        utest_id="amylase",
        verbose_name="Serum Amylase",
        units_choices=((IU_LITER, IU_LITER_DISPLAY),),
        decimal_places=1,
        validators=[MinValueValidator(1.0), MaxValueValidator(999.0)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class GgtModelMixin(
    blood_results_model_mixin_factory(
        utest_id="ggt",
        units_choices=((IU_LITER, IU_LITER_DISPLAY),),
        decimal_places=0,
        validators=[MinValueValidator(1.0), MaxValueValidator(999.0)],
    ),
    models.Model,
):
    class Meta:
        abstract = True
