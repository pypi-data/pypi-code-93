from typing import List

from sqlalchemy.orm import Query

from cytra.db.transform_mixin import TransformMixin
from cytra.db.access_control_mixin import AccessControlMixin


class SerializeMixin(TransformMixin, AccessControlMixin):
    def to_dict(self) -> dict:
        result = dict()
        for type_, key, info, c in self.__class__.get_readables(self.__app__):
            key = self.get_column_key(c)
            result.setdefault(
                self.export_column_name(key, info),
                self.export_value(c, getattr(self, key)),
            )
        return result

    def update_from_dict(self, data: dict) -> None:
        datakeys = data.keys()
        for type_, key, info, c in self.get_writables(self.__app__):
            key = self.get_column_key(c)
            key_ = self.export_column_name(key, info)
            if key_ not in datakeys:
                continue

            setattr(self, key, self.import_value(c, data[key_]))

    def update_from_request(self) -> None:
        self.update_from_dict(self.__app__.request.form)

    @classmethod
    def dump_query(cls, query: Query) -> List[dict]:
        """
        Dump query results in a list of model dictionaries.
        :param query:
        :return:
        """
        return [o.to_dict() for o in query]
