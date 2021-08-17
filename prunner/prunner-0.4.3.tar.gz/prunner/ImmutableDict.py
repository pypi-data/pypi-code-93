from collections import UserDict


class ImmutableDict(UserDict):
    def update(self, update_dict) -> None:
        for k, v in update_dict.items():
            if k in self:
                print("WARNING: The variable is already defined. Ignoring:", k, "=>", v)
            else:
                self[k] = v
