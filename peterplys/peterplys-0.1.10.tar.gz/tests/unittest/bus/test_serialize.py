from datetime import datetime

from energytt_platform.bus import messages as m
from energytt_platform.bus.serialize import MessageSerializer
from energytt_platform.models.measurements import \
    Measurement, MeasurementType


class TestMessageSerializer:

    def test__should_serialize_and_deserialize_correctly(self):

        # -- Arrange ---------------------------------------------------------

        obj = m.MeasurementAdded(
            subject='12345',
            measurement=Measurement(
                id='1',
                type=MeasurementType.consumption,
                gsrn='12345',
                amount=123,
                begin=datetime.now(),
                end=datetime.now(),
            )
        )

        uut = MessageSerializer()

        # -- Act -------------------------------------------------------------

        serialized = uut.serialize(obj)
        deserialized = uut.deserialize(serialized)

        # -- Assert ----------------------------------------------------------

        assert isinstance(deserialized, m.MeasurementAdded)
        assert deserialized == obj
