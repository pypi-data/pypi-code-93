from typing import List, Tuple, cast


class Register:
    """
    Registers are the main interaction point with the QLattice, IO interfaces.

    Users connect registers with their data concepts, columns in their dataset or stores.

    The constructor is for internal use. Registers should always be allocated with the `QLattice.registers.get()` method.

    Arguments:
        name -- Name of the register, so that you can find it again later. Usually the column name in your dataset, or the name of the concept this register represents.
        location -- Location in the QLattice.
    """

    def __init__(self, name: str, location: Tuple[int, int, int]):
        """Construct a new 'Register' object."""
        self.name = name
        self._latticeloc = location

    def __str__(self):
        return self.name


class RegisterCollection:
    """
    The RegisterCollection is used to find, create and delete registers from a QLattice.

    Before you can extract models from the QLattice, you need to allocate a register for each input feature and the output feature you want to predict.

    The registers serve as the input and output points into a QLattice and must be specified when extracting models from the QLattice.

    You can find an existing register (but not create it) using item access:
    >>> reg = qlattice.registers["somename"]

    Sometimes you want to create it if it doesnt already exist. That can be done using the get() method:
    >>> reg = qlattice.registers.get("somename", register_type="cat")

    Finally, you can get rid of unwanted registers using the del syntax:
    >>> del(qlattice.registers["out"])

    Or the delete function:
    >>> qlattice.registers.delete("out")

    """

    def __init__(self, qlattice):
        self.qlattice = qlattice
        self._http_client = qlattice._http_client

    def delete(self, name: str):
        """
        Delete a register from the QLattice.

        A QLattice has a limited number of registers avaiable. Adding registers beyond this limit will cause an error. You can use this funtion to remove unused registers from the QLattice to make room for new ones.

        The same can also be achieved using the more pythonic del() function, thus:
        >>> qlattice.registers.delete("somename")
        is equvalent to
        >>> del(qlattice.registers["somename"])

        Arguments:
            name -- Name of the register to delete

        """
        req = self._http_client.delete(f"/register/{name}")
        if req.status_code == 422:
            raise ValueError(req.text)
        req.raise_for_status()

    def __delitem__(self, name: str):
        self.delete(name)

    def __getitem__(self, name: str) -> Register:
        for reg in self:
            if reg.name == name:
                return reg

        raise KeyError(f"No register named {name}")

    def __len__(self):
        return len(self._get_register_list())

    def __iter__(self):
        return self._get_register_list().__iter__()

    def _get_register_list(self) -> List[Register]:
        resp = self._http_client.get("/register")
        resp.raise_for_status()

        registers = [self._register_from_json(s) for s in resp.json()]
        return registers

    def _register_from_json(self, json) -> Register:
        latticeloc = cast(Tuple[int, int, int], tuple(json["location"]))
        return Register(json["name"], latticeloc)
