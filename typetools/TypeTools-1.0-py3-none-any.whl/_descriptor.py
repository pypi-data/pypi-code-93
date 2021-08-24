# Descriptor
class Descriptor:
    def __init__(self, name=None, **opts):
        self.name = name

        for k, v in opts.items():
            setattr(self, k, v)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
