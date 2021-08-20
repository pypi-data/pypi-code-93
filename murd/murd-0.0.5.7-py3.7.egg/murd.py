import json
from collections.abc import Iterable


group_sort_sep = "|||||"
group_key = "GROUP"
sort_key = "SORT"


def is_iterable(thing):
    return isinstance(thing, Iterable) and not isinstance(thing, str)


class M_management:
    """ A class for M data management """
    @classmethod
    def M(cls, **kwargs):
        """ Serialize a M item """
        kwargs = {"GROUP": "MISC", "SORT": "_", **kwargs}
        return kwargs

    @classmethod
    def prime_ms(cls, ms: list) -> dict:
        """ Marshall a M list into the Murd storage dictionary """
        return {cls.m_to_key(m): cls.M(**m) for m in ms}

    @classmethod
    def m_to_key(cls, m) -> str:
        """ Use a Murd item to create a Murd store key """
        m = cls.M(**m)
        return "{}{}{}".format(m[group_key], group_sort_sep, m[sort_key])

    @classmethod
    def group_sort_to_key(cls, group, sort):
        """ Format a group and a sort value into a Murd store key """
        return "{}{}{}".format(group, group_sort_sep, sort)


class Murd_json_file:
    def open_murd(self, filepath, murd=None):
        """ Open Murd store from file """
        murd = murd or self.default_murd_name
        if murd == self.default_murd_name:
            with open(filepath, "r") as f:
                self.matrix = json.dumps(json.loads(f.read()))
        else:
            self.murds[murd] = Murd(filepath)
            self.murds[murd].default_murd_name = murd

    def write_murd(self, filepath, murd=None):
        """ Write Murd store out to file """
        if murd is not None:
            self.murds[murd].write_murd(filepath)
        else:
            with open(filepath, "w") as f:
                f.write(json.dumps(json.loads(self.matrix), indent=4))

    def clear_murd(self, murd=None):
        """ Reset murd to an empty store """
        murd = murd or self.default_murd_name
        if type(murd) is str:
            self.murds[murd].clear_murd(self.murds[murd])
        else:
            murd.matrix = r'{}'


class Murd(M_management, Murd_json_file):
    def __init__(self, filepath=None, default_murd_name='0'):
        self.default_murd_name = default_murd_name
        self.murds = {self.default_murd_name: self}
        self.clear_murd()
        if filepath:
            self.open_murd(filepath)

    def update_data(self, ms):
        primed_ms = self.prime_ms(ms)
        murd = json.loads(self.matrix)
        murd = {**murd, **primed_ms}
        self.matrix = json.dumps(murd)

    def update(self, ms, murd=None):
        """ Create or modify an item in the Murd store """
        if is_iterable(murd):
            arg_sets = [dict(
                ms=ms,
                murd=murd_key
            ) for murd_key in murd]
            for arg_set in arg_sets:
                self.update(**arg_set)
        elif type(murd) is str:
            return self.murds[murd].update(ms)
        else:
            self.update_data(ms)

    def read_data(
        self,
        group,
        sort=None,
        min_sort=None,
        max_sort=None,
        limit=None,
        ascending_order=False
    ):
        loaded_murd = json.loads(self.matrix)

        matched = [key for key in loaded_murd.keys() if key[:len(group)] == group]

        if sort is not None:
            prefix = "{}{}{}".format(group, group_sort_sep, sort)
            matched = [key for key in matched if prefix in key]

        if min_sort is not None:
            minimum = self.group_sort_to_key(group, min_sort)
            matched = [key for key in matched if key > minimum]

        if max_sort is not None:
            maximum = self.group_sort_to_key(group, max_sort)
            matched = [key for key in matched if key < maximum]

        results = [self.M(**loaded_murd[key]) for key in matched]

        results = sorted(results, reverse=not ascending_order, key=lambda x: x['SORT'])

        if limit is not None:
            results = results[:limit]

        return results

    def read(
        self,
        group,
        sort=None,
        min_sort=None,
        max_sort=None,
        limit=None,
        ascending_order=False,
        murd=None
    ):
        """ Read items from the Murd store """
        if is_iterable(group):
            groups = group
            arg_sets = [dict(
                group=group,
                sort=sort,
                min_sort=min_sort,
                max_sort=max_sort,
                limit=limit,
                ascending_order=ascending_order,
                murd=murd
            ) for group in groups]

            results = [self.read(**arg_set) for arg_set in arg_sets]
            return [self.M(**m) for ms in results for m in ms]
        
        print(murd)
        if murd is None or is_iterable(murd):
            murds = self.murds.keys() if murd is None else murd
            arg_sets = [dict(
                group=group,
                sort=sort,
                min_sort=min_sort,
                max_sort=max_sort,
                limit=limit,
                ascending_order=ascending_order,
                murd=murd
            ) for murd in murds]
            results = [self.read(arg_set) for arg_set in arg_sets]
            return [self.M(**m) for ms in results for m in ms]
        elif murd != self.default_murd_name:
            return self.murds[murd].read(**dict(
                group=group,
                sort=sort,
                min_sort=min_sort,
                max_sort=max_sort,
                limit=limit,
                ascending_order=ascending_order,
                murd=murd
            ))

        return self.read_data(**dict(
            group=group,
            sort=sort,
            min_sort=min_sort,
            max_sort=max_sort,
            limit=limit,
            ascending_order=ascending_order
        ))

    def read_first(
        self,
        group,
        sort=None,
        min_sort=None,
        max_sort=None,
        limit=None,
        ascending_order=False,
        murd=None
    ):
        """ Utility method to simply return first result """
        try:
            return self.read(group, sort, min_sort, max_sort, limit, ascending_order, murd)[0]
        except IndexError:
            raise KeyError(f"No results")

    def delete_data(self, ms):
        murd = json.loads(self.matrix)
        primed_ms = self.prime_ms(ms)

        for key in primed_ms.keys():
            try:
                murd.pop(key)
            except KeyError:
                pass

        self.matrix = json.dumps(murd)

    def delete(self, ms, murd=None):
        """ Delete one or more items from the Murd store """
        if is_iterable(murd):
            arg_sets = [dict(
                ms=ms,
                murd=murd
            ) for murd in murd]

            [self.delete(**arg_set) for arg_set in arg_set]
        elif type(murd) is str:
            self.murds[murd].delete(ms)
        else:
            self.delete_data(ms)
