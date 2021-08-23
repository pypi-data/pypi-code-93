import factory

from ob_dj_otp.core.otp.models import OneTruePairing


class OneTruePairingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OneTruePairing

    class Params:
        register = factory.Trait(
            status=OneTruePairing.Statuses.init, usage=OneTruePairing.Usages.register
        )
