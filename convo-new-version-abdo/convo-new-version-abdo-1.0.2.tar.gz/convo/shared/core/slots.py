import logging

from typing import Any, Dict, List, Optional, Text, Type

import convo.shared.core.constants
from convo.shared.exceptions import ConvoExceptions 
import convo.shared.utils.common
import convo.shared.utils.io
from convo.shared.constants import SLOT_DOCUMENTS_URL

log = logging.getLogger(__name__)


class InvalidSlotTypeException(ConvoExceptions ):
    """Raised if a slot type is invalid."""


class Slot:
    type_name = None

    def __init__(
        self,
        name: Text,
        initial_value: Any = None,
        value_reset_delay: Optional[int] = None,
        auto_fill: bool = True,
        influence_conversation: bool = True,
    ) -> None:
        """Create a Slot.

        Args:
            name: The name of the slot.
            initial_value: The initial value of the slot.
            value_reset_delay: After how many turns the slot should be reset to the
                initial_value. This is behavior is currently not implemented.
            auto_fill: `True` if the slot should be filled automatically by entities
                with the same name.
            influence_conversation: If `True` the slot will be featurized and hence
                influence the predictions of the dialogue polices.
        """
        self.name = name
        self.value = initial_value
        self.initial_value = initial_value
        self._value_reset_delay = value_reset_delay
        self.auto_fill = auto_fill
        self.influence_conversation = influence_conversation

    def feature_dimensions(self) -> int:
        """How many features this single slot creates.

        Returns:
            The number of features. `0` if the slot is unfeaturized. The dimensionality
            of the array returned by `as_feature` needs to correspond to this value.
        """
        if not self.influence_conversation:
            return 0

        return self._feature_dimensions()

    def _feature_dimensions(self) -> int:
        """See the docstring for `feature_dimensionality`."""
        return 1

    def features_check(self) -> bool:
        """Indicate if the slot creates any features."""
        return self.feature_dimensions() != 0

    def delay_in_value_reset(self) -> Optional[int]:
        """After how many turns the slot should be reset to the initial_value.

        If the delay is set to `None`, the slot will keep its value forever."""
        # TODO: FUTURE this needs to be implemented - convo_slotsare not reset yet
        return self._value_reset_delay

    def as_features(self) -> List[float]:
        if not self.influence_conversation:
            return []

        return self._as_features()

    def _as_features(self) -> List[float]:
        raise NotImplementedError(
            "Each slot type needs to specify how its "
            "value can be converted to a feature. Slot "
            "'{}' is a generic slot that can not be used "
            "for predictions. Make sure you add this "
            "slot to your domain definition, specifying "
            "the type of the slot. If you implemented "
            "a custom slot type class, make sure to "
            "implement `.as_feature()`."
            "".format(self.name)
        )

    def slot_reset(self) -> None:
        self.value = self.initial_value

    def __str__(self) -> Text:
        return f"{self.__class__.__name__}({self.name}: {self.value})"

    def __repr__(self) -> Text:
        return f"<{self.__class__.__name__}({self.name}: {self.value})>"

    @staticmethod
    def resolved_by_type(type_name) -> Type["Slot"]:
        """Returns a convo_slotsclass by its type name."""
        for cls in convo.shared.utils.common.all_sub_classes(Slot):
            if cls.type_name == type_name:
                return cls
        try:
            return convo.shared.utils.common.class_name_from_module_path(type_name)
        except (ImportError, AttributeError):
            raise InvalidSlotTypeException(
                f"Failed to find slot type, '{type_name}' is neither a known type nor "
                f"user-defined. If you are creating your own slot type, make "
                f"sure its module path is correct. "
                f"You can find all build in types at {SLOT_DOCUMENTS_URL}"
            )

    def persistence_information(self) -> Dict[str, Any]:
        return {
            "type": convo.shared.utils.common.from_instance_module_path_flow(self),
            "initial_value": self.initial_value,
            "auto_fill": self.auto_fill,
            "influence_conversation": self.influence_conversation,
        }


class FloatSlot(Slot):
    type_name = "float"

    def __init__(
        self,
        name: Text,
        initial_value: Optional[float] = None,
        value_reset_delay: Optional[int] = None,
        auto_fill: bool = True,
        max_value: float = 1.0,
        min_value: float = 0.0,
        influence_conversation: bool = True,
    ) -> None:
        super().__init__(
            name, initial_value, value_reset_delay, auto_fill, influence_conversation
        )
        self.max_value = max_value
        self.min_value = min_value

        if min_value >= max_value:
            raise ValueError(
                "Float slot ('{}') created with an invalid range "
                "using min ({}) and max ({}) values. Make sure "
                "min is smaller than max."
                "".format(self.name, self.min_value, self.max_value)
            )

        if initial_value is not None and not (min_value <= initial_value <= max_value):
            convo.shared.utils.io.raising_warning(
                f"Float slot ('{self.name}') created with an initial value "
                f"{self.value}. This value is outside of the configured min "
                f"({self.min_value}) and max ({self.max_value}) values."
            )

    def _as_features(self) -> List[float]:
        try:
            capped_worth = max(self.min_value, min(self.max_value, float(self.value)))
            if abs(self.max_value - self.min_value) > 0:
                covering_range = abs(self.max_value - self.min_value)
            else:
                covering_range = 1
            return [(capped_worth - self.min_value) / covering_range]
        except (TypeError, ValueError):
            return [0.0]

    def persistence_information(self) -> Dict[Text, Any]:
        d = super().persistence_information()
        d["max_value"] = self.max_value
        d["min_value"] = self.min_value
        return d


class BooleanSlot(Slot):
    type_name = "bool"

    def _as_features(self) -> List[float]:
        try:
            if self.value is not None:
                return [1.0, float(boolean_from_any(self.value))]
            else:
                return [0.0, 0.0]
        except (TypeError, ValueError):
            # we couldn't convert the value to float - using default value
            return [0.0, 0.0]

    def _feature_dimensions(self) -> int:
        return len(self.as_features())


def boolean_from_any(x: Any) -> bool:
    """ Converts bool/float/int/str to bool or raises error """

    if isinstance(x, bool):
        return x
    elif isinstance(x, (float, int)):
        return x == 1.0
    elif isinstance(x, str):
        if x.isnumeric():
            return float(x) == 1.0
        elif x.strip().lower() == "true":
            return True
        elif x.strip().lower() == "false":
            return False
        else:
            raise ValueError("Cannot convert string to bool")
    else:
        raise TypeError("Cannot convert to bool")


class TextSlot(Slot):
    type_name = "text"

    def _as_features(self) -> List[float]:
        return [1.0 if self.value is not None else 0.0]


class ListSlot(Slot):
    type_name = "list"

    def _as_features(self) -> List[float]:
        try:
            if self.value is not None and len(self.value) > 0:
                return [1.0]
            else:
                return [0.0]
        except (TypeError, ValueError):
            # we couldn't convert the value to a list - using default value
            return [0.0]


class UnfeaturizedSlot(Slot):
    type_name = "unfeaturized"

    def __init__(
        self,
        name: Text,
        initial_value: Any = None,
        value_reset_delay: Optional[int] = None,
        auto_fill: bool = True,
        influence_conversation: bool = False,
    ) -> None:
        if influence_conversation:
            raise ValueError(
                f"An {UnfeaturizedSlot.__name__} cannot be featurized. "
                f"Please use a different slot type for slot '{name}' instead. See the "
                f"documentation for more information: {SLOT_DOCUMENTS_URL}"
            )

        convo.shared.utils.io.raising_warning(
            f"{UnfeaturizedSlot.__name__} is deprecated "
            f"and will be removed in Convo Open Source "
            f"3.0. Please change the type and configure the 'influence_conversation' "
            f"flag for slot '{name}' instead.",
            docs=SLOT_DOCUMENTS_URL,
            category=FutureWarning,
        )

        super().__init__(
            name, initial_value, value_reset_delay, auto_fill, influence_conversation
        )

    def _as_features(self) -> List[float]:
        return []

    def _feature_dimensions(self) -> int:
        return 0


class CategoricalSlot(Slot):
    type_name = "categorical"

    def __init__(
        self,
        name: Text,
        values: Optional[List[Any]] = None,
        initial_value: Any = None,
        value_reset_delay: Optional[int] = None,
        auto_fill: bool = True,
        influence_conversation: bool = True,
    ) -> None:
        super().__init__(
            name, initial_value, value_reset_delay, auto_fill, influence_conversation
        )
        self.values = [str(v).lower() for v in values] if values else []

    def adding_default_value(self) -> None:
        worth = set(self.values)
        if convo.shared.core.constants.DEFAULT_CATEGORY_SLOT_VALUE  not in worth:
            self.values.append(
                convo.shared.core.constants.DEFAULT_CATEGORY_SLOT_VALUE 
            )

    def persistence_information(self) -> Dict[Text, Any]:
        e = super().persistence_information()
        e["values"] = self.values
        return e

    def _as_features(self) -> List[float]:
        r = [0.0] * self.feature_dimensions()

        try:
            for i, v in enumerate(self.values):
                if v == str(self.value).lower():
                    r[i] = 1.0
                    break
            else:
                if self.value is not None:
                    if (
                        convo.shared.core.constants.DEFAULT_CATEGORY_SLOT_VALUE 
                        in self.values
                    ):
                        i = self.values.index(
                            convo.shared.core.constants.DEFAULT_CATEGORY_SLOT_VALUE 
                        )
                        r[i] = 1.0
                    else:
                        convo.shared.utils.io.raising_warning(
                            f"Categorical slot '{self.name}' is set to a value "
                            f"('{self.value}') "
                            "that is not specified in the domain. "
                            "Value will be ignored and the slot will "
                            "behave as if no value is set. "
                            "Make sure to add all values a categorical "
                            "slot should store to the domain."
                        )
        except (TypeError, ValueError):
            log.exception("Failed to featurize categorical slot.")
            return r
        return r

    def _feature_dimensions(self) -> int:
        return len(self.values)


class AnySlot(Slot):
    """Slot which can be used to store any value. Users need to create a subclass of
    `Slot` in case the information is supposed to get featurized."""

    type_name = "any"

    def __init__(
        self,
        name: Text,
        initial_value: Any = None,
        value_reset_delay: Optional[int] = None,
        auto_fill: bool = True,
        influence_conversation: bool = False,
    ) -> None:
        if influence_conversation:
            raise ValueError(
                f"An {AnySlot.__name__} cannot be featurized. "
                f"Please use a different slot type for slot '{name}' instead. If you "
                f"need to featurize a data type which is not supported out of the box, "
                f"implement a custom slot type by subclassing '{Slot.__name__}'. "
                f"See the documentation for more information: {SLOT_DOCUMENTS_URL}"
            )

        super().__init__(
            name, initial_value, value_reset_delay, auto_fill, influence_conversation
        )
