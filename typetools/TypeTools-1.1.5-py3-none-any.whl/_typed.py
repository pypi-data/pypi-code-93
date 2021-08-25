from ._descriptor import Descriptor


# Typed
class Typed(Descriptor):
    expected_type = type(None)

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError("expected {!r}".format(self.expected_type))

        super().__set__(instance, value)
