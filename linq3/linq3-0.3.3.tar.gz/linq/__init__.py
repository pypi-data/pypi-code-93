__version__ = '0.3.3'


import itertools
from collections import defaultdict
from typing import Iterable, TypeVar, List, Set, Optional, Callable, Dict, Any


T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')
TKey = TypeVar('TKey')
TValue = TypeVar('TValue')


class InvalidOperationException(Exception):
    pass


class linq(Iterable[T]):
    """
    NB: No cache! One linq can only be used once.
    """
    def __init__(self, data: Iterable[T]):
        self._data = data
        self._indexable = isinstance(self._data, (list, tuple, str, dict, bytes))

    def __iter__(self):
        """
        should override in subclasses if you want to support lazy evaluation.
        1. assign self._data
        2. return super(Subclass, self).__iter__()
        :return:
        """
        return self._data.__iter__()

    # as itertools doesn't provide this, I don't think we need to provide it either.
    # def close(self):
    #     iterable_close = getattr(self._data, 'close', None)
    #     if iterable_close:
    #         self._data.close()

    def __repr__(self):  # should override in subclasses if you want to support lazy evaluation.
        return self._data.__repr__()

    def count(self, pred_func: Optional[Callable[[T], bool]] = None) -> int:
        if pred_func is None:
            if self._indexable:
                return len(self._data)
            return sum(1 for _ in self)
        else:
            return self.where(pred_func).count()

    def to_list(self) -> List[T]:
        return list(self)

    def to_dict(self, key_func: Callable[[T], TKey],
                value_func: Optional[Callable[[T], TValue]] = None) \
            -> Dict[TKey, TValue]:
        if value_func is None:
            value_func = linq._identity_map
        ret = {}
        for element in self:
            ret[key_func(element)] = value_func(element)
        return ret

    def to_set(self) -> Set[T]:
        return set(self)

    def to_lookup(self, key_func: Callable[[T], TKey]) -> Dict[TKey, List[T]]:
        lookup = defaultdict(list)
        for element in self:
            lookup[key_func(element)].append(element)
        return lookup

    def element_at(self, n: int) -> T:
        if n < 0:
            raise IndexError
        if self._indexable:
            if len(self._data) > n:
                return self._data[n]
            else:
                raise IndexError
        for index, element in enumerate(self):
            if index == n:
                return element
        raise IndexError

    def element_at_or_default(self, n: int, default: Optional[T] = None) -> Optional[T]:
        if n < 0:
            raise IndexError
        if self._indexable:
            if len(self._data) > n:
                return self._data[n]
            else:
                return default
        for index, element in enumerate(self):
            if index == n:
                return element
        return default

    def first(self, pred_func: Optional[Callable[[T], bool]] = None) -> T:
        if pred_func:
            return self.where(pred_func).first()
        for element in self:
            return element
        raise InvalidOperationException

    def first_or_default(self, pred_func: Optional[Callable[[T], bool]] = None,
                         *, default: Optional[T] = None) -> Optional[T]:
        if pred_func:
            return self.where(pred_func).first_or_default(default=default)
        for element in self:
            return element
        return default

    def single(self, pred_func: Optional[Callable[[T], bool]] = None) -> T:
        if pred_func:
            return self.where(pred_func).single()
        found = False
        first_element = None
        for element in self:
            if not found:
                found = True
                first_element = element
            else:
                raise InvalidOperationException
        if not found:
            raise InvalidOperationException
        return first_element

    def single_or_default(self, pred_func: Optional[Callable[[T], bool]] = None,
                          *, default: Optional[T] = None) -> Optional[T]:
        if pred_func:
            return self.where(pred_func).single_or_default(default=default)
        found = False
        first_element = default
        for element in self:
            if not found:
                found = True
                first_element = element
            else:
                raise InvalidOperationException
        return first_element

    def last(self, pred_func: Optional[Callable[[T], bool]] = None) -> T:
        if self._indexable:
            if pred_func is None:
                if len(self._data) > 0:  # pylint: disable=len-as-condition
                    return self._data[len(self._data) - 1]
                else:
                    raise InvalidOperationException
            else:
                for element in reversed(self._data):
                    if pred_func(element):
                        return element
                raise InvalidOperationException

        if pred_func:
            return self.where(pred_func).last()

        last_element = None
        found = False
        for element in self:
            last_element = element
            found = True
        if not found:
            raise InvalidOperationException
        return last_element

    def last_or_default(self, pred_func: Optional[Callable[[T], bool]] = None,
                        *, default: Optional[T] = None) -> Optional[T]:
        try:
            return self.last(pred_func)
        except InvalidOperationException:
            return default

    def sum(self, select_func: Optional[Callable[[T], U]] = None) -> U:
        if select_func is None:
            select_func = linq._identity_map
        return sum(select_func(x) for x in self)

    def aggregate(self, seed: U, accumulate_func: Callable[[U, U], U]) -> U:
        value = seed
        for element in self:
            value = accumulate_func(value, element)
        return value

    def max(self, select_func: Optional[Callable[[T], U]] = None) -> U:
        if select_func is None:
            select_func = linq._identity_map
        found = False
        max_value = None
        for element in self:
            if not found:
                found = True
                max_value = select_func(element)
            else:
                max_value = max(max_value, select_func(element))
        if not found:
            raise InvalidOperationException
        return max_value

    def argmax(self, select_func: Optional[Callable[[T], U]] = None) -> int:
        if select_func is None:
            select_func = linq._identity_map
        found = False
        max_value = None
        max_origin = None
        for element in self:
            if not found:
                found = True
                max_value = select_func(element)
                max_origin = element
            else:
                new_value = select_func(element)
                if new_value > max_value:
                    max_value = new_value
                    max_origin = element
        if not found:
            raise InvalidOperationException
        return max_origin

    def min(self, select_func: Optional[Callable[[T], U]] = None) -> U:
        if select_func is None:
            select_func = linq._identity_map
        found = False
        min_value = None
        for element in self:
            if not found:
                found = True
                min_value = select_func(element)
            else:
                min_value = min(min_value, select_func(element))
        if not found:
            raise InvalidOperationException
        return min_value

    def argmin(self, select_func: Optional[Callable[[T], U]] = None) -> int:
        if select_func is None:
            select_func = linq._identity_map
        found = False
        min_value = None
        min_origin = None
        for element in self:
            if not found:
                found = True
                min_value = select_func(element)
                min_origin = element
            else:
                new_value = select_func(element)
                if new_value < min_value:
                    min_value = new_value
                    min_origin = element
        if not found:
            raise InvalidOperationException
        return min_origin

    def all(self, pred_func: Optional[Callable[[T], bool]] = None) -> bool:
        if pred_func:
            return all(self.select(pred_func))
        return all(self)

    def any(self, pred_func: Optional[Callable[[T], bool]] = None) -> bool:
        if pred_func:
            return any(self.select(pred_func))
        return any(self)

    def contains(self, element: T) -> bool:
        return self.any(lambda e: e == element)

    def sequence_equal(self, iterable: Iterable[T]) -> bool:
        sentinel = object()
        for combo in itertools.zip_longest(self, iterable, fillvalue=sentinel):
            if sentinel in combo:
                return False
            if combo[0] != combo[1]:
                return False
        return True

    def add(self, element: T) -> 'linq[T]':
        return self.concat([element])

    def append(self, element: T) -> 'linq[T]':
        return self.add(element)

    def prepend(self, element):
        return linq([element]).concat(self)

    def concat(self, iterable: Iterable[T]) -> 'linq[T]':
        return linq(itertools.chain(self, iterable))

    def select(self, select_func: Callable[[T], U]) -> 'linq[U]':
        return linq(map(select_func, self))

    def select_with_index(self, select_func: Callable[[int, T], U]) -> 'linq[U]':
        return linq(map(select_func, itertools.count(), self))

    def select_many(self, select_func: Callable[[T], Iterable[U]]) -> 'linq[U]':
        return linq(itertools.chain.from_iterable(self.select(select_func)))

    def select_many_with_index(self, select_func: Callable[[int, T], Iterable[U]]) -> 'linq[U]':
        return linq(itertools.chain.from_iterable(self.select_with_index(select_func)))

    def where(self, pred_func: Callable[[T], bool]) -> 'linq[T]':
        return linq(filter(pred_func, self))

    def skip(self, n: int) -> 'linq[T]':
        return linq(itertools.islice(self, n, None, 1))

    def skip_while(self, pred_func: Callable[[T], bool]) -> 'linq[T]':
        return linq(itertools.dropwhile(pred_func, self))

    def take(self, n: int) -> 'linq[T]':
        return linq(itertools.islice(self, n))

    def take_while(self, pred_func: Callable[[T], bool]) -> 'linq[T]':
        return linq(itertools.takewhile(pred_func, self))

    def reverse(self) -> 'linq[T]':
        return _ReverseHelper(self)

    def order_by(self, key_func: Callable[[T], TKey]) -> '_OrderHelper':
        return _OrderHelper(self, _OrderFunc(key_func, False))

    def order_by_descending(self, key_func: Callable[[T], TKey]) -> '_OrderHelper':
        return _OrderHelper(self, _OrderFunc(key_func, True))

    def group_by(self, key_func: Callable[[T], TKey]) -> 'linq[_Group]':
        return _GroupHelper(self, key_func)

    def intersect(self, iterable: Iterable[T]) -> 'linq[T]':
        return _IntersectionHelper(self, iterable)

    def union(self, iterable: Iterable[T]) -> 'linq[T]':
        return _UnionHelper(self, iterable)

    def except_(self, iterable: Iterable[T]) -> 'linq[T]':
        return _ExceptHelper(self, iterable)

    def difference(self, iterable: Iterable[T]) -> 'linq[T]':
        return self.except_(iterable)

    def distinct(self, key_func: Callable[[T], TKey] = None) -> 'linq[T]':
        if key_func is None:
            return linq(set(self))
        return self.group_by(key_func).select(lambda e: e.first())

    def zip(self, iterable: Iterable[U],
            result_select_func: Optional[Callable[[T, U], V]] = None) -> 'linq[V]':
        """
        For unequal length input, the unmatched values will be ignored from the longer iterable.
        if result_select_func is None, return results as tuple
        """
        if result_select_func is None:
            return linq(zip(self, iterable))
        else:
            return linq(zip(self, iterable)).select(lambda v: result_select_func(*v))

    @classmethod
    def empty(cls) -> 'linq':
        return linq([])

    @classmethod
    def repeat(cls, element: T, n: int) -> 'linq[T]':
        return linq(itertools.repeat(element, n))

    @classmethod
    def range(cls, start: int, count: int) -> 'linq[int]':
        return linq(range(start, start + count))

    @staticmethod
    def _identity_map(x):
        return x


class _ReverseHelper(linq):
    def __init__(self, data):
        super(_ReverseHelper, self).__init__(data)
        self._indexable = False

    def __iter__(self):
        new_data = list(self._data)
        self._data = reversed(new_data)
        return super(_ReverseHelper, self).__iter__()

    def __repr__(self):
        return '<_ReverseHelper for ' + super(_ReverseHelper, self).__repr__() + '>'


class _OrderFunc(object):
    def __init__(self, key_func, descending):
        self.key_func = key_func
        self.descending = descending


class _OrderHelper(linq):
    def __init__(self, data, order_func):
        """
        :param data:
        :type order_func: _OrderFunc
        """
        super(_OrderHelper, self).__init__(data)
        self._order_funcs = [order_func]
        self._indexable = False

    def __repr__(self):
        return '<_OrderHelper for ' + super(_OrderHelper, self).__repr__() + '>'

    def __iter__(self):
        for order_func in reversed(self._order_funcs):
            self._data = sorted(self._data, key=order_func.key_func, reverse=order_func.descending)
        return super(_OrderHelper, self).__iter__()

    def then_by(self, key_func):
        self._order_funcs.append(_OrderFunc(key_func, False))
        return self

    def then_by_descending(self, key_func):
        self._order_funcs.append(_OrderFunc(key_func, True))
        return self


class _Group(linq):
    def __init__(self, key, values):
        self.key = key
        super(_Group, self).__init__(values)

    def __repr__(self):
        return "<_Group for key={}, values={}>".format(repr(self.key), super(_Group, self).__repr__())


class _GroupHelper(linq):
    def __init__(self, data, key_func):
        super(_GroupHelper, self).__init__(data)
        self._indexable = False
        self._key_func = key_func

    def __repr__(self):
        return '<_GroupHelper for ' + super(_GroupHelper, self).__repr__() + '>'

    def __iter__(self):
        new_data = defaultdict(list)
        for element in self._data:
            new_data[self._key_func(element)].append(element)
        self._data = (_Group(key, values) for key, values in new_data.items())
        return super(_GroupHelper, self).__iter__()


class _IntersectionHelper(linq):
    def __init__(self, data1, data2):
        super(_IntersectionHelper, self).__init__(data1)
        self._indexable = False
        self._data2 = data2

    def __iter__(self):
        new_data = set(self._data)
        new_data.intersection_update(self._data2)
        self._data = new_data
        return super(_IntersectionHelper, self).__iter__()

    def __repr__(self):
        return "<_IntersectionHelper for {} and {}>".format(
            super(_IntersectionHelper, self).__repr__(),
            repr(self._data2))


class _UnionHelper(linq):
    def __init__(self, data1, data2):
        super(_UnionHelper, self).__init__(data1)
        self._indexable = False
        self._data2 = data2

    def __iter__(self):
        new_data = set(self._data)
        new_data.update(self._data2)
        self._data = new_data
        return super(_UnionHelper, self).__iter__()

    def __repr__(self):
        return "<_UnionHelper for {} and {}>".format(
            super(_UnionHelper, self).__repr__(),
            repr(self._data2))


class _ExceptHelper(linq):
    def __init__(self, data1, data2):
        super(_ExceptHelper, self).__init__(data1)
        self._indexable = False
        self._data2 = data2

    def __iter__(self):
        new_data = set(self._data)
        new_data.difference_update(self._data2)
        self._data = new_data
        return super(_ExceptHelper, self).__iter__()

    def __repr__(self):
        return "<_ExceptHelper for {} and {}>".format(
            super(_ExceptHelper, self).__repr__(),
            repr(self._data2))
