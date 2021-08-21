import uuid
from typing import *

import random
import pymongo
import pymongo.database
import pymongo.results
from bson import ObjectId
from datetime import datetime
from collections import OrderedDict


class QxMongoClient(object):
  def __init__(self, host='127.0.0.1', port=27017, username=None, password=None, database='admin', current_time=None):
    if isinstance(host, str):
      if '://' in host:
        py_mongo_client = QxMongoClient.create_py_mongo_client_from_url(host)
      else:
        py_mongo_client = QxMongoClient.create_py_mongo_client(host, port, username, password)
    else:
      assert isinstance(host, pymongo.MongoClient)
      py_mongo_client = host
    self._mongo_db = py_mongo_client.get_database(database)
    self._current_time = None

    self.current_time = current_time

  @staticmethod
  def create_py_mongo_client(host='127.0.0.1', port=27017, username=None, password=None):
    py_mongo_client = pymongo.MongoClient(
      host=host,
      port=port,
      username=username,
      password=password,
    )
    return py_mongo_client

  @staticmethod
  def create_py_mongo_client_from_url(url='mongodb://127.0.0.1:27017/admin'):
    py_mongo_client = pymongo.MongoClient(url)
    return py_mongo_client

  @property
  def db(self) -> pymongo.database:
    return self._mongo_db

  @property
  def mongo_db(self):
    return self._mongo_db

  @property
  def current_time(self):
    return self._current_time

  @current_time.setter
  def current_time(self, v):
    self._current_time = v if isinstance(v, datetime) else datetime.now()

  @staticmethod
  def _preprocess_sort(sort):
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
  def make_object_id(object_id: Union[ObjectId, str, uuid.UUID]):
    if not isinstance(object_id, ObjectId):
      object_id = ObjectId(str(object_id).replace('-', ''))
    return object_id

  def aggregate(self, collection_name, pipeline):
    items = []
    cursor = self.db.get_collection(collection_name).aggregate(pipeline)
    for item in cursor:
      items.append(item)
    return items  # type: list[dict]

  def aggregate_one(self, collection_name, pipeline) -> Optional[Dict]:
    cursor = self.db.get_collection(collection_name).aggregate(pipeline)
    for item in cursor:
      return item
    return None

  def count(self, collection_name, filter=None):
    count = self.db.get_collection(collection_name).count(filter)
    return count  # type: int

  def exists(self, collection_name, filter=None):
    item = self.db.get_collection(collection_name).find_one(filter)
    is_exists = item is not None
    return is_exists  # type: bool

  def find_one(self, collection_name, filter=None, sort=None, projection=None, fn_process_item=None):
    sort = self._preprocess_sort(sort)

    item = self.db.get_collection(collection_name).find_one(filter, sort=sort, projection=projection)
    if callable(fn_process_item) and item:
      item = fn_process_item(item)

    return item  # type: dict

  def find_many(self, collection_name, filter=None, sort=None, skip=None, limit=None, projection=None, fn_process_item=None):
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
      cursor = self.db.get_collection(collection_name).find(filter, **kw)
      if callable(fn_process_item):
        items = [fn_process_item(item) for item in cursor]
      else:
        items = [item for item in cursor]

    return items  # type: list[dict]

  def find_one_random(self, collection_name, filter=None, projection=None, fn_process_item=None):
    kw = dict()
    if projection:
      kw['projection'] = projection

    cursor = self.db.get_collection(collection_name).find(filter, **kw)
    item = None
    total = cursor.count()
    if total > 0:
      index = random.randint(0, max(total, 999999)) % total
      cursor.skip(index)
      item = cursor.next()

    if callable(fn_process_item) and item:
      item = fn_process_item(item)

    return item  # type: dict

  def insert_one(self, collection_name, document) -> pymongo.results.InsertOneResult:
    assert isinstance(document, dict)
    result = self.db.get_collection(collection_name).insert_one(document)
    return result

  def insert_many(self, collection_name, documents) -> pymongo.results.InsertManyResult:
    assert isinstance(documents, list)
    result = self.db.get_collection(collection_name).insert_many(documents)
    return result

  def delete_one(self, collection_name, filter) -> pymongo.results.DeleteResult:
    result = self.db.get_collection(collection_name).delete_one(filter)
    return result

  def delete_many(self, collection_name, filter) -> pymongo.results.DeleteResult:
    result = self.db.get_collection(collection_name).delete_many(filter)
    return result

  def update_one(self, collection_name, filter, update, upsert=False) -> pymongo.results.UpdateResult:
    result = self.db.get_collection(collection_name).update_one(filter, update, upsert)
    return result

  def update_one_and_return_it(self, collection_name, filter, update, upsert=False) -> Optional[Dict]:
    result = self.update_one(collection_name, filter, update, upsert)
    if upsert and result.upserted_id:
      return self.find_one(collection_name, {
        '_id': result.upserted_id
      })
    return self.find_one(collection_name, filter)

  def update_many(self, collection_name, filter, update, upsert=False) -> pymongo.results.UpdateResult:
    result = self.db.get_collection(collection_name).update_many(filter, update, upsert)
    return result

  def find_one_and_delete(self, collection_name, filter, projection=None, sort=None, fn_process_item=None) -> Optional[Dict]:
    sort = self._preprocess_sort(sort)

    item = self.db.get_collection(collection_name).find_one_and_delete(filter, projection, sort)
    if callable(fn_process_item) and item:
      item = fn_process_item(item)
    return item

  def find_one_and_replace(self, collection_name, filter, replacement, projection=None, sort=None, upsert=False, return_document=False, fn_process_item=None) -> Optional[Dict]:
    sort = self._preprocess_sort(sort)

    item = self.db.get_collection(collection_name).find_one_and_replace(filter, replacement, projection, sort, upsert, return_document)
    if callable(fn_process_item) and item:
      item = fn_process_item(item)
    return item

  def find_one_and_update(self, collection_name, filter, update, projection=None, sort=None, upsert=False, return_document=False, fn_process_item=None) -> Optional[Dict]:
    sort = self._preprocess_sort(sort)

    item = self.db.get_collection(collection_name).find_one_and_update(filter, update, projection, sort, upsert, return_document)
    if callable(fn_process_item) and item:
      item = fn_process_item(item)
    return item

  def find_many_with_page_info(self, collection_name, filter=None, sort=None, skip=None, limit=None, projection=None, page_info=None, fn_process_item=None, fn_process_sort=None) -> Tuple[List[Dict], Dict]:
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

  def collection_names(self, include_system_collections=True, session=None):
    return self.db.collection_names(include_system_collections, session)

  def create_collection(self, name, codec_options=None, read_preference=None, write_concern=None, read_concern=None, session=None, **kw):
    return self.db.create_collection(name, codec_options, read_preference, write_concern, read_concern, session, **kw)


################################################################################


class QxMongoModel(object):
  def __init__(self, mongo_client, collection_name, pk_name='_id', ex_field_names=None, raw_delete: bool = True):
    assert isinstance(mongo_client, QxMongoClient)
    assert isinstance(collection_name, str)
    self._mongo_client = mongo_client
    self._collection_name = collection_name
    self._pk_name = pk_name
    self._ex_field_names = QxMongoModel._process_ex_field_names(ex_field_names)
    self._raw_delete = raw_delete

  def _make_pk_value(self, pk_value: Any) -> Any:
    return QxMongoClient.make_object_id(pk_value) if self._pk_name == '_id' else pk_value

  @staticmethod
  def _process_ex_field_names(d):
    ret = d if isinstance(d, dict) else dict()
    ret.setdefault('created_time', 'created_time')
    ret.setdefault('updated_time', 'updated_time')
    ret.setdefault('is_deleted', '__is_deleted__')
    return ret

  @property
  def mongo_client(self):
    return self._mongo_client

  @property
  def collection_name(self):
    return self._collection_name  # type: str

  @property
  def ex_field_created_time(self):
    return self._ex_field_names.get('created_time', 'created_time')

  @property
  def ex_field_updated_time(self):
    return self._ex_field_names.get('updated_time', 'updated_time')

  @property
  def ex_field_is_deleted(self):
    return self._ex_field_names.get('is_deleted', '__is_deleted__')

  @property
  def pk_name(self):
    return self._pk_name  # type: str

  @property
  def raw_delete(self) -> bool:
    return self._raw_delete

  @staticmethod
  def delete_dict_k_safe(d, k):
    v = None
    if k in d:
      v = d[k]
      del d[k]
    return v

  def process_filter_for_not_deleted(self, filter):
    assert isinstance(filter, dict)
    new_filter = {
      '$and': [
        {
          self.ex_field_is_deleted: {'$ne': True},
        },
        filter,
      ]
    }
    return new_filter

  def insert_item(self, item):
    assert isinstance(item, dict)
    self.delete_dict_k_safe(item, self.ex_field_is_deleted)

    item['_id'] = QxMongoClient.make_object_id(item.get('_id', ObjectId()))
    item[self.ex_field_created_time] = self.mongo_client.current_time
    item[self.ex_field_updated_time] = self.mongo_client.current_time

    self.mongo_client.insert_one(self.collection_name, item)

    return item

  def delete_item(self, filter):
    filter = self.process_filter_for_not_deleted(filter)
    if self.raw_delete:
      self.mongo_client.delete_one(self.collection_name, filter)
    else:
      self.mongo_client.update_one(self.collection_name, filter, {
        '$set': {self.ex_field_is_deleted: True}
      })

  def delete_item_by_property(self, property_name, property_value):
    self.delete_item({
      property_name: property_value,
    })

  def delete_item_by_pk(self, pk_value):
    self.delete_item_by_property(property_name=self.pk_name, property_value=pk_value)

  def update_item(self, filter, update, upsert=False):
    filter = self.process_filter_for_not_deleted(filter)

    assert isinstance(update, dict)
    set_table = update.get('$set', {})
    set_table[self.ex_field_updated_time] = self.mongo_client.current_time
    update['$set'] = set_table

    self.mongo_client.update_one(self.collection_name, filter, update, upsert)

  def update_items(self, filter, update, upsert=False):
    filter = self.process_filter_for_not_deleted(filter)

    assert isinstance(update, dict)
    set_table = update.get('$set', {})
    set_table[self.ex_field_updated_time] = self.mongo_client.current_time
    update['$set'] = set_table

    self.mongo_client.update_many(self.collection_name, filter, update, upsert)

  def update_item_by_property(self, property_name, property_value, update):
    self.update_item({
      property_name: property_value,
    }, update)

  def update_item_by_pk(self, pk_value, update):
    self.update_item_by_property(self.pk_name, pk_value, update)

  def set_item_property(self, pk_value, property_name, property_value):
    self.update_item_by_pk(pk_value, {
      '$set': {
        property_name: property_value,
      },
    })

  def inc_item_property(self, pk_value, property_name, property_value):
    self.update_item_by_pk(pk_value, {
      '$inc': {
        property_name: property_value,
      },
    })

  def push_item_property(self, pk_value, property_name, property_value):
    self.update_item_by_pk(pk_value, {
      '$push': {
        property_name: property_value,
      },
    })

  def pull_item_property(self, pk_value, property_name, property_value):
    self.update_item_by_pk(pk_value, {
      '$pull': {
        property_name: property_value,
      },
    })

  def update_item_properties(self, pk_value, set_properties=None, inc_properties=None, push_properties=None, pull_properties=None):
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

  def set_item_properties(self, pk_value, **kw):
    self.update_item_properties(pk_value, set_properties=kw)

  def inc_item_properties(self, pk_value, **kw):
    self.update_item_properties(pk_value, inc_properties=kw)

  def push_item_properties(self, pk_value, **kw):
    self.update_item_properties(pk_value, push_properties=kw)

  def pull_item_properties(self, pk_value, **kw):
    self.update_item_properties(pk_value, pull_properties=kw)

  def find_item(self, filter, default=None):
    filter = self.process_filter_for_not_deleted(filter)
    item = self.mongo_client.find_one(self.collection_name, filter)
    item = default if item is None else item
    return item

  def find_item_random(self, filter, default=None):
    filter = self.process_filter_for_not_deleted(filter)
    item = self.mongo_client.find_one_random(self.collection_name, filter)
    item = default if item is None else item
    return item

  def find_item_by_property(self, property_name, property_value):
    return self.find_item({
      property_name: property_value,
    })

  def find_item_by_pk(self, pk_value):
    return self.find_item_by_property(self.pk_name, pk_value)

  def find_items_with_page_info(self, filter, sort=None, limit=None, page_info=None):
    filter = self.process_filter_for_not_deleted(filter)
    items, page_info = self.mongo_client.find_many_with_page_info(
      self.collection_name,
      filter=filter,
      sort=sort,
      limit=limit,
      page_info=page_info,
    )
    return items, page_info

  def find_items(self, filter, sort=None):
    items, page_info = self.find_items_with_page_info(filter, sort)
    return items

  def find_items_by_pk_as_table(self, pk_values, pk_name=None):
    assert isinstance(pk_values, (set, list, tuple))
    pk_name = self.pk_name if pk_name is None else pk_name
    items = self.find_items({
      pk_name: {'$in': list(pk_values)},
    })
    table = dict()
    for item in items:
      if pk_name in item:
        table[item[pk_name]] = item
    return table

  def find_items_by_pk_as_order(self, pk_values, pk_name=None):
    table = self.find_items_by_pk_as_table(pk_values=pk_values, pk_name=pk_name)
    items = [table[x] for x in pk_values if x in table]
    return items

  def is_exists(self, filter):
    return bool(self.find_item(filter))

  def is_exists_by_property(self, property_name, property_value):
    return bool(self.find_item_by_property(property_name, property_value))

  def is_exists_by_pk(self, pk_value):
    return bool(self.find_item_by_pk(pk_value))
