from datetime import datetime
import pytz
from typing import Any
import logging,os, jmespath
from abc import ABCMeta, abstractmethod
from mailjet_rest import Client
from .client_utils import FirestoreClient
from google.cloud.firestore import DocumentReference, DocumentSnapshot
from .pub_sub import publish_message

GROW_PATTERN = r"\/*(?P<grow_path>application_data\/(?P<company>\w+)\/Sales_Inventory\/(?P<invloc_collname>\w+)\/(?P<grow_name>Grow(?P<grow_type>Week|Month))\/(?P<grow_id>(?P<grow_year>\d{4})_(?P<grow_suffix>\d{2}))).*"
ITEMS_PATTERN = r"\/*(?P<item_path>(?P<location_path>(?P<customer_path>application_data/\w+/\w+/StorageBlob/customer/(?P<customer_id>customer\-\d+))/locations/(?P<location_id>location\-\d+))/items/(?P<item_id>\w+\-\d+))"
LOCATION_PATTERN = r"\/*(?P<location_path>(?P<customer_path>application_data/\w+/\w+/StorageBlob/customer/(?P<customer_id>customer\-\d+))/locations/(?P<location_id>location\-\d+))"
CUSTOMER_PATTERN = r"\/*(?P<customer_path>application_data/\w+/\w+/StorageBlob/customer/(?P<customer_id>customer\-\d+))(/locations/(?P<location_id>location\-\d+)(/items/(?P<item_id>\w+\-\d+)|$)|$)"
BASIC_PATTERN = r"\/*application_data\/(?P<company>\w+)\/.*"
FLOAT_REGEX = r'(^(-?|\+?)\d*\.?\d+|^\d+)$'

from json import JSONEncoder

def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)

_default.default = JSONEncoder.default  # Save unmodified default.
JSONEncoder.default = _default # Replace it.

class FSDocument(object):
    def __init__(self, fsDocument: object, loadSnap=True):
        self.snap = None
        self.ref = None
        self.origDoc = fsDocument
        self.docType = 'ref'
        self._growInfo = None
        self.customer_info = None
        if isinstance(fsDocument,DocumentReference):
            self.ref = fsDocument
            if loadSnap:
                self.snap = fsDocument.get()
        elif isinstance(fsDocument,DocumentSnapshot):
            self.docType = 'snap'
            self.snap = fsDocument
            self.ref = fsDocument.reference
        elif isinstance(fsDocument,FSDocument):
            self.docType = 'fsDoc'
            self.snap = fsDocument.snap
            self.ref = fsDocument.ref

    @classmethod
    def getInstance(cls,docPath, loadSnap=True):
        clt = FirestoreClient.getInstance().fsClient
        docRef = clt.document(docPath)
        return FSDocument(docRef,loadSnap)

    @property
    def exists(self):
        return self.snap.exists
    
    @property
    def path(self):
        if self.ref is None:
            return ''
        return self.ref.path
    
    @property
    def grow_info(self):
        if self._growInfo is None:
            self._growInfo = self._get_grow_info()
        return self._growInfo
    
    @property
    def period_type(self):
        return self.grow_info['grow_type']
    
    @property
    def grow_period(self):
        return self.grow_info['grow_id']
    
    @property
    def grow_name(self):
        return self.grow_info['grow_name']

    @property
    def grow_path(self):
        return self.grow_info['grow_path']

    @property
    def grow_number(self):
        return self.grow_info['grow_suffix']
    
    @property
    def grow_year(self):
        return self.grow_info['grow_year']

    @property
    def company(self):
        return self.grow_info['company']
    
    @property
    def inventory_location(self):
        return self.grow_info['inventory_location']

    @property
    def customer_path(self):
        if self.customer_info is None:
            self._get_customer_info()
        return jmespath.search("[?info_type == 'customer'].info_details.path | [0]",self.customer_info)

    @property
    def customer_id(self):
        if self.customer_info is None:
            self._get_customer_info()
        return jmespath.search("[?info_type == 'customer'].info_details.id | [0]",self.customer_info)

    @property
    def location_path(self):
        if self.customer_info is None:
            self._get_customer_info()
        return jmespath.search("[?info_type == 'location'].info_details.path | [0]",self.customer_info)

    @property
    def location_id(self):
        if self.customer_info is None:
            self._get_customer_info()
        return jmespath.search("[?info_type == 'location'].info_details.id | [0]",self.customer_info)

    @property
    def item_path(self):
        if self.customer_info is None:
            self._get_customer_info()
        return jmespath.search("[?info_type == 'item'].info_details.path | [0]",self.customer_info)

    @property
    def item_id(self):
        if self.customer_info is None:
            self._get_customer_info()
        return jmespath.search("[?info_type == 'item'].info_details.id | [0]",self.customer_info)

    @property
    def id(self):
        return self.ref.id

    def _get_customer_info(self) -> dict:
        '''
        Take the customer pattern and extract info from it
        '''
        pull_items = ['customer','location','item']
        mm = re.match(ITEMS_PATTERN,self.path)
        self.customer_info = []
        if mm is not None:
            self.customer_info = self._get_regex_info(pull_items,mm.groupdict())
        else:
            mm = re.match(LOCATION_PATTERN,self.path)
            if mm is not None:
                self.customer_info = self._get_regex_info(pull_items[:-1],mm.groupdict())
            else:
                mm = re.match(CUSTOMER_PATTERN)
                if mm is not None:
                    self.customer_info = self._get_regex_info(pull_items[:-2],mm.groupdict())

    
    def _get_regex_info(self,items,grpDict):
        return [{'info_type':x, 'info_details':{'path':grpDict.get(x+'_path',''),'id':grpDict.get(x+'_id','')}} for x in items]

    def _get_grow_info(self) -> dict:
        '''
        Given a path to the either the ItemMonth or the ItemWeek, can we get needed info
        
        Returns
        -------
            grow_path : str
                The path to the growMonth or growWeek
            grow_id : str
                The identifier for this path i.e. (2021_06)
            grow_type : str
                Either 'Month' or 'Week'
            grow_year : str
                The 4 digit year for this grow month/week
            grow_name : str
                The instance name GrowMonth or GrowWeek
            grow_suffix : str
                if this is a month it will be the month number, if week, it will be the week number
            company: str
                what company is the data loaded under
            inventory_location : str
                Get the inventory location
        
        Parameters
        ----------
            documentPath : str
                The path to the ItemWeek or ItemMonth
        '''
        mm = re.match(GROW_PATTERN,self.path)
        cols = ['grow_name','grow_type','grow_id','grow_path','grow_year','grow_suffix','company']
        retInfo = {}
        if mm is not None:
            grpD = mm.groupdict()
            oldStr = grpD.get('invloc_collname',None)
            growPath = grpD.get('grow_path',None)
            invLoc = oldStr
            if oldStr is not None and growPath is not None:
                growPath = growPath.replace(oldStr,'Converted')
                invLoc = oldStr.replace('InventoryLoc__','')
            for col in cols:
                retInfo[col] = grpD.get(col,'')
            
            retInfo['grow_path'] = growPath
            retInfo['inventory_location'] = invLoc
        
        return retInfo
    
    def isRef(self) -> bool:
        return self.docType == 'ref'
    
    def isSnap(self) -> bool:
        return self.docType == 'snap'
    
    def isFsDoc(self) -> bool:
        return self.docType == 'fsDoc'

    def get(self, field_path: str) -> Any:
        return self.snap.get(field_path)

    def getData(self,field_path: str) -> Any:
        return self.snap.get(field_path)

    def setData(self, field_updates: dict) -> Any:
        return self.ref.update(field_updates)
    
    def to_json(self):
        return {'object':'FSDocument','path':self.path}
    
    @property
    def exists(self):
        if self.snap is None:
            return False
        return self.snap.exists

class FireStoreBase(metaclass=ABCMeta):

    base_fields = ['added_by','updated_by','timestamp','up_timestamp','soft_delete','added_system','updated_system','dnl']

    DATA_STORAGE_TYPE = 'data_schemas'
    STORAGE_FIELDS = 'storage_fields'

    DELETED_PATH = 'application_deleted_data'

    #grow_pattern = r"\/*(?P<grow_path>application_data\/(?P<company>\w+)\/Sales_Inventory\/(?P<invloc_collname>\w+)\/(?P<grow_name>Grow(?P<grow_type>Week|Month))\/(?P<grow_id>(?P<grow_year>\d{4})_(?P<grow_suffix>\d{2}))).*"


    @abstractmethod
    def base_path(self):
        pass

    @property
    @abstractmethod
    def ext_fields(self):
        pass

    @property
    def grow_pattern(self):
        return GROW_PATTERN
    
    @property
    def item_pattern(self):
        return ITEMS_PATTERN
    
    @property
    def location_pattern(self):
        return LOCATION_PATTERN

    @property
    def customer_pattern(self):
        return CUSTOMER_PATTERN

    @property
    def basic_pattern(self):
        return BASIC_PATTERN
    

    def __init__(self,fsClient,**kwargs): 
        '''
        it is expected that the documentReference and the documentSnapshot is passed in
        documentReference = fs_docRef
        documentSnapshot = fs_docSnap
        '''
        self._fsClient = self.get_client() if fsClient is None else fsClient
        self._documentRef = kwargs.get('fs_docRef',None)
        self._document = kwargs.get('fs_docSnap',None)
        self._doc_loaded = True # this tracks whether the class... will always be 3/8/20
        self.added_by = kwargs.get('added_by',None)
        self._company = None
        self.updated_by = kwargs.get('updated_by',None)
        self.timestamp = kwargs.get('timestamp',None)
        self.up_timestamp = kwargs.get('up_timestamp',None)
        self.soft_delete = kwargs.get('soft_delete',False)
        self.added_system = kwargs.get('added_system','legacy')
        self.updated_system = kwargs.get('updated_system','legacy')
        self._fields = FireStoreBase.base_fields + self.ext_fields

    def update_data(self,update_data):
        self.__dict__.update(update_data)

    def _add_fields(self,field_name_list):
        _ = [self._add_field(fn) for fn in field_name_list]

    def get_bq_schema(self):
        schema = {'fields':[]}
        schema['fields'].append({'field_name':'added_by','field_type':'string'})
        schema['fields'].append({'field_name':'updated_by','field_type':'string'})
        schema['fields'].append({'field_name':'timestamp','field_type':'datetime'})
        schema['fields'].append({'field_name':'up_timestamp','field_type':'datetime'})
        schema['fields'].append({'field_name':'soft_delete','field_type':'boolean'})
        schema['fields'].append({'field_name':'doc_id','field_type':'int','field_required':True})
        schema['fields'].append({'field_name':'added_system','field_type':'int'})
        schema['fields'].append({'field_name':'updated_system','field_type':'int'})
        return schema

    @classmethod
    def returnFSDoc(cls,inFsDoc) -> FSDocument:
        return FSDocument(inFsDoc)

    @classmethod
    def GetEnvironment(cls) -> str:
        comp = os.environ.get('APP_FIRESTORE_COMPANY','Color_Orchids')
        fsDoc = cls.returnFSDocByPath(f'application_data/{comp}')
        return fsDoc.getData('environment')
    
    @classmethod
    def returnFSDocByPath(cls,docPath) -> FSDocument:
        return cls.returnFSDoc(cls.get_firestore_client().document(docPath))

    @classmethod
    def getInstanceAny(cls,inCls,fsDoc):
        return inCls.getInstance(fsDoc)

    @classmethod
    def get_active_any(cls,inClient, base_path, inCls):
        colRef = inClient.collection(base_path)
        #q = colRef.where('soft_delete','==',False)  #Getting no values when the soft-delete field doesn't exist
        docs = colRef.list_documents()

        objArr = []

        if inCls:
            objArr = [inCls.getInstance(ref) for ref in docs]
            objArr = [x for x in objArr if not x.soft_delete]
        else:
            objArr = [x.get().to_dict() for x in docs]
            objArr = [x for x in objArr if not x['soft_delete']]
        
        return objArr

    def __load_data(self):
        self.data_dict = {}
        for field in self._fields:
            self.data_dict[field] = self.__get_data_value(field)
        return self.data_dict
    
    @classmethod
    def snapToDict(cls, snap):
        dd = snap.to_dict()
        if dd is None:
            dd = {}
        return dd

    @classmethod
    def CheckFloat(cls,inNum):
        mm = re.match(FLOAT_REGEX,inNum)
        if mm is not None:
            return True
        else:
            return False

    def check_float(self,inNum):
        return FireStoreBase.CheckFloat(inNum)
    
    @classmethod
    def _toNum(cls,inNum,defaultNum=1):
        try:
            return int(inNum)
        except:
            return defaultNum

    def set_document(self,inDoc):
        if self._document is None and isinstance(inDoc,DocumentSnapshot):
            self._document = inDoc

    def get_base(self):
        dd = {}
        for field in FireStoreBase.base_fields:
            dd[field] = self.__get_data_value(field)
        return dd

    def get_fields(self):
        dd = {}
        for field in self.ext_fields:
            dd[field] = self.__get_data_value(field)
        return dd

    def __get_data_value(self,name):
        return getattr(self, name, "")

    def __set_data_value(self,name,value):
        setattr(self,name,value)

    def _add_field(self,field_name):
        self._fields.append(field_name)

    @property
    def reference(self):
        return self._documentRef

    @property
    def exists(self):
        if self._document is not None:
            return self._document.exists
        return False

    @property
    def path(self):
        return self.reference.path

    @property
    def company(self):
        if self._company is None:
            mm = re.match(self.basic_pattern,self.path)
            if mm is not None:
                grpD = mm.groupdict()
                self._company = grpD.get('company',None)
        return self._company
    
    @property
    def dnl(self):
        if not self.reference is None:
            return self.reference.id
        return ''
    
    @property
    def parent_path(self):
        if self.exists:
            parCol = self._documentRef.parent
            parId = parCol.id
            return parCol.parent.path+"/"+parId
        else:
            if self.path:
                return "/".join(self.path.split('/')[:-1])
        return ''
    
    @property
    def parent_doc_path(self):
        return self._documentRef.parent.parent.path

    @property
    def parent_doc_id(self):
        return self._documentRef.parent.parent.id

    @property
    def parent_id(self):
        parCol = self._documentRef.parent
        return parCol.parent.id
    
    def load_document(self):
        if not self._doc_loaded:
            self._doc_loaded = self.__load_document()
        return self._doc_loaded

    def __load_document(self):
        '''
        Call this method when you want to load this class with the values stored in Firestore
        '''
        if self._document is None and self._documentRef is None:
            return False

        if self._document is None:
            self._document = self._documentRef.get()
        elif self._documentRef is None:
            self._documentRef = self._document.reference

        #for field in self._fields:
        #    try:
        #        self.__set_data_value(field, self._document.get(field))
        #    except KeyError:
        #        logging.debug("Could not fetch ("+field +") from document... defaulting to empty")
        #        self.__set_data_value(field, '')

        return True

    def eval_value(self, key, val):
        '''
        An opportunity for a class to override the way a value gets
        translated into a dictionary
        '''
        return val

    def __process_collection(self,collectionRef):
        return_dict = {'id':collectionRef.id,'docs':{}}
        docs = collectionRef.list_documents()
        for doc in docs:
            ref,snap = FireStoreBase.getDocuments(doc)
            inDict = {'fs_docRef':ref,'fs_docSnap':snap}
            fsDoc = FirestoreBaseImpl.getInstance(self._fsClient,inDict)
            return_dict['docs'][doc.id] = fsDoc.get_dict(load=True)
        return return_dict

    def get_dict(self,include_keys=True, addl_exclude=[],load=True):
        if not self._doc_loaded:
            if load:
                self.load_document()
                if not self._doc_loaded:
                    return {}

        elist = self._fields
        includeFields  = [x for x in elist if x not in ['fs_docRef','fs_docSnap'] + addl_exclude]

        #fields = self.__dict__
        #data = {k:v for k,v in fields.items() if k in includeFields}
        data = {k:getattr(self,k,'') for k in includeFields}
        if self._documentRef is not None:
            data['id'] = self._documentRef.id
        
        return data

    @property
    def id(self):
        """Override for getting the ID.
        Resolves NotImplementedError: No `id` attribute - override `get_id`
        :rtype: str
        """
        return self._documentRef.id

    @classmethod
    def getDocuments(cls,inDocument):
        if isinstance(inDocument,FSDocument):
            return inDocument.ref, inDocument.snap
        fsDoc = FSDocument(inDocument)
        return fsDoc.ref, fsDoc.snap

    @classmethod
    def create_key(cls, kind_str, int_id):
        raise Exception('Method not implemented:  "create_key"')

    @classmethod
    def _post_get_hook(cls, key, future):
        raise Exception('Method not implemented:  "_post_get_hook"')

    def _post_put_hook(self, future):
        raise Exception('Method not implemented:  "_post_put_hook"')

    def set_saved(self):
        self._is_saved = True

    def is_saved(self):
        return getattr(self, "_is_saved", False)

    def convert_bool(self, value):
        if str(value).lower().strip()  == "true":
            return True

        if str(value).lower().strip() == "1":
            return True
        return False

    def update_resp(self,doCreate=False):
        resp = {'status':'success','msg':'Updated Successfully'}
        try:
            path = self.update_ndb(doCreate)
            resp['path'] = path
        except Exception as e:
            resp = {'status':'failed','msg': str(e)}
        return resp

    def default_data_set(self):
        '''
        meant to be overridden... so you can a default value if needed
        '''
        pass

    def _set_add_entries(self):
        self.added_by = self.get_client().user_email
        self.timestamp = datetime.now().isoformat()
        self.added_system = 'Firestore_Backend_2020'

    def _set_update_entries(self):
        self.up_timestamp = datetime.now().isoformat()
        self.updated_by = self.get_client().user_email
        self.updated_system = 'Firestore_Backend_2020'

    def update_ndb(self, doCreate=False):
        if self._document is None and not doCreate:
            self._document = self._documentRef.get()
        if self._document is not None and self._document.exists:
            self._set_update_entries()
            self.default_data_set()
            self._document.reference.set(self.__load_data())
        else:
            self._set_add_entries()
            self._set_update_entries()
            self.default_data_set()
            self._documentRef.create(self.__load_data())
            self._document = self._documentRef.get()
        return self._documentRef.path

    def delete_resp(self,backupData=True, removeDnl=True):
        resp = {'status':'success','msg':'Deleted Successfully', 'didDelete':True}
        try:
            if self._documentRef is not None:
                resp['path'] = self._documentRef.path
                delData = None
                if self._documentRef.path.startswith('application_data') and backupData:
                    delData = self._documentRef.get().to_dict()
                    delDate = datetime.now()
                    newStart = f'application_deleted_data/{self.company}__{delDate.month}_{delDate.day}_{delDate.year}'
                    delCollection = self._fsClient.collection(newStart+'/deleted_docs')
                    delDocRef = delCollection.document()
                    baseDelRef = self._fsClient.document(newStart)
                    if not baseDelRef.get().exists:
                        baseDelRef.set({'description':'Created to track deleted items','deleted_dnl':{}})
                    
                    #delDocRef = self._fsClient.document(newPath)
                    delDocRef.set(delData)
                    baseDelRef.update({f"deleted_dnl.`{self._documentRef.id}`":{'new_path':delDocRef.path,'old_path':self._documentRef.path}})
                self._documentRef.delete()
                if removeDnl:
                    FireStoreBase.remove_dnl(self._documentRef.id)
            else:
                raise Exception("Cannot Delete that to which there is no reference")

        except Exception as e:
            resp = {'status':'failed','msg': str(e), 'didDelete':False}
        return resp

    def build_data_info(self, inAction='init'):
        '''
        This is the function that gathers information to publish
        for those interested in data updates... ahem... BigQuery!!
        '''
        dataInfo = {}
        status = 'Active'
        if inAction == 'delete':
            status = 'Inactive'

        dataInfo['status'] = status
        dataInfo["_id"] = self.id
        dataInfo['action'] = inAction
        dataInfo['model_name'] = self.__class__.__name__
        dataInfo['app_name'] = 'SalesInventory'
        method_to_call = getattr(self, 'get_schema')
        dataInfo['schema'] = method_to_call()
        method_to_call = getattr(self, 'get_values_dict')
        dataInfo['payload'] = method_to_call()

        return dataInfo

    def reset_dw_sync(self):
        raise Exception('Method not implemented:  "reset_dw_sync"')

    def set_dw_sync(self):
        raise Exception('Method not implemented:  "set_dw_sync"')
        
    @property
    def period_type(self):
        growInfo = self.get_grow_info(self.path)
        return growInfo['grow_type']
    
    @property
    def grow_period(self):
        growInfo = self.get_grow_info(self.path)
        return growInfo['grow_id']
    
    @property
    def grow_path(self):
        return self.get_grow_path(self.path)
    
    @property
    def grow_name(self):
        growInfo = self.get_grow_info(self.path)
        return growInfo['grow_name']

    def get_grow_path(self, documentPath : str) -> str:
        '''
        Given a path to either ItemMonth or ItemWeek, can we get the GrowWeek or GrowMonth path
        
        Parameters
        ----------
            documentPath : str
                The path to the inventory
        '''
        growInfo = self.get_grow_info(documentPath)
        
        return growInfo['grow_path']

    def apply_path_pattern(self,pattern_type=None, inPath=None):
        pattern = self.customer_pattern
        if pattern_type == 'location':
            pattern = self.location_pattern
        elif pattern_type == 'item':
            pattern = self.item_pattern
        else:
            pattern_type = 'customer'

        if inPath is None:
            inPath = self.path
        
        mm = re.match(pattern,inPath)
        if mm is not None:
            grpD = mm.groupdict()
            if pattern_type == 'customer':
                if grpD.get('item_id',None) is not None:
                    mmi = re.match(self.item_pattern,inPath)
                    grpD = mmi.groupdict()
            return grpD
        else:
            return None


    def get_grow_info(self, documentPath : str) -> dict:
        '''
        Given a path to the either the ItemMonth or the ItemWeek, can we get needed info
        
        Returns
        -------
            grow_path : str
                The path to the growMonth or growWeek
            grow_id : str
                The identifier for this path i.e. (2021_06)
            grow_type : str
                Either 'Month' or 'Week'
            grow_year : str
                The 4 digit year for this grow month/week
            grow_name : str
                The instance name GrowMonth or GrowWeek
            grow_suffix : str
                if this is a month it will be the month number, if week, it will be the week number
        
        Parameters
        ----------
            documentPath : str
                The path to the ItemWeek or ItemMonth
        '''
        mm = re.match(GROW_PATTERN,documentPath)
        cols = ['grow_name','grow_type','grow_id','grow_path','grow_year','grow_suffix']
        retInfo = {}
        if mm is not None:
            grpD = mm.groupdict()
            oldStr = grpD.get('invloc_collname',None)
            growPath = grpD.get('grow_path',None)
            if oldStr is not None and growPath is not None:
                growPath = growPath.replace(oldStr,'Converted')
            for col in cols:
                retInfo[col] = grpD.get(col,'')
            
            retInfo['grow_path'] = growPath
        
        return retInfo

    @classmethod
    def get_lastupdated(cls, upd_date):
        raise Exception('Method not implemented:  "get_lastupdated"')

    @classmethod
    def set_for_update(cls, upd_date):
        raise Exception('Method not implemented:  "set_for_update"')

    @classmethod
    def get_for_update(cls):
        raise Exception('Method not implemented:  "get_for_update"')

    @classmethod
    def get_client(cls):
        return FirestoreClient.getInstance()

    @classmethod
    def get_firestore_client(cls):
        return FirestoreClient.getInstance().fsClient

    @classmethod
    def get_storage_client(cls):
        return FirestoreClient.getInstance().storeClient

    @classmethod
    def get_backend_client(cls):
        return FirestoreClient.getInstance()
    
    @classmethod
    def convert_utc_to_timezone_str(cls,inputDate, tz_string='US/Eastern',dt_format="%m/%d/%Y %H:%M:%S EST"):
        if inputDate is None:
            inputDate = ''
        if inputDate != '' and inputDate.find('+') > 0:
            updDt = datetime.fromisoformat(inputDate)
            strDt = updDt.strftime(dt_format)
            return strDt
        if inputDate != '' and inputDate.find('EST') < 0:
            updDt = datetime.fromisoformat(inputDate+'+00:00')
            updDt = updDt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(tz_string))
            strDt = updDt.strftime(dt_format)
            return strDt
        return inputDate

    @classmethod
    def _get_collection_type(cls, dnl):
        if dnl:
            parts = dnl.split("-")
            if len(parts) > 1:
                return "DNL_"+parts[0]
        return FireStoreBase.get_client().application

    @classmethod
    def remove_dnl(cls,dnl):
        if dnl == '' or dnl is None:
            return False

        colName = cls._get_collection_type(dnl)
        dnlRef = cls.get_firestore_client().document(f'data_number_lookup/Color_Orchids/{colName}/{dnl}')
        try:
            if dnlRef.exists:
                dnlRef.delete()
            return True
        except Exception:
            return False

    @classmethod
    def CleanItemName(cls,inName):
        '''
        The shared method to update the name to make it URL safe

        Parameters
        ----------
            inName : str
                Replace single quote, double quote spaces, periods and ampersand
        '''
        return inName.replace("'","").replace('"','').replace(' ','').replace(".","").replace('&',"")
    
    @classmethod
    def CleanItemType(cls,item_type):
        '''
        Get the clean item type name (lower case not ending in 's')

        Parameters
        ----------
            item_type : str
                The string name of the item type
        '''
        lower = item_type.lower()
        lower = lower.replace(" ","_")
        if (lower.endswith('s')):
            return lower[:-1]
        return lower

class FirestoreBaseImpl(FireStoreBase):
    base_path = ''
    ext_fields = []

    @classmethod
    def getInstance(cls,fsClient,inDict):
        fbi = FirestoreBaseImpl(fsClient,**inDict)
        return fbi

class FirestoreBaseFSDoc(FireStoreBase):
    base_path = ''
    ext_fields = []

    def __init__(self, fsDocument, **kwargs):
        self.fsDocument = fsDocument
        super(FirestoreBaseFSDoc, self).__init__(FirestoreBaseFSDoc.get_firestore_client(), **kwargs)

    @classmethod
    def getInstance(cls,fsDocument):
        docDict = fsDocument.snap.to_dict()
        docDict['fs_docSnap'] = fsDocument.snap
        docDict['fs_docRef'] = fsDocument.ref
        return cls(fsDocument,**docDict)

    def base_path(self):
        return ''

class FSObjSummary(object):
    '''
    Convenience class written to summarize a firestore object to store in another object

    The functions in here will help create a summary from a loaded object... Or can load an object based on
    the summary

    id:  this is the document id and/or Data Number Lookup
    name: The name from which to identify this object
    path:  The lookup path to load the full object

    '''

    fields = ['id','type','name','path']

    def __init__(self, id=None, name=None, path=None):
        self.id = id
        self.name = name
        self.path = path

    @classmethod
    def createInstance(cls,obj,fldMapping=None):
        '''
        check object to be instance of DocumentReference or instance of FireStoreBase (then use ._documentRef)
        '''
        if fldMapping is None:
            fldMapping = {'name':'name','id':'id','path':'path'}
        
        dataInput = {}
        dataInput['id'] = getattr(obj,fldMapping.get('id','id'))
        dataInput['name'] = getattr(obj,fldMapping.get('name','name'))
        dataInput['path'] = getattr(obj,fldMapping.get('path','path'))
        return FSObjSummary(**dataInput)

    def getFirestoreDoc(self):
        doc = FirestoreClient.getInstance().fsClient.document(self.path)
        return doc

    def getFirestoreData(self):
        snap = self.getFirestoreDoc().get()
        if snap.exists:
            return snap.to_dict()
        return {}

    def get_dict(self):
        ret = {'id':self.id,'name':self.name,'path':self.path}
        return ret

class LoggingMessages(FireStoreBase):

    ext_fields = ['message','msg_type']

    def __init__(self,fsClient,**kwargs):
        self.message = kwargs.get('message','') #ndb.TextProperty(required=True)
        self.msg_type = kwargs.get('msg_type','') #ndb.StringProperty()
        super(LoggingMessages,self).__init__(fsClient,**kwargs)

    def base_path(self):
        return LoggingMessages.__basePath(self._fsClient)

    @classmethod
    def basePath(cls):
        return LoggingMessages.__basePath(LoggingMessages.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return 'application_data/'+inClient.company+'/Sales_Inventory/Converted/LoggingMessages'

    @classmethod
    def get_msg_type(cls, instr):
        if instr.lower().startswith("error"):
            return "ERROR"
        if instr.lower().startswith("warn"):
            return "WARNING"
        if instr.lower().startswith("info"):
            return "INFORMATIONAL"
        return instr

    @classmethod
    def create_log_message(cls, msg, msg_type):
        mType = LoggingMessages.get_msg_type(msg_type)
        data = {}
        data['msg_type'] = mType
        data['message'] = msg
        data['fs_docRef'] = LoggingMessages.get_firestore_client().collection(LoggingMessages.basePath()).document()
        lm = LoggingMessages(LoggingMessages.get_firestore_client(),**data)
        lm.update_ndb()
        return lm


'''
======================
--- Copied from other project ---
---- 2/15/20 ------
=======================
Created on Jan 21, 2018

@author: jason
'''

import re

def chunks(l, n):
    """Yield n number of striped chunks from l."""
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


'''
This is setup to replace variables in the json path returned for option variables
''' 
def replace_vars(entries):
    ret_entries = []
    for idx in range(len(entries)):
        upd_entry = replace_vars_one(entries[idx],idx)
        ret_entries.append(upd_entry)
    return ret_entries


def get_root_id(json_path):
    regex = r"^((\w*)\[\?\s*id\s*==\s*`(\d+)`\])"
    matches = re.finditer(regex, json_path)
    resp = {}
    for _,match in enumerate(matches):
        resp = {'model_name':match.group(2), 'id':int(match.group(3))}
        
    return resp
        
'''
Process and replace information in each value of the dictionary
where the pattern matches {{variable_name}},  
regex is (\{\{\s*(\w+)\s*\}\})

'''
def replace_vars_one(entry,item_num=None):
    for key in entry.keys():
        jp = entry[key]
        entry[key] = replace_values(jp,entry,item_num)
    return entry
   
def replace_values(path,dObj,item_num=None):
    if isinstance(path, str) and path.find("{{")>=0 and path.find("}}")>0:
        regex = r"(\{\{\s*(\w+)\s*\}\})"
        matches = re.finditer(regex,path)
        for _, match in enumerate(matches):
            if len(match.groups()) == 2 and match.group(2) in dObj.keys():
                path = path.replace(match.group(1),str(dObj[match.group(2)]))
            elif len(match.groups()) == 2 and match.group(2) == 'idx' and item_num != None:
                path = path.replace(match.group(1),str(item_num+1))
    return path

'''
Expect that the args will be passed are foo_id, where "foo" is the field name and value is the "id"
'''
def process_gen_args(in_args):
    ret_d = {}
    for key in in_args.keys():
        if key.endswith("_id"):
            name = key[:len(key)-3]
            name_id = in_args[key]
            ret_d[name] = int(name_id)
    ret_d['option_field'] = in_args.get('option_field',None)
    
    return ret_d
'''
As of 3/4/2018 I need to revamp... 

The pass in will now be a long string separated by dashes.. i.e.
32432-3351-9911, would be 3 numbers 32432, 3351, 9911

that will be passed as ancestry_list

if the ancestry_list argument is there... thne it is a TypeListing, otherwise TypeDisplay

'''
def process_args(in_args):
    ret_d = {'ancestry_list':[],'ancestry_names':[],'page_type':'TypeListing'}
    if 'ancestry_list' in in_args.keys():
        ret_d['page_type'] = 'TypeDisplay'
        parts = in_args['ancestry_list'].split("-")
        for part in parts:
            ret_d['ancestry_list'].append(part)
            
    if 'ancestry_names' in in_args.keys():
        parts = in_args['ancestry_names'].split("-")
        for part in parts:
            ret_d['ancestry_names'].append(part)
        
    return ret_d
'''
if the string starts with "id_" return the int version after that
None otherwise
'''
def parse_id(id_path):
    if id_path.find("id_") == 0:
        return int(id_path[3:])
    return None

'''
Will return list of matches and then a list of lists for groups
'''
def process_regex(regex, reStr):
    
    ret_re = {'matches':[], 'groups':[]}
    matches = re.finditer(regex, reStr)

    for _, match in enumerate(matches):
        ret_re['matches'].append(match.group())
        g = []
        for groupNum in range (0, len( match.groups())):
            g.append(match.group(groupNum+1))
        ret_re['groups'].append(g)
    return ret_re

'''
Replace the old option container... for something new
'''
def replace_op_container(option_path):
    regex = r"\?option_name == '(.*)']"
    match = re.search(regex,option_path)
    if match:
        return match.group(1)
    return None

'''
process the path from update_data and page_data
'''
def process_path(in_path, data=None):
    resp_d = {'root':None,
              'parent':None,
              'base':None}
    
    part_d = {0:'root',1:'parent',2:'base'}
    
    path_parts = in_path.split("/")
    n_pts = len(path_parts)
    
    if n_pts > 0:
        i = 0
        p = 0
        while i < n_pts:
            if p > 2:
                break
            name = path_parts[i]
            data_id = None
            if (i+1) < n_pts:
                data_id = parse_id(path_parts[i+1])
            resp_d[part_d[p]] = {'name':name,'id':data_id}
            i += 1
            p += 1
            if data_id:
                i += 1
        if data:
            p = p - 1
            resp_d[part_d[p]]['data'] = data
    return resp_d


class Email(object):

    def __init__(self):
        ''' hey there I send emails '''
        self.sender = None
        self.subject = None
        self.receivers = []
        self.body = None
        self.html = None
        self.signer = str(datetime.now()).replace("-","").replace(":","").replace(" ","").replace(".","")
        self.api_key = os.environ.get('MJ_API_KEY', None)
        self.api_secret = os.environ.get('MJ_API_SECRET', None)
        if self.api_key is None or self.api_secret is None:
            raise Exception(
                "Cannot setup mail client without the key or the secret")
        self.mailjet = Client(
            auth=(self.api_key, self.api_secret), version='v3.1')

    def send(self):
        if not self.sender:
            raise Exception("You must set the sender")

        if not self.subject:
            raise Exception("You did not set the subject")

        if len(self.receivers) == 0:
            raise Exception("You must have at least 1 receiver")

        if not self.body and not self.html:
            raise Exception("You need a text body or an html body")

        data = self.__create_data()
        result = self.mailjet.send.create(data=data)
        if not result.status_code == 200:
            raise Exception("None 200 status ({}), message: {}".format(
                str(result.status_code), str(result.json())))
        return result.json()

    def __create_data(self):
        to_array = [{"Email":x,"Name":x.split("@")[0]} for x in self.receivers]
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": self.sender,
                        "Name": self.sender.split("@")[0]
                    },
                    "To": to_array,
                    "Subject": self.subject,
                    "TextPart": self.body,
                    "HTMLPart": self.html,
                    "CustomID": self.subject+"_"+self.signer
                }
            ]
        }

        return data

class UploadItemData(object):

    instance = None
    PROD_BUCKET = 'prod_analytics_supply_upload_data'
    DEV_BUCKET = 'analytics_supply_upload_data'

    upload_bucket = {'backend-firestore-test':DEV_BUCKET,'colororchids-apss':PROD_BUCKET }

    def __init__(self):
        self.client = FirestoreClient.getInstance()
        self.bucket = self.upload_bucket.get(self.client.project,UploadItemData.PROD_BUCKET)

    @classmethod
    def getInstance(cls):
        if UploadItemData.instance is None:
            UploadItemData.instance = UploadItemData()
        return UploadItemData.instance

    def upload_spreadsheet(self, upload_file,email):
        '''
        Need to convert this to use the new method for using Google Storage
        URL: https://googleapis.dev/python/storage/latest/client.html
        '''
        bucket = self.client.storeClient.bucket(self.bucket)
        prefix = str(datetime.now()).replace("-","").replace(":","").replace(" ","").replace(".","")+"_"
        tsFileName = prefix+upload_file.filename
        email_folder = email.replace("@","__at__").replace(".","__dot__")
        path = email_folder+"/"+tsFileName
        blob = bucket.blob(path)

        blob.upload_from_file(upload_file,content_type=upload_file.mimetype)
        uri = "gs://{}/{}".format(bucket.name,path)

        payload = {'filename':tsFileName,'blob_uri':uri, 'email':email}
        publish_message('processUpload','File Uploaded: '+tsFileName,payload)

        return uri

def EnvironSetup(environment):
    if environment is None:
        environment = os.environ.get('AS_APP_ENVIRONMENT','Development_Tracking')
        
    env = {'Production_Tracking': 
              {'CO':'Color_Orchids',
               'NM': 'Customer_Tracking',
               'AP': 'colororchids-apps'},
           'Development_Tracking':
              {'CO':'Color_Orchids',
               'NM': 'Customer_Tracking',
               'AP': 'backend-firestore-test'}}
    
    env_map = {'CO':'APP_FIRESTORE_COMPANY',
               'NM':'APP_FIRESTORE_NAME',
               'AP':'GOOGLE_CLOUD_PROJECT'}
    
    use_env = env.get(environment,env['Development_Tracking'])
    for key in use_env.keys():
        envName = env_map.get(key,'n/a')
        envValue = use_env[key]
        os.environ[envName] = envValue
        
