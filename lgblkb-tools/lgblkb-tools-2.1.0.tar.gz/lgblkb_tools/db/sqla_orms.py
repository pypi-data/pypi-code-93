import os
from abc import abstractmethod

# import joblib
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import Function as sql_function

from .. import Folder
from .. import logger
from ..common import utils

Base = declarative_base()


def get_info(obj):
    if not isinstance(obj, dict): obj = obj.__dict__
    out_info = dict()
    for k, v in obj.items():
        if k[0] == '_':
            continue
        elif type(v) in [WKBElement, sql_function]:
            v = to_shape(v).wkt
        out_info[k] = v
    # info={k:v for k,v in self.__dict__.items() if (k[0]!='_' and not isinstance(v,WKBElement))}
    return out_info


class InfoBase(object):
    
    @property
    def info(self):
        return get_info(self)
    
    def __repr__(self):
        return utils.reprer(self)


class StatusTrackable(InfoBase):
    status_key = 'status'


class Reconnectable(InfoBase):
    
    @abstractmethod
    def reconnect(self, session):
        pass
    
    @staticmethod
    def get_dump_filepath(folder=None, filename='', filepath=''):
        if not filepath:
            assert all([folder, filename]), 'Dump folder and filename should be provided.'
            filepath = Folder(folder).get_filepath(filename)
            if not os.path.splitext(filepath)[-1]: filepath += '.joblib'
        logger.debug('filepath: %s', filepath)
        return filepath

# @classmethod
# def from_dump(cls,folder=None,filename='',filepath=''):
# 	filepath=cls.get_dump_filepath(folder=folder,filename=filename,filepath=filepath)
# 	assert os.path.exists(filepath),f'Filepath {filepath} does not exist.'
# 	logger.debug('Loading object from dump file.')
# 	return joblib.load(filepath)

# def to_dump(self,folder=None,filename='',filepath=''):
# 	filepath=self.get_dump_filepath(folder=folder,filename=filename,filepath=filepath)
# 	joblib.dump(self,filepath)
# 	return self


class KeysBase(Reconnectable):
    primary_keys = ['id']
    
    def reconnect(self, session):
        pass
    
    def __repr__(self):
        return utils.reprer(self)


class IntegerID_Base(KeysBase):
    id = Column(Integer, primary_key=True)


class TextID_Base(KeysBase):
    id = Column(Text, primary_key=True)


def main():
    # Sentinel2_Info.__table__.create(engine)
    pass
    # old_statuses=collections.OrderedDict()
    # old_statuses['RunningAtmosphericCorrection']=image_status.Running.AtmosphericCorrection
    # old_statuses['FinishedAtmosphericCorrection']=image_status.Finished.AtmosphericCorrection
    # old_statuses['QueuedForAtmosphericCorrection']=image_status.QueuedFor.AtmosphericCorrection
    # old_statuses['NotForProcessing']=image_status.NotForProcessing
    #
    # for old_status,new_status in old_statuses.items():
    # 	for row in session.query(Sentinel2_Info).filter(Sentinel2_Info.status==old_status).all():
    # 		row.status=new_status
    pass
    
    pass


if __name__ == '__main__':
    main()
