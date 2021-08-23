from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from dp_json_util import JsonRetriever
from .base_db import BaseDB
from .base_config import BaseDBConfig, UnsetConfigProperty



class JsonFilledDBConfig(BaseDBConfig):
    json_fill_dir = UnsetConfigProperty
    instances_type_mapping: Dict[str, type] = UnsetConfigProperty


class JsonFilledDB(BaseDB):
    def __init__(self, db_config: JsonFilledDBConfig, Base: DeclarativeMeta) -> None:
        super().__init__(db_config, Base)
        self.json_retriever =  self._init_json_retriever(db_config)
        
    def _init_json_retriever(self, db_config: JsonFilledDBConfig) -> JsonRetriever:
        json_retriever = JsonRetriever()
        json_retriever.set_json_location_dir(db_config.json_fill_dir)
        return json_retriever

    def _populate_all_tables(self, session: Session):
        self.run_in_transaction_context(self.fill_all_types)

    def fill_all_types(self, session: Session):
        for instances_name, type_to_fill in self.config.instances_type_mapping.items():
            self._fill_type(session, instances_name, type_to_fill)

    def _fill_type(self, session: Session, instances_name: str, Fill_type: type):
        instances_json_name = instances_name + ".json"
        instances = self.json_retriever.load_json(instances_json_name)
        for instance in instances:
            session.add(Fill_type(**instance))


