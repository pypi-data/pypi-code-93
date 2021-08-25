from ._descriptor import Descriptor


# Unsigned
class Unsigned(Descriptor):
    def __set__(self, instance, value):
        if value < 0:
            raise ValueError("expected >= 0")

        super().__set__(instance, value)


# MaxSizedIterable
class MaxSizedIterable(Descriptor):
    def __init__(self, name=None, **opts):
        if "size" not in opts:
            raise ValueError("missing size option")

        super().__init__(name, **opts)

    def __set__(self, instance, value):
        if len(value) > self.size:
            raise ValueError("size must be <= {}".format(self.size))

        super().__set__(instance, value)


# MinSizedIterable
class MinSizedIterable(Descriptor):
    def __init__(self, name=None, **opts):
        if "size" not in opts:
            raise ValueError("missing size option")

        super().__init__(name, **opts)

    def __set__(self, instance, value):
        if len(value) < self.size:
            raise ValueError("size must be >= {}".format(self.size))

        super().__set__(instance, value)


# MaxSizedInteger
class MaxSizedInteger(Descriptor):
    def __init__(self, name=None, **opts):
        if "size" not in opts:
            raise ValueError("missing size option")

        super().__init__(name, **opts)

    def __set__(self, instance, value):
        if value >= self.size:
            raise ValueError("size must be < {}".format(self.size))
        elif not isinstance(value, (int, float)):
            raise TypeError("cannot change to type {!r}".format(type(value).__name__))

        super().__set__(instance, value)


# MinSizedInteger
class MinSizedInteger(Descriptor):
    def __init__(self, name=None, **opts):
        if "size" not in opts:
            raise ValueError("missing size option")

        super().__init__(name, **opts)

    def __set__(self, instance, value):
        if value < self.size:
            raise ValueError("size must be >= {}".format(self.size))
        elif not isinstance(value, (int, float)):
            raise TypeError("cannot change to type {!r}".format(type(value).__name__))

        super().__set__(instance, value)
