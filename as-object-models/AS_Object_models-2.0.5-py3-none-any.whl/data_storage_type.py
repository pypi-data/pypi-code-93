import copy
import jmespath
import logging
from datetime import datetime
from .utils import FireStoreBase


class DataStorageType(FireStoreBase):
    COLLECTION_NAME = FireStoreBase.DATA_STORAGE_TYPE
    DST_STORE = {}
    ext_fields = ['storage_name', 'isList', 'extends', 'storage_fields']
    logger = logging.getLogger("DataStorageType")

    def __init__(self, fsClient, **kwargs):
        # ndb.StringProperty(required=True)
        self.storage_name = kwargs.get('storage_name', '')
        # ndb.BooleanProperty(default=False)
        self.isList = kwargs.get('isList', '')
        # ndb.StringProperty(default="None")
        self.extends = kwargs.get('extends', '')
        self.storage_fields = kwargs.get('storage_fields',[])
        self._storage_fields = {key:StorageField.getInstance(self.storage_fields[key]) for key in self.storage_fields}
        self.ext_storage_fields = self.__get_fields_dict(do_conv=False)
        self._ext_storage_fields = {key:StorageField.getInstance(self.ext_storage_fields[key]) for key in self.ext_storage_fields}
        super(DataStorageType, self).__init__(fsClient, **kwargs)
        DataStorageType.DST_STORE[self.storage_name] = self

    def base_path(self):
        return DataStorageType.__basePath(self._fsClient)

    @classmethod
    def basePath(cls):
        return DataStorageType.__basePath(DataStorageType.get_client())

    @classmethod
    def __basePath(cls, inClient):
        return DataStorageType.COLLECTION_NAME+'/'+inClient.company+'/'+inClient.application

    @classmethod
    def getInstance(cls, fsDocument):
        ref, snap = DataStorageType.getDocuments(fsDocument)
        docDict = {}
        if snap.exists:
            storName = snap.get('storage_name')
            if DataStorageType.DST_STORE.get(storName, None) is not None:
                return DataStorageType.DST_STORE[storName]
            else:
                docDict = snap.to_dict()
                docDict['fs_docRef'] = ref
                docDict['fs_docSnap'] = snap
        else:
            docDict['fs_docRef'] = ref
        return DataStorageType(DataStorageType.get_firestore_client(), **docDict)

    @classmethod
    def get_all_field_containers(cls):
        dst_coll = DataStorageType.get_firestore_client().collection(DataStorageType.basePath())
        docRefList = dst_coll.list_documents()
        return [docRef.id for docRef in docRefList]

    def get_fields_by_category(self, category):
        return self.create_field_dict([x for x in list(self._ext_storage_fields.values()) if x.category == category])

    def __get_fields_dict(self, get_extends=True, do_conv=False):
        dstFields = self.storage_fields.copy()
        if do_conv:
            dstFields = self.create_field_dict(self._storage_fields)
        if self.extends and self.extends != "" and self.extends.lower().strip() != "none" and get_extends:
            dst = DataStorageType.get_dataStorageType(self.extends)
            if dst and dst.exists:
                dstFieldsInner = dst.__get_fields_dict(get_extends, do_conv)
                dstFieldsInner.update(dstFields)
                dstFields = dstFieldsInner
        return dstFields

    def get_field(self, field_name):
        '''
        Returns dict of field
        '''
        return self.ext_storage_fields.get(field_name,None)
    
    def get_storage_field(self,field_name):
        '''
        Returns instance of StorageField
        '''
        return self._ext_storage_fields.get(field_name,None)

    def get_fields(self, get_extends=True):
        # return self.get_fields_dict(get_extends)
        if get_extends:
            return self.ext_storage_fields
        return self.storage_fields
        

    def get_storage_fields(self,get_extends=True):
        if get_extends:
            return self._ext_storage_fields
        return self._storage_fields

    def create_field_dict(self, fields):
        if isinstance(fields, dict):
            if fields.get('field_name', None) is None:
                # means the keys are the field names... as we want it
                return fields
            # we need to create the field_name as the key
            return {fields['field_name']: fields}

        # So now we have an array of data
        fld_d = {}
        for fld in fields:
            fld_d[fld.field_name] = fld

        return fld_d

    def save_storage_name(self):
        self.update_ndb()
        self.clean_up_storage()
        
    def clean_up_storage(self):
        if DataStorageType.DST_STORE.get(self.storage_name,None):
            del DataStorageType.DST_STORE[self.storage_name]
        
        collRef = DataStorageType.get_firestore_client().collection(DataStorageType.basePath())
        q = collRef.where("extends","==",self.storage_name)
        dstList = [DataStorageType.getInstance(x) for x in q.stream()]
        if dstList and len(dstList) > 0:
            [x.clean_up_storage() for x in dstList]


    @classmethod
    def get_dataStorageType(cls, storageName):
        dst = DataStorageType.DST_STORE.get(storageName,None)
        if dst is None:
            dstPath = DataStorageType.basePath()+'/'+storageName
            docRef = DataStorageType.get_firestore_client().document(dstPath)
            dst = DataStorageType.getInstance(docRef)
        return dst

    @classmethod
    def getAll_DSTNames(cls):
        collRef = DataStorageType.get_firestore_client().collection(DataStorageType.basePath())
        dstList = []
        docRefList = collRef.list_documents()
        for docRef in docRefList:
            dstList.append(DataStorageType.getInstance(docRef).storage_name)

        return dstList

    @classmethod
    def getAll_DST(cls):
        collRef = DataStorageType.get_firestore_client(
        ).collection(DataStorageType.basePath())
        dstList = []
        docRefList = collRef.list_documents()
        for docRef in docRefList:
            dstList.append(DataStorageType.getInstance(docRef))

        return dstList

    @classmethod
    def get_option_field(cls, name, opFld):
        dst = DataStorageType.get_dataStorageType(name)
        if dst.exists:
            return dst.get_field(opFld)
        return None

    @classmethod
    def addStorageFields(cls, storeName, flds):
        dst = DataStorageType.get_dataStorageType(storeName)
        dst.add_storage_fields(flds)
        return dst

    def add_storage_fields(self, flds):
        self.update_from_dict(flds)
        self.save_storage_name()

    @classmethod
    def removeStorageFields(cls, storeName, flds):
        dst = DataStorageType.get_dataStorageType(storeName)
        dst.remove_storage_fields(flds)
        return dst

    def remove_storage_fields(self, flds):
        #remFlds = self.create_field_dict(flds)
        remFlds = [fld['field_name'] for fld in flds]
        for remFld in remFlds:
            del self._storage_fields[remFld]

        self.update_fields()
        self.save_storage_name()

    @classmethod
    def getFieldsDict(cls, storeName):
        dst = DataStorageType.get_dataStorageType(storeName)
        if dst:
            return dst.storage_fields
        return {}

    @classmethod
    def get_dst(cls, model_name):
        dst = DataStorageType.get_dataStorageType(model_name)
        return dst

    @classmethod
    def save_or_update(cls, update_data):
        dst = DataStorageType.get_dataStorageType(update_data['model_name'])

        dst.isList = update_data.get('repeating', 'false').lower() == 'true'
        dst.extends = update_data.get("extending", "None")

        upData = {}

        for datum in update_data.get('data', []):
            fldName = datum.get('field_name', None)
            if fldName is None:
                logging.debug("skipping field due to missing field name")
            else:
                upDatum = {}
                for k in datum.keys():
                    if k in ['field_id', 'field_name', 'group_name', 'field_type', 'is_list',
                          'field_default', 'is_key_field', 'field_required',
                          'is_option_filled', 'option_container', 'field_order']:
                        upDatum[k] = datum[k]
                upData[fldName] = upDatum
        dst.update_from_dict(upData)
        dst.save_storage_name()

    def update_fields(self):
        fldNames = self._storage_fields.keys()
        fldList = [self._storage_fields[x].get_dict() for x in fldNames]
        self.storage_fields = {x['field_name']: x for x in fldList}

    def update_from_dict(self, inFlds, save=False):
        inputFields = self.create_field_dict(inFlds)
        fieldNames = inputFields.keys()
        for fieldName in fieldNames:
            field = inputFields[fieldName]

            if isinstance(field, StorageField):
                field = field.get_dict()

            if field.get('field_name', None) is None:
                raise Exception(
                    "Can not update storage field without field 'field_name'... get IT RIGHT!!!")

            sf = self._storage_fields.get(field['field_name'], None)
            if sf:
                sf.update_from_dict(field)
            else:
                sf = StorageField(**field)
                self._storage_fields[field['field_name']] = sf

        self.update_fields()
        if save:
            self.save_storage_name()

    def get_schema(self, get_extends=False):
        '''
        by default will not return the extended fields
        '''
        base = copy.deepcopy(self.get_dict())
        fields = self._ext_storage_fields if get_extends else self._storage_fields

        for field in list(fields.values()):
            fieldDict = field.get_dict()
            if field.field_type == 'group':
                fieldDict = self.__get_group_info(fieldDict,True,get_extends)

            base['storage_fields'][field.field_name] = fieldDict

        base['fields'] = list(base['storage_fields'].values())

        return base

    def get_dict(self, include_keys=True, addl_exclude=[], get_extends=True):
        base = FireStoreBase.get_dict(self, include_keys=include_keys, addl_exclude=addl_exclude)

        fields = self.get_fields(get_extends)

        fldList = []
        if isinstance(fields,list):
            fldList = fields
        
        if isinstance(fields,dict):
            fldList = list(fields.values())

        group_fields = jmespath.search("[?field_type == 'group']", fldList)

        for field in group_fields:
            fields[field['field_name']] = self.__get_group_info(field,get_extends=get_extends)

        base['storage_fields'] = fields
        return base

    def __get_group_info(self, field, schema=False,get_extends=False):
        field['repeated'] = False
        grp = field.get('group_name', None)
        if not grp:
            grp = field['field_name']

        obj = DataStorageType.get_dataStorageType(grp)
        if obj:
            val = {}
            if schema:
                val = obj.get_schema(get_extends=get_extends)
                del val['isList']
                del val['storage_name']
            else:
                val = obj.get_dict(addl_exclude=['isList', 'storage_name'],get_extends=get_extends)

            if obj.isList:
                field['repeated'] = True
                field['is_list'] = True
            field['structure'] = val
        return field


class StorageField(object):
    '''
    Holds fields for the json blob
    types include
    string
    int
    boolean
    float
    currency (same as float but rendered like currency on the screen
    date
    datetime
    group
    list (an array of values)
    auto_inc
    image
    readonly
    '''

    @classmethod
    def getInstance(cls, data):
        return StorageField(**data)

    @classmethod
    def get_storageField(cls, storage_name, field_name):
        dst = DataStorageType.get_dataStorageType(storage_name)
        return dst.get_field(field_name)

    def __init__(self, **kwargs):
        self._parent = kwargs.get('parent', None)
        self.field_id = kwargs.get('field_id', '')  # ndb.StringProperty(default='')
        self.field_order = kwargs.get('field_order', '')  # ndb.StringProperty(default="1")
        self.category = kwargs.get('category', '')  # ndb.StringProperty(default="main")
        self.field_name = kwargs.get('field_name', '')  # ndb.StringProperty(required=True)
        self.group_name = kwargs.get('group_name', '')  # ndb.StringProperty(required=False,default=None)
        self.field_type = kwargs.get('field_type', '')  # ndb.StringProperty(required=True,default="string")
        self.is_list = kwargs.get('is_list', '')  # ndb.BooleanProperty(required=False, default=False)
        self.field_default = kwargs.get('field_default', '')  # ndb.StringProperty(default="")
        self.is_key_field = kwargs.get('is_key_field', '')  # ndb.BooleanProperty(default=False)
        self.field_required = kwargs.get('field_required', '')  # ndb.BooleanProperty(default=False)
        self.is_option_filled = kwargs.get('is_option_filled', '')  # ndb.BooleanProperty(default=False)
        self.description = kwargs.get('description', '')  # ndb.TextProperty(required=False,default="")
        self.option_container = kwargs.get('option_container', '')  # ndb.StringProperty(default="none") # this will always be a container
        self.parent_container = kwargs.get('parent_container', '')  # ndb.KeyProperty(kind=DataStorageType,required=False)

    def get_dict(self):
        d = {k: v for k, v in self.__dict__.items() if k != '_parent'}
        d['id'] = self.field_name
        return d

    def validate_value(self, inValue):
        valid_response = {"valid": True, "messages": []}

        if not self.check_filled(inValue):
            valid_response['valid'] = False
            valid_response['messages'].append(
                "The field ("+self.field_name + ") is either required or a key field and must have a value")

        if not self.valid_type(inValue):
            valid_response['valid'] = False
            valid_response['messages'].append(
                "The type of this field ("+self.field_type+") doesn't match the value: "+str(inValue)+", for field: "+self.field_name)

        return valid_response

    def check_filled(self, inValue):
        if self.field_required or self.is_key_field:
            if inValue.strip() == "" and not self.isAutoInc():
                return False

        return True

    def valid_type(self, inValue):
        if self.isAutoInc():
            return True
        if self.isDate() or self.isDatetime() or self.isDateAuto():
            return self.check_date(inValue)
        if self.isFloat() or self.isCurrency():
            return self.check_float(inValue)
        if self.isBoolean():
            return self.check_boolean(inValue)
        if self.isInt():
            return self.check_int(inValue)

        return True

    def check_float(self, inValue):
        if inValue is None or str(inValue).strip() == "":
            return True
        #try:
        #    float(inValue)
        #    return True
        #except:
        #    return False
        return DataStorageType.CheckFloat(str(inValue))

    def check_image(self, inValue):
        ''' Return True if it is empty or null '''
        if inValue and inValue.strip(" ") != "":
            if str(inValue).startswith("image-"):
                return True
            else:
                return False
        else:
            return False

    def check_boolean(self, inValue):
        if isinstance(inValue, bool):
            return True

        if (inValue is None or str(inValue).strip() == ""):
            if self.field_required:
                return False
            else:
                return True

        if (inValue is not None and len(str(inValue)) > 0):
            if str(inValue).lower() == 'n/a': # saying that this field is not applicable
                return True

            if (inValue == True or inValue == False or str(inValue).lower() == "true" or
                    str(inValue).lower() == "false" or inValue == 1 or inValue == 0 or inValue == "1" or inValue == "0"):
                return True
            else:
                return False
        return False

    def check_int(self, inValue):
        if inValue is None or str(inValue).strip() == "":
            return True
        try:
            int(inValue)
            return True
        except:
            return False

    def check_date(self, inValue):
        if not inValue or inValue.strip() == "":
            return True
        if type(inValue) is not datetime:
            try:
                datetime.strptime(inValue, '%Y-%m-%d')
                return True
            except:
                try:
                    datetime.strptime(inValue, "%Y-%m-%d %H:%M:%S.%f")
                    return True
                except:
                    return False
        return True

    @classmethod
    def get_parent(cls, parent_key):
        raise Exception("method not implemented")

    @classmethod
    def get_field(cls, parent_key, fieldName):
        '''
        parent_key is the parent document
        the collection that all fields are in is called 'storage_fields'
        So given a parent called "customer" and a field name "customer_name"
        ... the path is '/data_schemas/customer/storage_fields/customer_name'
        '''
        return StorageField.get_storageField(parent_key, fieldName)

    @classmethod
    def update_field(cls, parent_key, fieldInfo):
        '''
         Passing in a dictionary for updating...

        '''
        dst = DataStorageType.get_dataStorageType(parent_key)
        dst.update_from_dict({fieldInfo.get('field_name', None): fieldInfo},True)

    def update_from_dict(self, fieldInfo, save=True):
        self.field_order = fieldInfo.get('field_order', self.field_order)
        self.category = fieldInfo.get('category', self.category)
        self.group_name = fieldInfo.get('group_name', self.group_name)
        self.field_type = fieldInfo.get('field_type', self.field_type)
        self.is_list = fieldInfo.get('is_list', self.is_list)
        self.field_default = fieldInfo.get('field_default', self.field_default)
        self.is_key_field = fieldInfo.get('is_key_field', self.is_key_field)
        self.field_required = fieldInfo.get(
            'field_required', self.field_required)
        self.is_option_filled = fieldInfo.get(
            'is_option_filled', self.is_option_filled)
        self.description = fieldInfo.get('description', self.description)
        self.option_container = fieldInfo.get(
            'option_container', self.option_container)

    def eval_value(self, key, val):
        if key == 'field_type':
            if val == "group":
                ''' process a data storage type '''
                grp = self.getGroupName()
                obj = DataStorageType.get_dataStorageType(grp)

                val = obj.get_dict(addl_exclude=['isList', 'storage_name'])
                if obj.isList:
                    val = [val]
                return val
        return val

    def getGroupName(self):
        if self.group_name and len(self.group_name) > 1:
            return self.group_name
        return self.field_name

    def isString(self):
        return self.field_type == "string"

    def isReadOnly(self):
        return self.field_type == "readonly"

    def isInt(self):
        return self.field_type == "int"

    def isFloat(self):
        return self.field_type == "float" or self.field_type == "currency"

    def isCurrency(self):
        return self.field_type == "currency"

    def isDate(self):
        return self.field_type == "date" or self.field_type == "datetime"

    def isDatetime(self):
        return self.field_type == "datetime"

    def isDateAuto(self):
        return self.field_type == "dateauto"

    def isImage(self):
        return self.field_type == "image"

    def isList(self):
        return self.is_list

    def isBoolean(self):
        return self.field_type == "boolean"

    def isGroup(self):
        return self.field_type == "group"

    def isAutoInc(self):
        return self.field_type == "auto_inc"
