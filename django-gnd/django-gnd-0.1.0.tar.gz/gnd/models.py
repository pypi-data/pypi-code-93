from datetime import datetime
from dateutil.parser import parse, ParserError
from django.db import models
from pylobid.pylobid import PyLobidClient, PyLobidPerson
from . fields import GndField
from . utils import fetch_gender


class GndBaseModel(models.Model):
    gnd_gnd_id = GndField(
        blank=True, null=True, unique=True
    )
    gnd_pref_name = models.CharField(
        blank=True, null=True, max_length=250
    )
    gnd_payload = models.JSONField(blank=True, null=True)
    gnd_created = models.DateTimeField(
        blank=True, null=True, auto_now=False, auto_now_add=False
    )

    def __str__(self):
        return f"{self.gnd_pref_name} <{self.gnd_gnd_id}>"

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.gnd_gnd_id and not self.gnd_created:
            py_ent = PyLobidClient(self.gnd_gnd_id, fetch_related=True).factory()
            self.gnd_pref_name = py_ent.pref_name
            self.gnd_payload = py_ent.ent_dict
            self.gnd_created = datetime.now()
        super().save(*args, **kwargs)


class GndPersonBase(GndBaseModel):
    gnd_gender = models.CharField(
        blank=True, null=True, max_length=250
    )
    gnd_birth_date_written = models.CharField(
        blank=True, null=True, max_length=250
    )
    gnd_death_date_written = models.CharField(
        blank=True, null=True, max_length=250
    )
    gnd_birth_date = models.DateField(
        blank=True, null=True
    )
    gnd_death_date = models.DateField(
        blank=True, null=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.gnd_gnd_id and not self.gnd_created:
            py_ent = PyLobidClient(self.gnd_gnd_id, fetch_related=False).factory()
            if isinstance(py_ent, PyLobidPerson):
                self.gnd_birth_date_written = py_ent.life_span['birth_date_str']
                self.gnd_death_date_written = py_ent.life_span['death_date_str']
                try:
                    self.gnd_birth_date = parse(self.gnd_birth_date_written)
                except ParserError:
                    pass
                try:
                    self.gnd_death_date = parse(self.gnd_death_date_written)
                except ParserError:
                    pass
                self.gnd_gender = fetch_gender(self.gnd_payload)
        super().save(*args, **kwargs)
