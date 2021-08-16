import json
from pathlib import Path 
from typing import List, Optional
from abc import ABC, abstractmethod

class UnsetJsonLocation:
    
    @classmethod
    def err_msg(cls):
        return "Unset Json Location - require a path to the directory from which the json is supposed to be loaded"

class UnsetJsonLocationException(Exception):
    pass

class InvalidJsonLocationDirPathException(Exception):
    pass 

    
class IJsonRetriever(ABC):
    @abstractmethod
    def set_json_location_dir(self, json_location_dir: Path):
        pass

    @abstractmethod
    def get_json_location_dir(self) -> Path:
        pass
    
    @abstractmethod
    def load_json(name: str):
        pass 

class JsonRetriever(IJsonRetriever):

    def __init__(self, json_location_dir: Optional[Path] = UnsetJsonLocation) -> None:
        if not json_location_dir is UnsetJsonLocation:
            self._check_location_dir(json_location_dir)
        self._json_location_dir = json_location_dir
    
    def load_json(self, json_name: str):
        json_loc = self.get_json_location_dir()
        with open(json_loc.joinpath(json_name)) as f:
            return json.load(f)
    
    def get_json_location_dir(self) -> Path:
        self._check_unset_location_dir()
        return self._json_location_dir

    def set_json_location_dir(self, json_location_dir: Path):
        self._check_location_dir(json_location_dir)
        self._json_location_dir = json_location_dir

    def _check_location_dir(self, json_loc_dir):
        self._check_location_is_path(json_loc_dir)
        self._check_location_path_is_dir(json_loc_dir)

    def _check_location_is_path(self, json_loc_dir):
        if not isinstance(json_loc_dir, Path):
            error_msg_templ = "The given parameter {p} is not a Path instance"
            raise InvalidJsonLocationDirPathException(error_msg_templ.format(p = json_loc_dir))

    def _check_location_path_is_dir(self, json_loc_dir):
        if not json_loc_dir.is_dir():
            error_msg_templ = "The given path {p} does not correspond to a directory"
            raise InvalidJsonLocationDirPathException(error_msg_templ.format(p=json_loc_dir))

    def _check_unset_location_dir(self):
        if self._json_location_dir is UnsetJsonLocation:
            raise(UnsetJsonLocationException(UnsetJsonLocation.err_msg()))
    

        
class JsonSchemaRetrievalResponse:
    def __init__(self, schema: dict, store: List[dict]) -> None:
        self.schema = schema
        self.store = store
     

class JsonSchemaRetriever:
    SCHEMA_SUFFIX = "_schema.json"

    def __init__(self, json_retriever: IJsonRetriever = JsonRetriever()) -> None:
        self.json_retriever = json_retriever

    def set_schema_dir(self, schema_dir: Path):
        self.json_retriever.set_json_location_dir(schema_dir)

    def retrieve_schema(self, schema_name: str) -> JsonSchemaRetrievalResponse:
        safe_schema_name = self._safe_schema_name(schema_name)
        schema = self._load_schema(safe_schema_name)
        schema_loc_dir = self.json_retriever.get_json_location_dir()
        schema_store = {p.name : self._load_schema(p.name) for p in schema_loc_dir.iterdir() if self.is_schema_path(p)}
        return JsonSchemaRetrievalResponse(schema=schema, store=schema_store)

    def _load_schema(self, name: str):
       return self.json_retriever.load_json(name)
    
    @classmethod
    def is_schema_path(cls, path: Path):
        return path.is_file() and path.name.endswith(cls.SCHEMA_SUFFIX)

    @classmethod
    def _safe_schema_name(cls, schema_name: str) -> str:
        suffix_head, suffix_tail = cls.SCHEMA_SUFFIX.split(".")
        if schema_name.endswith(cls.SCHEMA_SUFFIX):
            return schema_name
        
        elif schema_name.endswith(suffix_tail):
            short_name, file_ext = schema_name.split(".")
            assert file_ext == suffix_tail
            full_name = short_name + suffix_head
            return ".".join([full_name, file_ext])
        
        elif schema_name.endswith(suffix_head):
            return ".".join([schema_name, suffix_tail])
        
        else:
            return schema_name + cls.SCHEMA_SUFFIX
