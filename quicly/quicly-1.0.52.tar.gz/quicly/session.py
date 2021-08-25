from typing import *

from quicly.mongodb import QxMongoModel, QxMongoClient
from bson import ObjectId


class QxSession(object):
  def __init__(self, session_id: str):
    self._session_id = session_id

  @property
  def session_id(self) -> str:
    return self._session_id

  def __enter__(self):
    self._load()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self._save()

  def _load(self):
    raise NotImplementedError()

  def _save(self):
    raise NotImplementedError()

  def get(self, name: str, default: Any = None) -> Any:
    raise NotImplementedError()

  def set(self, name: str, value: Any):
    raise NotImplementedError()

  def delete(self, name: str):
    raise NotImplementedError()

  def clear(self):
    raise NotImplementedError()


class QxMongoSession(QxSession):
  STATE_TO_LOAD = 0
  STATE_IS_LOADED = 1
  STATE_TO_CREATE = 2
  STATE_TO_UPDATE = 3
  STATE_TO_DELETE = 4
  STATE_DO_NOTHING = 5

  def __init__(self, model: QxMongoModel, session_id: str):
    super(QxMongoSession, self).__init__(session_id)
    self._model = model
    self._session_data = dict()
    self._state = self.STATE_TO_LOAD

  @property
  def model(self) -> QxMongoModel:
    return self._model

  def _load(self):
    if not isinstance(self._session_data, dict):
      self._session_data = dict()
    self._session_data.clear()
    self._state = self.STATE_TO_LOAD

  def _save(self):
    if self._state == self.STATE_TO_CREATE:
      self._session_data['_id'] = ObjectId(self.session_id)
      self.model.insert_item(self._session_data)
    elif self._state == self.STATE_TO_UPDATE:
      self.model.update_item_by_pk(ObjectId(self.session_id), {
        '$set': self._session_data,
      })
    elif self._state == self.STATE_TO_DELETE:
      self.model.delete_item_by_pk(ObjectId(self.session_id))

  def _lazy_load(self):
    if self._state == self.STATE_TO_LOAD:
      session_data = self.model.find_item_by_pk(ObjectId(self.session_id))
      if session_data:
        self._session_data = session_data
        self._state = self.STATE_IS_LOADED
      else:
        self._session_data = dict()
        self._state = self.STATE_TO_CREATE

    if not isinstance(self._session_data, dict):
      self._session_data = dict()

  def get(self, name: str, default: Any = None) -> Any:
    self._lazy_load()
    return self._session_data.get(name, default)

  def set(self, name: str, value: Any):
    self._lazy_load()
    if self._state in (self.STATE_TO_DELETE, self.STATE_DO_NOTHING):
      return
    self._session_data[name] = value
    if self._state == self.STATE_IS_LOADED:
      self._state = self.STATE_TO_UPDATE

  def delete(self, name: str):
    self._lazy_load()
    if self._state in (self.STATE_TO_DELETE, self.STATE_DO_NOTHING):
      return
    del self._session_data[name]
    if self._state == self.STATE_IS_LOADED:
      self._state = self.STATE_TO_UPDATE

  def clear(self):
    self._lazy_load()
    if self._state == self.STATE_TO_CREATE:
      self._state = self.STATE_DO_NOTHING
    else:
      self._state = self.STATE_TO_DELETE

################################################################################


class QxSessionFactory(object):
  def __init__(self):
    pass

  def new_session_id(self):
    raise NotImplementedError()

  def init_session(self):
    raise NotImplementedError()

  def load_session(self, session_id: str):
    raise NotImplementedError()


class QxMongoSessionFactory(QxSessionFactory):
  def __init__(self, db: Union[QxMongoModel, QxMongoClient]):
    super(QxMongoSessionFactory, self).__init__()
    if isinstance(db, QxMongoModel):
      self._db = db.mongo_client
      self._model = db
    else:
      self._db = db
      self._model = QxMongoModel(db, 'sessions', raw_delete=True)

  @property
  def db(self) -> QxMongoClient:
    return self._db

  @property
  def model(self) -> QxMongoModel:
    return self._model

  def new_session_id(self):
    return str(ObjectId())

  def init_session(self):
    names = self.db.collection_names(include_system_collections=False)
    if self.model.collection_name not in names:
      self.db.create_collection(self.model.collection_name)

  def load_session(self, session_id: str):
    return QxMongoSession(self.model, session_id)
