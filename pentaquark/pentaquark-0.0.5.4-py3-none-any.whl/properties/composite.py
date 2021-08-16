import json
from .scalars import StringProperty, Property
from .choices import ChoiceMeta
from ..exceptions import PentaQuarkValidationError


class JSONProperty(StringProperty):
    def from_cypher(self, __value):
        if __value:
            return json.loads(__value)

    def to_cypher(self, __value):
        if __value:
            return json.dumps(__value)

    def _validate(self, __value):
        if __value is None:
            return None
        try:
            json.dumps(__value)
        except TypeError as e:
            raise PentaQuarkValidationError(f"'{__value}' is not json serializable ({e})")
        return __value

    def to_graphql(self, __value):
        return json.dumps(__value)


class ArrayProperty(Property):
    def __init__(self, internal_type=StringProperty, max_length=None, **kwargs):
        super().__init__(**kwargs)
        self.internal_type = internal_type
        self.max_length = max_length

    def _validate(self, __value):
        if __value is None:
            return None
        if isinstance(__value, (list, set, tuple)):
            if self.max_length and len(__value) > self.max_length:
                raise PentaQuarkValidationError(
                    f"'{__value}' is too long: {len(__value)} > {self.max_length}"
                )
            return list(__value)
        raise PentaQuarkValidationError(f"'{__value}' is not an iterable")

    def get_graphql_type(self):
        return f"[{self.internal_type.get_graphql_type()}]"


class ChoiceProperty(Property):
    def __init__(self, choices: ChoiceMeta, internal_type=StringProperty(), **kwargs):
        super().__init__(**kwargs)
        self.choices = choices
        self.internal_type = internal_type

        # make sure choices values are compatible with the internal type
        for c in choices:
            self.internal_type._validate(c.value)

    def from_cypher(self, __value):
        if __value:
            v = self.internal_type.from_cypher(__value)
            c = self.choices(v)
            return c

    def to_cypher(self, __value):
        if __value:
            c = self.choices(__value)
            return self.internal_type.to_cypher(c.value)

    def _validate(self, __value):
        if __value is None:
            return None
        try:
            return self.choices(__value)
        except ValueError:
            raise PentaQuarkValidationError(f"'{__value}' is not a valid choice for {self.choices}")

    def get_graphql_type(self):
        return self.internal_type.get_graphql_type()

    def to_graphql(self, __value):
        # make sure we return the choice value and not the choice instance which is not serializable
        v = self._validate(__value)
        return self.internal_type.to_graphql(v.value)
