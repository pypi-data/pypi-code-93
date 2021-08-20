from enum import Enum

from django.db import models


class Stimulus(models.Model):
    class TYPE(Enum):
        auditive = (0, 'auditive')
        gustatory = (1, 'gustatory')
        haptic = (2, 'haptic')
        olfactory = (3, 'olfactory')
        visual = (4, 'visual')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    type = models.PositiveSmallIntegerField(choices=[x.value for x in TYPE])
