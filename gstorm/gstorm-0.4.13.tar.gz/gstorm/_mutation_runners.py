from __future__ import annotations
from typing import Union, List
from gstorm.enums import MutationMode
import gstorm

def create(
    data: Union[gstorm.GraphQLType, List[gstorm.GraphQLType]],
    mode: MutationMode = MutationMode.BATCH
  ) -> MutationBuilder:
  """Builds instance of MutationBuilder to sync GraphQLType objects created locally with the remote DB.
  
  Parameters
  ----------
  data : Union[gstorm.GraphQLType, List[gstorm.GraphQLType]]
    GraphQLType instance(s) to create in the DB
  mode : MutationMode, optional
    allows to upload data by different upload mechanisms, by default MutationMode.BATCH
  
  Returns
  -------
  MutationBuilder
    Instance of MutationBuilder class, responsible of building mutation string and communication with DB.
  """
  return gstorm.MutationBuilder(data=data, mode=mode)

def update():
  raise NotImplementedError('gstorm.update not implemented')

def upsert():
  raise NotImplementedError('gstorm.upsert not implemented')

def delete():
  raise NotImplementedError('gstorm.delete not implemented')
