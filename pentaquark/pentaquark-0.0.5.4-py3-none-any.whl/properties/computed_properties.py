from slugify import slugify

from .scalars import Property
from ..exceptions import PentaQuarkValidationError


class ComputedProperty(Property):
    def __init__(self, func, graphql_type="String", deps=None, **kwargs):
        super().__init__(**kwargs)
        self.deps = deps or []
        self.func = func
        self.graphql_type = graphql_type

    def _validate(self, __value):
        if __value:
            return __value
        data = {}
        for d in self.deps:
            data[d] = getattr(self.instance, d, None)
        try:
            __value = self.func(**data)
        except Exception as e:
            raise PentaQuarkValidationError(e)
        return super()._validate(__value)


class SlugProperty(ComputedProperty):
    def __init__(self, source, **kwargs):
        def func(**kws):
            v = kws.get(source)
            if v is None:
                return v
            return slugify(kws.get(source))
        super().__init__(func, deps=[source], **kwargs)
