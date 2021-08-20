""" Functions for matching :py:class:`~momotor.bundles.elements.result.Result` objects to conditions.

Conditions are strings that can for example be included in XML attributes and used to filter results.

Accepted conditions:

+----------------+----------------------------------------------------+
| ``pass``       | Match if outcome == `pass`                         |
+----------------+----------------------------------------------------+
| ``fail``       | Match if outcome == `fail`                         |
+----------------+----------------------------------------------------+
| ``error``      | Match if outcome == `error`                        |
+----------------+----------------------------------------------------+
| ``prop[x]``    | Match if property `x` is True                      |
+----------------+----------------------------------------------------+
| ``prop[x]?``   | Match if property `x` exists                       |
+----------------+----------------------------------------------------+
| ``prop[x]==0`` | Match if property `x` equals 0                     |
+----------------+----------------------------------------------------+
| ``prop[x]>0``  | Match if property `x` is greater than 0            |
+----------------+----------------------------------------------------+
| ``prop[x]>=0`` | Match if property `x` is greater than or equals 0  |
+----------------+----------------------------------------------------+
| ``prop[x]<0``  | Match if property `x` is less than 0               |
+----------------+----------------------------------------------------+
| ``prop[x]<=0`` | Match if property `x` is less than or equals 0     |
+----------------+----------------------------------------------------+

To invert the condition, prefix with `not-`:

+--------------------+----------------------------------------+
| ``not-pass``       | Match if outcome != `pass`             |
+--------------------+----------------------------------------+
| ``not-prop[x]==0`` | Match if property `x` does not equal 0 |
+--------------------+----------------------------------------+
"""

import re
import operator
import typing

from momotor.bundles.elements.result import Result, Outcome

PROP_SELECTOR_RE = re.compile(r"^prop\[([^]]+)\](\?|==|>=|>|<=|<)?(.*)$")


def parse_prop_selector(selector: str) -> typing.Optional[typing.Tuple[str, str, str]]:
    """
    Parse a property selector.

    Expected format is ``prop[`` `<name>` ``]`` [ `<condition>` [ `<value>` ] ], where

    * `<name>` is the property's name,
    * `<condition>` is one of ``?``, ``==``, ``<``, ``<=``, ``>``, ``>=``, and
    * `<value>` is the value to compare the property to

    If no `<condition>` and `<value>` are provided interprets the property as a boolean value. If `<condition>`
    is ``?``, it matches if the property exists. The other conditions compare the property to the value.

    :param selector: The selector to parse
    :return: A three-tuple with the `name`, `condition` and `value`

    >>> parse_prop_selector("prop[abc]")
    ('abc', None, '')

    >>> parse_prop_selector("prop[abc]?")
    ('abc', '?', '')

    >>> parse_prop_selector("prop[abc]==0")
    ('abc', '==', '0')

    >>> parse_prop_selector("prop[abc]==def ghi jkl")
    ('abc', '==', 'def ghi jkl')

    >>> parse_prop_selector("prop[abc]>0")
    ('abc', '>', '0')

    >>> parse_prop_selector("prop[abc]>=0")
    ('abc', '>=', '0')

    >>> parse_prop_selector("prop[abc]<0")
    ('abc', '<', '0')

    >>> parse_prop_selector("prop[abc]<=0")
    ('abc', '<=', '0')

    """
    m = PROP_SELECTOR_RE.match(selector)
    return m.groups() if m else m


# All operators and functions to check them
OPERATIONS = {
    None: lambda prop_value, value: bool(prop_value),
    '?': lambda prop_value, value: True,
    '==': operator.eq,
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le
}

# These operators should have no value
OPERATIONS_WITHOUT_VALUE = {None, '?'}


def _cast_num(value: typing.Optional[str]) -> typing.Union[int, float]:
    if value is None:
        raise TypeError

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass


def make_matcher_fn(condition: typing.Union[str, None]) -> typing.Callable[[Result], bool]:
    """ Make a step condition matcher function from a condition. Returns a callable that accepts a
    :py:class:`~momotor.bundles.elements.result.Result` and returns `True` if the condition matches the
    result, otherwise it returns `False`
    """

    if not condition:
        return lambda step_result: True

    if condition.startswith('not-'):
        base_condition, invert = condition[4:], True
    else:
        base_condition, invert = condition, False

    try:
        outcome = Outcome(base_condition)
    except ValueError:
        outcome = None

    if outcome:
        # Test on outcome
        def matcher(step_result):
            return step_result.outcome_enum == outcome

    elif base_condition.startswith('prop['):
        # Test on property value
        prop_name, operator_str, value = parse_prop_selector(base_condition)

        if operator_str in OPERATIONS_WITHOUT_VALUE:
            if value:
                raise ValueError("Invalid selector %r" % base_condition)
            value = None

        operator_fn = OPERATIONS.get(operator_str)
        if not operator_fn:
            raise ValueError("Invalid selector %r" % base_condition)

        try:
            value_num = _cast_num(value)
        except (ValueError, TypeError):
            # Match on string values only
            def matcher(step_result):
                try:
                    prop_value = step_result.get_property_value(prop_name)
                except KeyError:
                    return False

                try:
                    return operator_fn(prop_value, value)
                except TypeError:
                    return False
        else:
            def matcher(step_result):
                try:
                    prop_value = step_result.get_property_value(prop_name)
                except KeyError:
                    return False

                if isinstance(prop_value, str):
                    try:
                        prop_value = _cast_num(prop_value)
                    except ValueError:
                        pass

                try:
                    return operator_fn(prop_value, value_num)
                except TypeError:
                    try:
                        return operator_fn(prop_value, value)
                    except TypeError:
                        return False

    else:
        raise ValueError("Invalid condition %r" % base_condition)

    if invert:
        def inverted_matcher(step_result):
            return not matcher(step_result)

        return inverted_matcher

    return matcher


def match_result(condition: typing.Union[str, None], step_result: Result) -> bool:
    """ Match a :py:class:`~momotor.bundles.elements.result.Result` to a condition.

    Shortcut for ``make_matcher_fn(condition)(step_result)``

    Use :py:func:`make_matcher_fn` if multiple results need to be validated against the same condition.
    """
    return make_matcher_fn(condition)(step_result)
