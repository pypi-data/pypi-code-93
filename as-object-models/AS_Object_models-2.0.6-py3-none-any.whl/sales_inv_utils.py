from datetime import datetime
from .utils import FireStoreBase

from .quick_storage import QuickStorage
from .storage_blob import StorageBlob
from .data_storage_type import StorageField
from .data_number import DataNumber, DataNumberLookup

class SalesInvBase(FireStoreBase):

    def _get_sb_by_dnl(self,inId):
        return SalesInvBase.GetSbByDNL(inId)

    @classmethod
    def GetSbByDNL(cls, inId):
        return StorageBlob.get_by_dnl(inId)
    
    def _get_sb_instance_by_path(self,path):
        return SalesInvBase.GetSbInstanceByPath(path)
    
    @classmethod
    def GetSbInstanceByPath(cls,path):
        return SalesInvBase.GetSBObj(path)

    def _get_doc_id(self, storeName):
        return SalesInvBase.GetNextDNL(storeName)

    def _insert_dnl(self, docRef):
        DataNumberLookup.create_dnl(docRef)

    def _delete_by_dnl(self,dnl):
        return DataNumberLookup.delete_obj_by_dnl(dnl)

    @classmethod
    def GetSBObj(cls,path):
        return StorageBlob.getInstanceByPath(path)
    
    @classmethod
    def GetSB(cls,docRef):
        return StorageBlob.getInstance(docRef)

    @classmethod
    def GetSBObjByDNL(cls,dnl):
        return SalesInvBase.GetByDNL(dnl,StorageBlob)


    @classmethod
    def AddDNL(cls,dnl, path):
        return DataNumberLookup.store_data_number_sbPath(dnl,path)
        
    @classmethod
    def GetNextDNL(cls,inName):
        dn = DataNumber.createInstance(inName)

        dn.number = dn.number + 1
        dn.update_ndb()
        retNum = str(datetime.now()).replace("-","").replace(":","").replace(" ","").replace(".","")[:18] + str(dn.number)
        return inName+"-"+retNum

    @classmethod
    def DeleteByDNL(cls,dnl):
        return DataNumberLookup.delete_obj_by_dnl(dnl)

    @classmethod
    def GetActive(cls,collectionName, clzz):
        cg = SalesInvBase.get_firestore_client().collection_group(collectionName)
        q = cg.where('soft_delete','!=','true')
        objArr = []
        for snap in q.stream():
            if clzz:
                clsObj = clzz.getInstance(snap)
                objArr.append(clsObj)
            else:
                d = snap.to_dict()
                d['id'] = snap.id
                objArr.append(d)
        
        return objArr


    @classmethod
    def GetByDNL(cls,dnl,clzz):
        return DataNumberLookup.get_obj_by_dnl(dnl,clzz)

    def _get_cust_info(self,customer):
        return SalesInvBase.GetCustInfo(customer)
    
    @classmethod
    def GetCustInfo(cls,customer):
        return {'id':customer.id,
        'name':customer.customer_name,
        'path':customer.path,
        'type':'Item_Tracking'}

    def _get_item_info(self,item):
        return SalesInvBase.GetItemInfo(item)

    @classmethod
    def GetItemInfo(self,item):
        return {'id':item.id,
        'name':item.Product_Name,
        'path':item.path,
        'type':'Item_Tracking'}

    def _get_loc_info(self,location,defLoc=None):
        return SalesInvBase.GetLocInfo(location,defLoc)

    @classmethod
    def GetLocInfo(cls,location,defLoc=None):
        return {'id':location.id,
        'name':location.location_name,
        'path':location.path,
        'inventory_location':getattr(location,'inventory_location',defLoc),
        'type':'Item_Tracking'}

    def _get_sb_instance(self,fsDoc):
        return SalesInvBase.getInstanceAny(StorageBlob,fsDoc)

    @classmethod
    def GetStorageBlobInstance(cls,fsDoc):
        return SalesInvBase.getInstanceAny(StorageBlob,fsDoc)

    @classmethod
    def GetRecipeItemById(cls,recipeId):
        itemInfo = StorageBlob.get_by_dnl(recipeId)
        if itemInfo is not None:
            return {'name':itemInfo.name,'id':itemInfo.id,'path':itemInfo.path, 'item_type': itemInfo.item_type,'type':'recipe_costing'}
        return None

    def get_recipe_item_by_id(self,recipeId):
        return SalesInvBase.GetRecipeItemById(recipeId)

    def _get_recipe_costing_item(self, item_type, item_name,isCount=False):
        return SalesInvBase.GetRecipeCostingItem(item_type,item_name,isCount)

    @classmethod
    def GetRecipeCostingItem(cls, item_type, item_name,isCount=False):
        path = 'application_data/Color_Orchids/Customer_Tracking/StorageBlob/recipe_costing'
        colRef = cls.get_firestore_client().collection(path)
        q = colRef.where('item_type','==',item_type)
        #q = q.where('status','==','Active')
        if not isCount:
            q = q.where('name','==',item_name)
        snaps = q.stream()
        items = [{'name':x.get('name'),'id':x.id,'path':x.reference.path,'item_type': item_type,'type':'recipe_costing'} for x in snaps]
        return None if len(items) == 0 else items[0]
    

    def _get_item_recipe(self, item_type, recipe_entry):
        return SalesInvBase.GetItemRecipe(item_type,recipe_entry)
    
    @classmethod
    def GetItemRecipe(cls,item_type,recipe_entry):
        if recipe_entry is None or recipe_entry.strip() == '':
            return None
            
        parts = str(recipe_entry).split("|")
        if len(parts) == 1:
            isCount = cls.CheckFloat(parts[0])
            return cls.GetRecipeCostingItem(item_type, parts[0],isCount)

        itemDNL = parts[0]
        itemName = parts[1]
        itemInfo = StorageBlob.get_by_dnl(itemDNL)
        if itemInfo is None:
            #sf = StorageField()
            #isCount = sf.check_float(itemName)
            isCount = cls.CheckFloat(itemName)
            itemInfo = cls.GetRecipeCostingItem(item_type, itemName)
        else:
            itemInfo = {'name':itemInfo.name,'id':itemInfo.id,'path':itemInfo.path, 'item_type': itemInfo.item_type,'type':'recipe_costing'}

        return itemInfo