from .utils import FireStoreBase,replace_values,process_regex, replace_vars, replace_op_container
from .image import Image
from .data_storage_type import DataStorageType
from .data_number import DataNumber, DataNumberLookup
from .quick_storage import QuickStorage
import jmespath
import logging
from datetime import datetime
import re

advanced_pattern = re.compile(r"((?P<field_name>[^\[\]\?\s=<>!]+)\s*(?P<comparison>[=<>!]+)\s*[\'\`](?P<field_value>[^\[\]\?=<>!]+)[\'\`](\s*(?P<operator>[&|]+)\s*)*)")

class StorageBlob(FireStoreBase):
    '''
    make key_fields a computed propperty

    - key_fields: never updated from incoming data is pulled from the json object and string together with "|" as seperators
    - data:  this is the json object in its raw form
    - data_type:  this refers to the key name for the DataStorageType.storage_name, the data stored must adhere to that format
    '''

    COLLECTION_NAME = 'application_data'
    ext_fields = ['key_fields','data_number_lookup','data_type']
    CPI_FLDS = '{"Customer_Name": customer_name, "Customer_Id": customer_id, "Location_Name": location_name, "Location_Id": location_id, "Type":`Customer`,"Product_Name":Product_Name,"Item_Num":Cust_Item_Num,"plant_image":plant_image[0].image_url}'
    CPI = 'cust_plant_item.*.'+CPI_FLDS
    PI_FLDS = '{"Customer_Name": `master`, "Customer_Id": ``, "Location_Name": `master`, "Location_Id":   ``, "Type":`Master`,"Product_Name":Product_Name,"Item_Num":Item_Num,"plant_image":plant_image[0].image_url}'
    PI = 'plant_item.*.'+PI_FLDS

    TYPE_FIELDS = {}


    def __init__(self, fsClient, **kwargs):
        self.key_fields = kwargs.get('key_fields','') #ndb.StringProperty(required=True)
        self.data_number_lookup = kwargs.get('data_number_lookup','') #ndb.StringProperty()
        #self.data = ndb.JsonProperty()
        dType = ''
        if kwargs.get('fs_docRef',None) is not None: # Updated to pull the collection name... this should be the data type for a storage blog, this defaults if it isn't in the field
            if kwargs['fs_docRef'].parent:
                dType = kwargs['fs_docRef'].parent.id
        self.data_type = kwargs.get('data_type',dType) #ndb.StringProperty(required=True)  # Refers to the DataStorageType.storage_name
        self._non_data_fields = FireStoreBase.base_fields+['key_fields','data_number_lookup','data_type','fs_docRef','fs_docSnap']
        self._parent = None
        # This part of the code is designed to help load data passed in...
        # This part of the data is not hard coded but is defined by the schema layer...
        # It is not the job of this class to be the traffic cop on what gets stored
        keys = kwargs.keys()
        xtra_fields = [x for x in keys if x not in self._non_data_fields]
        extraDict = {}
        self._sb_fields = self._load_dst_fields()

        for k in xtra_fields:
            extraDict[k] = kwargs[k]
            if k not in self._sb_fields:
                self._sb_fields.append(k)

        self.update_data(extraDict)
        super(StorageBlob, self).__init__(fsClient, **kwargs)
        self._fields = self._fields + self._sb_fields

    def base_path(self):
        return StorageBlob.__basePath(self._fsClient)

    @classmethod
    def basePath(cls):
        return StorageBlob.__basePath(StorageBlob.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return StorageBlob.COLLECTION_NAME+'/'+inClient.company+'/'+inClient.application+'/StorageBlob'

    @classmethod
    def getInstance(cls,fsDocument):
        ref,snap = StorageBlob.getDocuments(fsDocument)
        docDict = snap.to_dict()
        if docDict is None:
            raise Exception("The document doesn't exist: "+ref.path)
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        return StorageBlob(StorageBlob.get_firestore_client(),**docDict)

    @classmethod
    def getInstanceByPath(cls,path):
        return StorageBlob.getInstance(StorageBlob.get_firestore_client().document(path))

    @classmethod
    def get_by_dnl(cls,dataNumberLookup):
        return DataNumberLookup.get_obj_by_dnl(dataNumberLookup,StorageBlob)

    def _load_dst_fields(self):
        dst = DataStorageType.get_dataStorageType(self.data_type)
        return list(dst._ext_storage_fields.keys())

    def get_id_ancestry(self,ndbKey, idString=""):
        '''
        Won't implement this... but will create get "get_parent_path"
        '''
        raise Exception('Method not implemented:  "get_id_ancestry", try calling "get_parent_path"')
        #idString = str(ndbKey.id()) + "-" + idString
        #if ndbKey.parent():
        #    return self.get_id_ancestry(ndbKey.parent(), idString)
        #else:
        #    return idString[:-1]

    def get_parent_path(self):
        '''
        Use this instead of the standard path
        '''
        path = self.parent_path
        return path.replace(StorageBlob.basePath,'')

    def get_parent(self):
        if self._parent is None:
            parColl = self._documentRef.parent
            if not parColl == "" and parColl.parent.id != 'StorageBlob':
                self._parent = StorageBlob.getInstance(parColl.parent)

        return self._parent
    
    def get_custom_dict(self,lookupDict):
        '''
        If you need a custom dictionary, send in this request

        Parameters
        ----------
            lookupDict : list(dict)
                key_name : str
                    The name of the key for the field
                key_value : str
                    The actual field name
        '''
        respDict = {}
        for lookupEntry in lookupDict:
            if 'key_name' not in lookupEntry.keys():
                raise Exception("Invalid request was made to get_custom_dict in StorageBlob")
            fieldName = lookupEntry['key_name']
            fieldValue = getattr(self,lookupEntry.get('key_value',fieldName),None)
            respDict[fieldName] = fieldValue
        return respDict

    def get_sb_data(self):
        '''
        They dynamic fields are no longer going to be stored in "data"... we'll put it with all else...
        So this method is just to get the fields that would have been in "data"
        '''
        #fields = self.__dict__
        #data = {k:v for k,v in fields.items() if k not in self._non_data_fields and not k.startswith("_") and not k.startswith("fs_")}
        #data['id'] = self.data_number_lookup
        #return data
        return self.get_dict()
        

    @classmethod
    def get_dnl_list(cls,storage_name, jmespathSearch=None):
        q = StorageBlob.get_firestore_client().collection_group(storage_name)
        #q = StorageBlob.query(StorageBlob.data_type == storage_name)
        hits = {storage_name:[]}
        for sbsSnap in q.stream():
            sbs = StorageBlob.getInstance(sbsSnap)
            sbData = sbs.get_sb_data()
            if jmespathSearch:
                sbData = jmespath.search(jmespathSearch, sbData)

            hits[storage_name].append({'_id':sbs.data_number_lookup,'data':sbData})
        return hits

    @classmethod
    def get_by_urlkey(cls, urlkey):
        raise Exception('Method not implemented:  "get_by_urlkey", try calling "StorageBlob.get_storageBlob"')

    @property
    def id(self):
        return self.data_number_lookup

    @classmethod
    def get_storageBlob(cls,path):
        return StorageBlob.getInstance(StorageBlob.get_firestore_client().document(path))

    @classmethod
    def get_SB_from_Collection(cls,parent_id,model_name):
        docRefs = []
        if parent_id is not None and parent_id != '':
            docRefs = DataNumberLookup.get_doc_children(parent_id,model_name)
        else:
            sbPath = StorageBlob.basePath()+'/'+model_name
            collection = StorageBlob.get_firestore_client().collection(sbPath)
            docRefs = collection.list_documents()
        
        return [StorageBlob.getInstance(docRef) for docRef in docRefs]

    @classmethod
    def getSB_of_Type(cls,storageName):
        grp = StorageBlob.get_firestore_client().collection_group(storageName)
        grpList = []
        for sbSnap in grp.stream():
            grpList.append(StorageBlob.getInstance(sbSnap))
        return grpList


    '''
            Here is a method I thought I'd never write... something specific for data that is located in the data element..

            but hey... I'll figure it out later (on how to make it platform compliant)

            :return:
    '''
    @classmethod
    def get_all_plant_items(cls,use_cache=True):
        resp = cls._get_api_qs_data()
        if resp and use_cache:
            return resp

        logging.info("Cached results not found for plant info... pulling data.. (USE CACHE: "+str(use_cache)+")")
        arr_resp = []

        mstr_path = 'application_data/Color_Orchids/Customer_Tracking/StorageBlob/admin_items/admin_items-100/master_items'
        pi = StorageBlob.get_firestore_client().collection(mstr_path)
        docs = pi.list_documents()
        docRefs = [doc for doc in docs]
        print("Found: "+str(len(docRefs))+" master items..." )
        for docRef in docRefs:
            arr_resp.append(StorageBlob.getInstance(docRef)._render_api_summary(cpi=False))

        pi = StorageBlob.get_firestore_client().collection_group('items')
        snps = [snap for snap in pi.stream()]
        print("Found: "+str(len(snps))+" customer plant items..." )
        for sbSnap in snps:
            arr_resp.append(StorageBlob.getInstance(sbSnap)._render_api_summary(cpi=True))

        cls._set_api_qs_data(arr_resp)

        return arr_resp
    
    @classmethod
    def _get_api_qs_data(cls):
        allKey = 'ALL_PLANT_ITEMS'
        qsEntries = QuickStorage.getValue('ALL_PLANT_ITEMS')
        if qsEntries is None:
            return None
        resp = []
        for qsEntry in qsEntries:
            entryValue = QuickStorage.getValue(qsEntry)
            if entryValue is not None:
                resp = resp + entryValue
        return resp
    
    @classmethod
    def _set_api_qs_data(cls,responses):
        allKey = 'ALL_PLANT_ITEMS'
        count = 0
        qsArr = []
        qsKeys = []
        qsKey = allKey+str(count).zfill(5)
        for response in responses:
            if len(qsArr) >= 300:
                qsKeys.append(qsKey)
                QuickStorage.setValue(qsKey,qsArr,expireMins=1380)
                qsKey = allKey+str(count).zfill(5)
                qsArr = []
            qsArr.append(response)
            count += 1
        if len(qsArr) > 0:
            QuickStorage.setValue(qsKey,qsArr,expireMins=1380)
            qsKeys.append(qsKey)
        QuickStorage.setValue(allKey,qsKeys,expireMins=1380)

    @classmethod
    def __render_array_response(cls,dict_resp):
        arr1 = jmespath.search(StorageBlob.CPI, dict_resp)
        if not arr1:
            arr1 = []
        arr2 = jmespath.search(StorageBlob.PI, dict_resp)
        if not arr2:
            arr2 = []
        resp = arr1 + arr2
        return resp

    @classmethod
    def get_plant_item(cls, item_number):
        #dnl = StorageBlob.get_firestore_client().document(DataNumberLookup.basePath()+'/'+item_number)
        sb = StorageBlob.get_by_dnl(item_number)
        if not sb.exists:
            return None

        return sb.get_plant_item_data()
    
    def _render_api_summary(self,cpi=True):
        apiData = self.get_plant_item_data()
        r = None
        if cpi:
            r = jmespath.search(StorageBlob.CPI_FLDS,apiData)
        else:
            r = jmespath.search(StorageBlob.PI_FLDS,apiData)
        return r


    def get_plant_item_data(self):
        pi_data = self.get_sb_data()

        pi_images = pi_data.get('plant_image',[])
        pi_data['plant_image'] = [] if len(pi_images) == 0 else pi_images
        par = self.get_parent()
        if par and par.data_type == 'location':
            self.get_plant_ancestor_info(pi_data)

        return pi_data

    def get_children_by_type(self, dataType):
        childrenRefs = self._documentRef.collection(dataType).list_documents()
        sbList = [StorageBlob.getInstance(ref) for ref in childrenRefs]
        return sbList

    def get_plant_ancestor_info(self,in_data):
        par_sb = self.get_parent()  # Should be the location
        in_data['location_name'] = par_sb.get_sb_data().get('location_name', '')
        in_data['location_id'] = par_sb.get_sb_data().get('location_number', '')

        if par_sb.get_parent().exists and par_sb.get_parent().data_type == 'customer':
            gr_par_sb = par_sb.get_parent() # should be the customer
            in_data['customer_name'] = gr_par_sb.get_sb_data().get('customer_name', '')
            in_data['customer_id'] = gr_par_sb.get_sb_data().get('customer_number', '')
        else:
            logging.error("An entry didn't have a customer??... not expected")
            logging.error("Key: "+str(par_sb.path))

    def get_ancestry_ids(self):
        #return self.get_id_ancestry(self.key)
        raise Exception('Method not implemented:  "get_ancestry_ids", try calling "get_parent_path"')

    def get_ancestry_list(self):
        '''
        Returns the list of ids that are the ancestors of this entry

        if 3 entries are returned here is what that means
        [33333,22222,11111]
        - 11111 = The id of this entry
        - 22222 = The id of the parent
        - 33333 = The id of the grandparent
        '''
        #idString = self.get_id_ancestry(self.key)
        #return idString.split("-")
        raise Exception('Method not implemented:  "get_ancestry_list", try calling "get_parent_path"')

    def get_parent_id(self):
        '''
        Returns the id of the parent !! update 2/14.. now gets the "path"
        '''
        return self.get_parent_path

    '''
    This method is intended to be called for the root element,
    but it should work for any
    If root_id is None, then this is the root
    '''
    def get_full_data(self):
        schema = DataStorageType.get_dataStorageType(self.data_type).get_dict()
        for field in schema['fields']:
            if field.get('field_type',None) == 'group':
                grpFldName = field.get('field_name','bar')
                collRef = self.reference.collection(field['group_name'])
                qry = collRef.list_documents()
                grFlds = []
                for docRef in qry:
                    sbs = StorageBlob.getInstance(docRef)
                    grFlds.append(sbs.get_full_data())

                if len(grFlds)>0:
                    if field.get('repeated',False):
                        self.data[grpFldName] = grFlds
                    else:
                        self.data[grpFldName] = grFlds[0]
        data = self.get_sb_data()
        return data

    @classmethod
    def update_option_data(cls, option_type, option_update, doDelete=False):
        '''
        Update the option data
        '''
        qsKey = "options_data__"+option_type
        results = QuickStorage.getValue(qsKey)
        if results:
            dnl = option_update['data_number_lookup']
            item = jmespath.search(option_type+"[?id == '"+dnl+"'] | [0]",results)
            if item:
                if doDelete:
                    results[option_type].remove(item)
                else:
                    item.update(StorageBlob.__convert_to_lookup(option_type,StorageBlob(None,**option_update)))
            else:
                if not doDelete:
                    entry = StorageBlob.__convert_to_lookup(option_type,StorageBlob(None,**option_update))
                    results[option_type].append(entry)
                    
            QuickStorage.setValue(qsKey,results,1080,True)

    @classmethod
    def __convert_to_lookup(cls, option_type, input):
        rc = True if option_type == 'recipe_costing' else False
        entry = {}
        entry['name'] = input.item_type if rc else input.option_name
        entry['label'] = input.name if rc else input.option_value
        entry['value'] = input.data_number_lookup + '|' + input.name if rc else input.option_value
        entry['id'] = input.data_number_lookup
        entry['status'] = input.status if rc else 'Active'
        return entry

    @classmethod
    def get_all_option_data(cls, option_type, forceReload=False):
        '''
        Decided on 3/23/2020 to pull all option data and then update the jmespath to grab the options as needed
        
        1.  Cuts down on chattiness of the app
        2.  Can maintain a quick storage lookup
        3.  Easier to clean up if there are updates to recipe_costing and options

        return structure will be:
        array of this for "options"
        { 'name': 'upc_location',  //  "option_name"
          'label': 'Side of Pot',  // this is what shows in the drop down "option_value
          'value': 'Side of Pot',  // this is what actually gets saved "option_value"
          'id': 'options-100'}

        array of this for "recipe_costing"
        { 'name': 'Box',  // mapped from "item_type"
          'label': 'Standard 30', // mapped from "name"
          'value': 'recipe_costing-102|Standard 30', // mapped from data_number_lookup + "|" + name
          'id': 'recipe_costing-102'
        }
        '''
        qsKey = "options_data__"+option_type
        if not forceReload:
            results = QuickStorage.getValue(qsKey)
            if results:
                return results
            else:
                logging.warn("no options available in quick storage for "+option_type+".. loading..")
        else:
            logging.warn("being forced to reload options... for type: "+option_type)

        results = {option_type:[]}
        sbPath = StorageBlob.basePath()+'/'+option_type
        collRef = StorageBlob.get_firestore_client().collection(sbPath)
        docRefs = collRef.list_documents()
        sbList = [StorageBlob.getInstance(ref) for ref in docRefs]
        for sb in sbList:
            entry = StorageBlob.__convert_to_lookup(option_type, sb)
            addRc = option_type == 'recipe_costing' and sb.status == 'Active' and not sb.soft_delete
            addOp = option_type != 'recipe_costing' and not sb.soft_delete
            if addRc or addOp:
                results[option_type].append(entry)

        QuickStorage.setValue(qsKey,results,1080,True)
        return results



    @classmethod
    def get_option_data(cls, in_args):
        '''
        TODO Add in Simple (match a column to a value), to Advanced JMESPATH (both use jmespath under the hood).. so you can match a value and "active == true'

        Adding a 3rd way to do this... since I have no idea what I was thinking when I originally wrote this... sorry.  This is describing what will be found in the option_container

        psst... thinking I should send the option container... already have it don't I??

        Basically:  The assumption is that there is a DataStorageType and you need to pass that as well as the field name that will tell you how to look up the options
        For example  options.name.

        So to do this, you just need to pass the following to get all the valid storage fields that match the value 'dude' in the field 'name':
         --> SelectSimple:options.name:dude:business_type

         --> SelectAdv:options[?name == dude && ?active == true].business_type

        == SelectSimple ==
        How is that for simplicity.  The SimpleSimple tells this code that we're using the new and improved way of doing this.

        Expected:  SelectSimple:options.name:dude:item_name:false
        Broken down:  <Type>:<StorageName>.<FieldName>:<MatchValue>:<ItemSelect>:<IncludeId>  (last one is optional, default is False)

        ===================

        == SelectAdv ==
        Now for advanced cases.

        Expected:  SelectAdv:options[?name == dude && ?active == true]:business_type
        Broken down:  <Type>:<StorageName>:<jmespath_expression>:<ItemSelect>:<IncludeId>  (last one is optional, default is False)
        ===================

        ====== 11/18/2018 =========
        Adding Memcache to cache the option data queries
        ===========================

        '''

        option_fld = in_args['option_field']
        option_cont = in_args.get('option_container',None)

        #cache_key = option_fld+"_|_"+option_cont

        opData = None # TODO (add redis) memcache.get(cache_key)

        if opData is None:
            opData = StorageBlob.retrieve_option_data(option_fld, option_cont)
            #memcache.set(cache_key,opData,DEFAULT_CACHE_TIME)

        return opData



    @classmethod
    def retrieve_option_data(cls,option_fld,option_cont):
        if option_cont is None and option_fld:
            # As of 11/12/2018, started passing this in the call (this = option_container)
            name, opFld = option_fld.split(".")
            opFld = DataStorageType.get_option_field(name, opFld)
            if opFld:
                option_cont = opFld.option_container
                if not option_cont or option_cont.lower() == "none" or option_cont == "":
                    return {}

        if option_cont.startswith("options"):
            # look up the options in the options table, using jmespath
            return StorageBlob.get_opdata_options(option_cont,option_fld)

        if option_cont.startswith('SelectSimple:'):
            # Do the new way
            return StorageBlob.get_optdata_selectsimp(option_cont)

        if option_cont.startswith('SelectAdv'):
            # Do the new advanced way
            return StorageBlob.get_opdata_selectadv(option_cont)
        else:
            # means we found a look up
            raise Exception("No option data can be retrieved a default method does not exist")
            #return StorageBlob.get_opdata_default()


    @classmethod
    def get_opdata_selectadv(cls,option_cont):
        '''
        Expected:  SelectAdv:options[?name == dude && ?active == true]:business_type
        Broken down:  <Type>:<StorageName>:<jmespath_expression>:<ItemSelect>:<IncludeId>  (last one is optional, default is False)
        '''

        parts = option_cont.split(":")
        storeName = parts[1]
        jPath = parts[2]
        selectField = parts[3]
        includeId = parts[4].lower() == 'true' if len(parts) > 4 else False

        return cls.query_with_jmespath(storeName,jPath,selectField,includeId)


    @classmethod
    def get_optdata_selectsimp(cls,option_cont):
        '''
        Expected:  SelectSimple:options.name:dude:item_name:false
        Broken down:  <Type>:<StorageName>.<FieldName>:<MatchValue>:<ItemSelect>:<IncludeId>  (last one is optional, default is False)
        '''

        parts = option_cont.split(":")
        storeName = parts[1].split(".")[0]
        fieldName = parts[1].split(".")[1]
        matchValue = parts[2]
        selectField = parts[3]
        includeId = parts[4].lower() == 'true' if len(parts) > 4 else False

        jPath = "[?"+fieldName+" == '"+matchValue+"']"

        return cls.query_with_jmespath(storeName,jPath,selectField,includeId)

    @classmethod
    def query_with_jmespath(cls,storeName, jmPath, selectField, includeId):
        '''
        All option data will be at the base level... so no need to do a collection group
        '''

        where_stmts = StorageBlob.parse_jmespath(jmPath)
        sbPath = StorageBlob.basePath()+'/'+storeName
        hits = []
        qry = StorageBlob.get_firestore_client().collection(sbPath)
        for where in where_stmts:
            qry = qry.where(where['field'],where['compare'],where['value'])

        for sbsSnap in qry.stream():
            sbs = StorageBlob.getInstance(sbsSnap)
            d = sbs.get_sb_data()
            d['id'] = sbs.id
            hits.append(d)
            
        returnOptions = []

        cnt = 0
        for data in hits:
            cnt = cnt + 1
            option = {}
            value = data[selectField]
            option['json_path'] = '{}[?id == `{}`].{}'.format(storeName,str(data['id']),selectField)
            option['label'] = value
            option['option_id'] = str(data['id'])
            option['value'] = str(data['id']) +"|"+ value if includeId else value
            returnOptions.append(option)

        return returnOptions

    @classmethod
    def parse_jmespath(cls,jmespath_str):
        '''
        Regex is awesome... having named capture groups!!! seriously!!
        '''
        match_arr = []
        matches = advanced_pattern.finditer(jmespath_str)
        for _, match in enumerate(matches, start=1):
            m_dict = {'field':match.group('field_name'),'compare':match.group('comparison'),'value':match.group('field_value'),'operator':match.group('operator')}
            match_arr.append(m_dict)

        return match_arr 

    @classmethod
    def get_opdata_default(cls,option_cont, inArgs):
        #pArgs = app_utils.process_gen_args(in_args)
        #regex = r"^(.*)\[\?(\S+)\s*==\s*\?{3,}\]"
        regex = r"(^(\w+)\[\?id\s*==\s*`(\w+)`\])\."
        sbd = None

        srch = replace_values(option_cont, inArgs)
        results = process_regex(regex, srch)
        if results['groups'] and len(results['groups']) >= 0 and len(results['groups'][0]) >= 0:
            srch = srch.replace(results['groups'][0][0],results['groups'][0][1])
            sbs = StorageBlob.get_by_dnl(int(results['groups'][0][2]))
            sbd = {sbs.data_type: sbs.get_full_data()}
        else:
            sbd = {}

        return replace_vars(jmespath.search(srch,sbd))

    @classmethod
    def get_opdata_options(cls,option_container,option_fld):
        opFld = None
        if len(option_fld.split(".")) > 1:
            _, opFld = option_fld.split(".")
        else:
            opFld = option_fld
            
        option_field = replace_op_container(option_container)
        qHits = QuickStorage.getValue(option_field)
        if qHits is not None:
            return qHits

        if option_field:
            opFld = option_field
        opCont = option_container.replace(' id,',' data_number_lookup')
        opCont = opCont.replace('[?id ==','[?data_number_lookup ==')
        #opCont = opCont.replace("`","'")       
        sbColl = StorageBlob.get_firestore_client().collection(StorageBlob.basePath()+'/options')
        qryRef = sbColl.where('option_name','==',opFld).where('soft_delete','==',False)
        sbd = {"options":[]}
        for doc in qryRef.stream():
            sbd['options'].append(doc.to_dict())
        
        results = replace_vars(jmespath.search(opCont,sbd))

        QuickStorage.setValue(option_field,results,360)
        return results

    def delete_resp(self):
        '''
        Lots of code but we needed to make sure things get cleaned up
        '''
        colls = self._documentRef.collections()
        resps = []
        for coll in colls:
            docRefs = coll.list_documents()
            sbList = [StorageBlob.getInstance(docRef) for docRef in docRefs]
            resps =  [sb.delete_resp() for sb in sbList] #Yes Recursion!!

        errs = ','.join([r['dnl'] for r in resps if not r['didDelete']])
        resp = {'status':'success','msg':'Deleted Successfully', 'didDelete':True}
        if errs == '':
            resp = super(StorageBlob,self).delete_resp()
            if not resp['didDelete']:
                logging.warn(resp['msg'])
        else:
            resp['didDelete'] = False
            resp['status'] = 'failed'
            resp['msg'] = 'Failed to delete.. ('+errs+')'

        resp['dnl'] = self.data_number_lookup
        if resp['didDelete']:
            DataNumberLookup.remove_dnl(self.data_number_lookup)
        
        return resp



    def get_dict(self,include_keys=True, addl_exclude=[]):
        return super(StorageBlob,self).get_dict(include_keys, addl_exclude=['key_fields'])
        #return self.get_sb_data()

    @property
    def data(self):
        return self.get_sb_data()

    def _pre_put_hook(self):
        raise Exception("Method not implemented: '_pre_put_hook'")


    def validate_data(self, dst=None, fill_missing = False):
        if not dst:
            dst = DataStorageType.get_dataStorageType(self.data_type)

        if not dst:
            raise Exception("The data storage name of: "+self.data_type+", does not exist")

        fields = dst._ext_storage_fields
        valResp = []
        blobKeys = self._fields
        for key in fields:
            field = fields[key]
            if key in blobKeys:
                if field.isDateAuto():
                    #self.data[key] = datetime.now().isoformat(' ')
                    setattr(self,key,datetime.now().isoformat(' '))
                r = field.validate_value(getattr(self,key,''))
                if not r['valid']:
                    valResp = valResp + r['messages']
            else:
                if fill_missing and not field.isAutoInc() and not field.isReadOnly() and field.field_default:
                    if field.isDateAuto():
                        #self.data[key] = datetime.now()
                        setattr(self,key,datetime.now())
                    else:
                        #self.data[key] = field.field_default
                        setattr(self,key,field.field_default)

        if len(valResp) > 0:
            logging.error(valResp)
            raise Exception("The update/create failed field validation ("+str(valResp)+")")
    '''
    Shouldn't have more than 1 auto_inc fields in a storagetype
    '''
    def create_steps(self):
        dst = DataStorageType.get_dataStorageType(self.data_type)

        self.validate_data(dst=dst,fill_missing=True)

        schema = dst.get_schema(get_extends=True)

        auto_field = jmespath.search("fields[?field_type == 'auto_inc'] | [0].field_name",schema)
        dnVal = None
        if auto_field:
            dnVal = self.data_number_lookup
            #self.data[auto_field] = dnVal
            setattr(self,auto_field,dnVal)

        return dnVal

    def update_sbobj(self,updateDict):
        '''
        Given a dictionary with updated data.. set this storage blob up and validate and save

        Parameters
        ----------
            updateDict : dict
                The key/value pair dictionary with fields to be updated
        '''
        self.update_data(updateDict)
        self.validate_data()
        self.update_ndb()


    @classmethod
    def create_blob_parent(cls, data_type, blob_data, parentId, collection=None):
        if parentId is None:
            raise Exception("This method is intended to create a storageblob under a parent... use a different method if you are creating from scratch")

        return StorageBlob.create_blob_parent_fromPath(data_type,blob_data,DataNumberLookup.get_path_for_dnl(parentId),collection)


    @classmethod
    def get_next_dnl(cls,data_type):
        return DataNumber.get_type_number(data_type)

    @classmethod
    def create_blob_parent_fromPath(cls, data_type, blob_data, par_path = None, collection = None):
        #parent_key = None
        #if par_path:
        #    parent_key = StorageBlob.create_key(idList)

        dst = DataStorageType.get_dataStorageType(data_type)

        if not dst:
            raise Exception("The data storage name of: "+data_type+", does not exist")
        
        clt = StorageBlob.get_client()
        docRef = None
        dnl = StorageBlob.get_next_dnl(data_type)
        if par_path:
            par_doc = clt.fsClient.document(par_path)
            collName = data_type if collection is None else collection
            collRef = par_doc.collection(collName)
            docRef = collRef.document(dnl)
        else:
            collRef = clt.fsClient.collection(StorageBlob.basePath()+'/'+data_type)
            docRef = collRef.document(dnl)

        blob_data['fs_docRef'] = docRef
        blob_data['data_number_lookup'] = dnl
        blob_data['data_type'] = data_type

        sb = StorageBlob(clt.fsClient,**blob_data)
        sb.create_steps()

        sb.update_ndb(True)

        DataNumberLookup.store_data_number_sbPath(dnl, docRef.path)

        return sb

    @classmethod
    def create_key(cls,idList):
        raise Exception("Method not implemented: 'create_key', we're just using the full path now")

    @classmethod
    def update_blob_parent(cls, blob_data, idList):
        raise Exception("Method not implemented: 'update_blob_parent', we're just using the full path now, so call update_blob_parent_fromPath")
        
    @classmethod
    def update_blob_parent_fromPath(cls, blob_data, full_path):
        docRef = StorageBlob.get_firestore_client().document(full_path)
        blob = StorageBlob.getInstance(docRef)
        if blob:
            blob.update_data(blob_data)
            blob.validate_data()
            blob.update_ndb()
            return blob.get_sb_data()
        return {'data_type':'','id':'','data':{}}