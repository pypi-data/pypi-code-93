import requests
from django.db import models
from django.utils.translation import gettext, gettext_lazy as _


# Create your models here.


class Region(models.Model):

    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _('Regions')

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=254
    )

    acronym = models.CharField(
        verbose_name=_('Acronym'),
        max_length=2
    )

    def __str__(self):
        return self.name


class State(models.Model):

    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _('States')

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=254
    )

    acronym = models.CharField(
        verbose_name=_('Acronym'),
        max_length=2
    )

    region = models.ForeignKey(
        'Region',
        verbose_name=_('Region'),
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class City(models.Model):

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=254
    )

    state = models.ForeignKey(
        'State',
        verbose_name=_('State'),
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Address(models.Model):

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    zipcode = models.CharField(
        verbose_name=_('Zipcode'),
        max_length=8,
        blank=True,
        null=True
    )

    state = models.ForeignKey(
        'State',
        verbose_name=_('State'),
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    city = models.ForeignKey(
        'City',
        verbose_name=_('City'),
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    district = models.CharField(
        verbose_name=_('District'),
        max_length=254
    )

    address = models.CharField(
        verbose_name=_('Address'),
        max_length=254
    )

    number = models.IntegerField(
        verbose_name=_('Number'),
    )

    complement = models.CharField(
        verbose_name=_('Complement'),
        max_length=254
    )

    def __str__(self):
        return self.address


def import_regions():
    """
    docstring
    """

    response = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/regioes')
    data = response.json()

    for item in data:
        region = Region()
        region.pk = item.get("id")
        region.name = item.get("nome")
        region.acronym = item.get("sigla")
        region.save()


def import_state():
    """
    docstring
    """

    response = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/estados')
    data = response.json()

    for item in data:
        state = State()
        state.pk = item.get("id")
        state.name = item.get("nome")
        state.acronym = item.get("sigla")
        state.region = Region.objects.get(pk=item.get("regiao").get("id"))
        state.save()


def import_cities():
    """
    docstring
    """

    response = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/municipios')
    data = response.json()

    for item in data:
        city = City()
        city.pk = item.get("id")
        city.name = item.get("nome")
        city.state = State.objects.get(pk=item.get("microrregiao").get("mesorregiao").get("UF").get("id"))
        city.save()
