from collections import UserDict


class ImmutableDict(UserDict):
    def update(self, update_dict) -> None:
        for k, v in update_dict.items():
            if k in self:
                print(
                    f"WARNING: The variable `{k}` is already defined. Ignoring override value of:",
                    v,
                )
            else:
                self[k] = v
