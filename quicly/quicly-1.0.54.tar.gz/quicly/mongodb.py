import re
from typing import *

import uuid
import random
import pymongo
import pymongo.database
import pymongo.results
from bson import ObjectId
from datetime import datetime
from collections import OrderedDict


class QxMongoClient(object):
  def __init__(
      self,
      host: Union[str, pymongo.MongoClient] = '127.0.0.1',
      port: int = 27017,
      username: Optional[str] = None,
      password: Optional[str] = None,
      database: str = 'admin',
      current_time: Optional[datetime] = None
  ):
    if isinstance(host, str):
      if '://' in host:
        py_mongo_client = QxMongoClient.create_py_mongo_client_from_url(host)
      else:
        py_mongo_client = QxMongoClient.create_py_mongo_client(host, port, username, password)
    else:
      assert isinstance(host, pymongo.MongoClient)
      py_mongo_client = host

    self._mongo_client = py_mongo_client
    self._mongo_db = py_mongo_client.get_database(database)
    self._current_time = current_time

  @staticmethod
  def create_py_mongo_client(host='127.0.0.1', port=27017, username=None, password=None):
    return pymongo.MongoClient(
      host=host,
      port=port,
      username=username,
      password=password,
    )

  @staticmethod
  def create_py_mongo_client_from_url(url='mongodb://127.0.0.1:27017/admin'):
    return pymongo.MongoClient(url)

  @property
  def mongo_client(self) -> pymongo.MongoClient:
    return self._mongo_client

  @property
  def db(self) -> pymongo.database:
    return self._mongo_db

  @property
  def mongo_db(self):
    return self._mongo_db

  @property
  def current_time(self) -> datetime:
    return self._current_time if isinstance(self._current_time, datetime) else datetime.now()

  @current_time.setter
  def current_time(self, v):
    self._current_time = v

  @staticmethod
  def _preprocess_sort(sort: Optional[Union[Tuple, List, OrderedDict]]):
    items = []
    if isinstance(sort, (tuple, list)):
      if len(sort) == 2 and isinstance(sort[0], str) and sort[1] in [1, -1]:
        items = [tuple(sort)]
      else:
        for item in sort:
          if isinstance(item, (tuple, list)) and len(item) == 2 and isinstance(item[0], str) and item[1] in [1, -1]:
            items.append(tuple(item))
    elif isinstance(sort, OrderedDict):
      for (k, v) in sort.items():
        if isinstance(k, str) and v in [1, -1]:
          items.append((k, v))

    items = items if len(items) else None
    return items

  @staticmethod
  def is_object_id(object_id: Union[ObjectId, str, uuid.UUID], strict: bool = False):
    ret = False
    if isinstance(object_id, ObjectId) or (isinstance(object_id, str) and re.match(r'[0-9a-f]{24}', object_id)):
      ret = True
    elif not strict and (isinstance(str, uuid.UUID) or (isinstance(object_id, str) and re.match(r'[0-9a-f]{24}', object_id.replace('-', '')))):
      ret = True
    return ret

  @staticmethod
  def make_object_id(object_id: Union[ObjectId, str, uuid.UUID]):
    if not isinstance(object_id, ObjectId):
      object_id = ObjectId(str(object_id).replace('-', ''))
    return object_id

  def get_collection(self, name: str) -> pymongo.collection.Collection:
    return self.db.get_collection(name)

  def aggregate(self, collection_name: str, pipeline: Union[Dict, List[Dict]]) -> List[Dict]:
    items = []
    cursor = self.get_collection(collection_name).aggregate(pipeline)
    for item in cursor:
      items.append(item)
    return items

  def aggregate_one(self, collection_name: str, pipeline: Dict) -> Optional[Dict]:
    cursor = self.get_collection(collection_name).aggregate(pipeline)
    for item in cursor:
      return item
    return None

  def count(self, collection_name: str, filter: Optional[Dict] = None) -> int:
    return self.get_collection(collection_name).count_documents(filter)

  def exists(self, collection_name: str, filter: Optional[Dict] = None) -> bool:
    return bool(self.get_collection(collection_name).find_one(filter))

  def find_one(self, collection_name: str, filter: Optional[Dict] = None, sort: Optional[Union[Tuple, List, OrderedDict]] = None, projection: Optional[Dict] = None, fn_process_item: Optional[Callable] = None) -> Optional[Dict]:
    sort = self._preprocess_sort(sort)

    item = self.get_collection(collection_name).find_one(filter, sort=sort, projection=projection)
    if callable(fn_process_item) and item:
      item = fn_process_item(item)

    return item

  def find_many(self, collection_name: str, filter: Optional[Dict] = None, sort: Optional[Union[Tuple, List, OrderedDict]] = None, skip: Optional[int] = None, limit: Optional[int] = None, projection: Optional[Dict] = None, fn_process_item: Optional[Callable] = None) -> List[Dict]:
    sort = self._preprocess_sort(sort)

    items = []
    if (isinstance(limit, int) and limit > 0) or limit is None:
      kw = dict()
      if sort:
        kw['sort'] = sort
      if isinstance(skip, int):
        kw['skip'] = skip
      if isinstance(limit, int):
        kw['limit'] = limit
      if projection:
        kw['projection'] = projection
      cursor = self.get_collection(collection_name).find(filter, **kw)
      if callable(fn_process_item):
        items = [fn_process_item(item) for item in cursor]
      else:
        items = [item for item in cursor]

    return items

  def find_one_random(self, collection_name: str, filter: Optional[Dict] = None, projection: Optional[Dict] = None, fn_process_item: Optional[Callable] = None) -> Optional[Dict]:
    kw = dict()
    if projection:
      kw['projection'] = projection

    cursor = self.get_collection(collection_name).find(filter, **kw)

    item = None

    total = cursor.count()
    if total > 0:
      index = random.randint(0, max(total, 999999)) % total
      cursor.skip(index)
      item = cursor.next()

      if callable(fn_process_item) and item:
        item = fn_process_item(item)

    return item

  def insert_one(self, collection_name: str, document: Dict) -> pymongo.results.InsertOneResult:
    return self.get_collection(collection_name).insert_one(document)

  def insert_many(self, collection_name: str, documents: List[Dict]) -> pymongo.results.InsertManyResult:
    return self.get_collection(collection_name).insert_many(documents)

  def delete_one(self, collection_name: str, filter: Optional[Dict]) -> pymongo.results.DeleteResult:
    return self.get_collection(collection_name).delete_one(filter)

  def delete_many(self, collection_name: str, filter: Optional[Dict]) -> pymongo.results.DeleteResult:
    return self.get_collection(collection_name).delete_many(filter)

  def update_one(self, collection_name: str, filter: Optional[Dict], update: Dict, upsert: bool = False) -> pymongo.results.UpdateResult:
    return self.get_collection(collection_name).update_one(filter, update, upsert)

  def update_one_and_return_it(self, collection_name: str, filter: Optional[Dict], update: Dict, upsert: bool = False) -> Optional[Dict]:
    result = self.update_one(collection_name, filter, update, upsert)
    if upsert and result.upserted_id:
      return self.find_one(collection_name, {
        '_id': result.upserted_id
      })
    return self.find_one(collection_name, filter)

  def update_many(self, collection_name: str, filter: Optional[Dict], update: Dict, upsert: bool = False) -> pymongo.results.UpdateResult:
    return self.get_collection(collection_name).update_many(filter, update, upsert)

  def find_one_and_delete(self, collection_name: str, filter:  Optional[Dict], projection: Optional[Dict] = None, sort: Optional[Union[Tuple, List, OrderedDict]] = None, fn_process_item: Optional[Callable] = None) -> Optional[Dict]:
    sort = self._preprocess_sort(sort)

    item = self.get_collection(collection_name).find_one_and_delete(filter, projection, sort)
    if callable(fn_process_item) and item:
      item = fn_process_item(item)
    return item

  def find_one_and_replace(self, collection_name: str, filter:  Optional[Dict], replacement: Dict, projection: Optional[Dict] = None, sort: Optional[Union[Tuple, List, OrderedDict]] = None, upsert: bool = False, return_document: bool = False, fn_process_item: Optional[Callable] = None) -> Optional[Dict]:
    sort = self._preprocess_sort(sort)

    item = self.db.get_collection(collection_name).find_one_and_replace(filter, replacement, projection, sort, upsert, return_document)
    if callable(fn_process_item) and item:
      item = fn_process_item(item)
    return item

  def find_one_and_update(self, collection_name: str, filter:  Optional[Dict], update: Dict, projection: Optional[Dict] = None, sort: Optional[Union[Tuple, List, OrderedDict]] = None, upsert: bool = False, return_document: bool = False, fn_process_item: Optional[Callable] = None) -> Optional[Dict]:
    sort = self._preprocess_sort(sort)

    item = self.db.get_collection(collection_name).find_one_and_update(filter, update, projection, sort, upsert, return_document)
    if callable(fn_process_item) and item:
      item = fn_process_item(item)
    return item

  def find_many_with_page_info(self, collection_name: str, filter=None, sort=None, skip=None, limit=None, projection=None, page_info=None, fn_process_item=None, fn_process_sort=None) -> Tuple[List[Dict], Dict]:
    filter = dict() if filter is None else filter
    sort = self._preprocess_sort(sort)

    page_info = page_info if isinstance(page_info, dict) else dict()

    total = page_info.get('total', None)
    page_num = page_info.get('page_num', None)
    next_index = page_info.get('next_index', 0)
    cut_off_time = page_info.get('cut_off_time', self.current_time)

    filter = filter.copy()
    if '_id' in filter:
      filter['_id'] = {
        '$and': [
          {'$lte': ObjectId.from_datetime(cut_off_time)},
          filter['_id'],
        ]
      }
    else:
      filter['_id'] = {'$lte': ObjectId.from_datetime(cut_off_time)}

    if total is None:
      total = self.count(collection_name, filter=filter)

    if sort and callable(fn_process_sort):
      sort_t = fn_process_sort(sort)
    else:
      sort_t = sort

    if not isinstance(skip, int):
      skip = 0

    items = self.find_many(collection_name, filter=filter, sort=sort_t, skip=next_index + skip, limit=limit, projection=projection)

    page_num = 0 if page_num is None else page_num + 1
    from_index = next_index + skip
    next_index = next_index + skip + len(items)
    has_more = next_index < total

    page_info = dict(
      total=total,
      limit=limit,
      page_num=page_num,
      from_index=from_index,
      next_index=next_index,
      cut_off_time=cut_off_time,
      has_more=has_more,
    )

    if callable(fn_process_item) and items:
      for i in range(len(items)):
        items[i] = fn_process_item(items[i])

    return items, page_info

  def collection_names(self, include_system_collections: bool = True) -> List[str]:
    return self.db.collection_names(include_system_collections)

  def create_collection(self, name: str) -> pymongo.collection.Collection:
    return self.db.create_collection(name)

  def exists_collection(self, name: str) -> bool:
    return name in self.collection_names(False)

  def create_index(self, collection_name: str, index_name: str, keys: List[Dict], **kw):
    return self.get_collection(collection_name).create_index(keys, name=index_name, **kw)

  def delete_index(self, collection_name: str, index_name: str):
    return self.get_collection(collection_name).drop_index(index_or_name=index_name)

################################################################################


class QxMongoModel(object):
  def __init__(self, mongo_client: QxMongoClient, collection_name: str, pk_name: str = '_id', ex_field_names: Optional[Dict] = None, raw_delete: bool = True):
    self._mongo_client = mongo_client
    self._collection_name = collection_name
    self._pk_name = pk_name
    self._ex_field_names = QxMongoModel._process_ex_field_names(ex_field_names)
    self._raw_delete = raw_delete

  def _make_pk_value(self, pk_value: Any) -> Any:
    if self._pk_name == '_id' and QxMongoClient.is_object_id(pk_value):
      pk_value = QxMongoClient.make_object_id(pk_value)
    return pk_value

  @staticmethod
  def _process_ex_field_names(d: Optional[Dict]) -> Dict:
    ret = d if isinstance(d, dict) else dict()
    ret.setdefault('created_time', 'created_time')
    ret.setdefault('updated_time', 'updated_time')
    ret.setdefault('is_deleted', '__is_deleted__')
    return ret

  @property
  def mongo_client(self) -> QxMongoClient:
    return self._mongo_client

  @property
  def collection_name(self) -> str:
    return self._collection_name

  @property
  def ex_field_created_time(self) -> str:
    return self._ex_field_names.get('created_time', 'created_time')

  @property
  def ex_field_updated_time(self) -> str:
    return self._ex_field_names.get('updated_time', 'updated_time')

  @property
  def ex_field_is_deleted(self) -> str:
    return self._ex_field_names.get('is_deleted', '__is_deleted__')

  @property
  def pk_name(self) -> str:
    return self._pk_name

  @property
  def raw_delete(self) -> bool:
    return self._raw_delete

  @staticmethod
  def delete_dict_k_safe(d: Dict, k: str) -> Any:
    v = None
    if k in d:
      v = d[k]
      del d[k]
    return v

  @staticmethod
  def process_filter(filter: Optional[Dict]) -> Optional[Dict]:
    if not isinstance(filter, dict):
      filter = dict()
    return filter

  def process_filter_for_not_deleted(self, filter: Optional[Dict]) -> Dict:
    filter = self.process_filter(filter)
    if self.raw_delete:
      ret = filter
    else:
      if filter:
        ret = {
          '$and': [
            {
              self.ex_field_is_deleted: {'$ne': True},
            },
            filter,
          ]
        }
      else:
        ret = {
          self.ex_field_is_deleted: {'$ne': True},
        }
    return ret

  def insert_item(self, item: Dict) -> Dict:
    self.delete_dict_k_safe(item, self.ex_field_is_deleted)

    if '_id' in item and QxMongoClient.is_object_id(item['_id']):
      item['_id'] = QxMongoClient.make_object_id(item['_id'])
    item[self.ex_field_created_time] = self.mongo_client.current_time
    item[self.ex_field_updated_time] = self.mongo_client.current_time

    self.mongo_client.insert_one(self.collection_name, item)

    return item

  def delete_item(self, filter: Optional[Dict]):
    filter = self.process_filter_for_not_deleted(filter)
    if self.raw_delete:
      self.mongo_client.delete_one(self.collection_name, filter)
    else:
      self.mongo_client.update_one(self.collection_name, filter, {
        '$set': {
          self.ex_field_updated_time: self.mongo_client.current_time,
          self.ex_field_is_deleted: True,
        }
      })

  def delete_item_by_property(self, property_name: str, property_value: Any):
    self.delete_item({
      property_name: property_value,
    })

  def delete_item_by_pk(self, pk_value: Any):
    self.delete_item_by_property(property_name=self.pk_name, property_value=pk_value)

  def update_item(self, filter: Optional[Dict], update: Dict, upsert: bool = False):
    filter = self.process_filter_for_not_deleted(filter)

    set_table = update.get('$set', {})
    set_table[self.ex_field_updated_time] = self.mongo_client.current_time
    update['$set'] = set_table

    self.mongo_client.update_one(self.collection_name, filter, update, upsert)

  def update_items(self, filter: Optional[Dict], update: Dict, upsert: bool = False):
    filter = self.process_filter_for_not_deleted(filter)

    set_table = update.get('$set', {})
    set_table[self.ex_field_updated_time] = self.mongo_client.current_time
    update['$set'] = set_table

    self.mongo_client.update_many(self.collection_name, filter, update, upsert)

  def update_item_by_property(self, property_name: str, property_value: Any, update: Dict, upsert: bool = False):
    self.update_item({
      property_name: property_value,
    }, update, upsert)

  def update_item_by_pk(self, pk_value: Any, update: Dict, upsert: bool = False):
    self.update_item_by_property(self.pk_name, pk_value, update, upsert)

  def set_item_property(self, pk_value: Any, property_name: str, property_value: Any):
    self.update_item_by_pk(pk_value, {
      '$set': {
        property_name: property_value,
      },
    })

  def inc_item_property(self, pk_value: Any, property_name: str, property_value: Any):
    self.update_item_by_pk(pk_value, {
      '$inc': {
        property_name: property_value,
      },
    })

  def push_item_property(self, pk_value: Any, property_name: str, property_value: Any):
    self.update_item_by_pk(pk_value, {
      '$push': {
        property_name: property_value,
      },
    })

  def pull_item_property(self, pk_value: Any, property_name: str, property_value: Any):
    self.update_item_by_pk(pk_value, {
      '$pull': {
        property_name: property_value,
      },
    })

  def update_item_properties(self, pk_value: Any, set_properties: Optional[Dict] = None, inc_properties: Optional[Dict] = None, push_properties: Optional[Dict] = None, pull_properties: Optional[Dict] = None):
    update = dict()
    if isinstance(set_properties, dict) and len(set_properties):
      update['$set'] = set_properties
    if isinstance(inc_properties, dict) and len(inc_properties):
      update['$inc'] = inc_properties
    if isinstance(push_properties, dict) and len(push_properties):
      update['$push'] = push_properties
    if isinstance(pull_properties, dict) and len(pull_properties):
      update['$pull'] = pull_properties
    if len(update):
      self.update_item_by_pk(pk_value, update)

  def set_item_properties(self, pk_value: Any, **kw):
    self.update_item_properties(pk_value, set_properties=kw)

  def inc_item_properties(self, pk_value: Any, **kw):
    self.update_item_properties(pk_value, inc_properties=kw)

  def push_item_properties(self, pk_value: Any, **kw):
    self.update_item_properties(pk_value, push_properties=kw)

  def pull_item_properties(self, pk_value: Any, **kw):
    self.update_item_properties(pk_value, pull_properties=kw)

  def find_item(self, filter: Optional[Dict], default: Optional[Dict] = None) -> Optional[Dict]:
    filter = self.process_filter_for_not_deleted(filter)
    item = self.mongo_client.find_one(self.collection_name, filter)
    item = default if item is None else item
    return item

  def find_item_random(self, filter: Optional[Dict], default: Optional[Dict] = None):
    filter = self.process_filter_for_not_deleted(filter)
    item = self.mongo_client.find_one_random(self.collection_name, filter)
    item = default if item is None else item
    return item

  def find_item_by_property(self, property_name: str, property_value: Any):
    return self.find_item({
      property_name: property_value,
    })

  def find_item_by_pk(self, pk_value: Any):
    return self.find_item_by_property(self.pk_name, pk_value)

  def find_items_with_page_info(self, filter: Optional[Dict], sort: Union[Tuple, List, OrderedDict] = None, limit: int = None, page_info: Optional[Dict] = None):
    filter = self.process_filter_for_not_deleted(filter)
    items, page_info = self.mongo_client.find_many_with_page_info(
      self.collection_name,
      filter=filter,
      sort=sort,
      limit=limit,
      page_info=page_info,
    )
    return items, page_info

  def find_items(self, filter: Optional[Dict], sort: Union[Tuple, List, OrderedDict] = None):
    items, page_info = self.find_items_with_page_info(filter, sort)
    return items

  def find_items_by_property_as_table(self, property_name: str, property_values: Union[List, Tuple, Set]) -> Dict:
    assert isinstance(property_values, (set, list, tuple))
    items = self.find_items({
      property_name: {'$in': list(property_values)},
    })
    table = dict()
    for item in items:
      if property_name in item:
        table[item[property_name]] = item
    return table

  def find_items_by_property_as_order(self, property_name: str, property_values: Union[List, Tuple, Set]) -> List[Dict]:
    table = self.find_items_by_property_as_table(property_name, property_values)
    items = [table[x] for x in property_values if x in table]
    return items

  def find_items_by_pk_as_table(self, pk_values: Union[List, Tuple, Set]):
    return self.find_items_by_property_as_table(self.pk_name, pk_values)

  def find_items_by_pk_as_order(self, pk_values: Union[List, Tuple, Set]):
    table = self.find_items_by_pk_as_table(pk_values=pk_values)
    items = [table[x] for x in pk_values if x in table]
    return items

  def is_exists(self, filter: Optional[Dict]) -> bool:
    return bool(self.find_item(filter))

  def is_exists_by_property(self, property_name: str, property_value: Any) -> bool:
    return bool(self.find_item_by_property(property_name, property_value))

  def is_exists_by_pk(self, pk_value: Any) -> bool:
    return bool(self.find_item_by_pk(pk_value))
