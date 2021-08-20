from .sales_inv_utils import SalesInvBase
from datetime import datetime
import jmespath

from . import GetInstance
from .inventory_active_items import InventoryLocation
from . import Supplier

class MonthSupplyCollection(SalesInvBase):
    ext_fields = ['grow_month','item_type','supply','inventory_location','soft_delete','parent_path','path']
    COLLECTION_NAME = 'application_data'

    def __init__(self,fsClient, **kwargs):
        self.soft_delete = kwargs.get('soft_delete',False)
        self.item_type = kwargs.get('item_type','')
        self.supply = kwargs.get('supply',None)
        self.grow_month = kwargs.get('grow_month','')
        self._inventory_location = kwargs.get('inventory_location',None)
        self._in_growMonthParent = kwargs.get('_growMonthParent',None)
        self._loaded_supply = {}
        super(MonthSupplyCollection,self).__init__(fsClient, **kwargs)
        if self.supply is not None:
            supply_itemnames = self.supply.keys()
            for supplyname in supply_itemnames:
                supplies = self.supply[supplyname]
                for supply_entry in supplies:
                    supply_entry['_supplyCollection'] = self
                    supply_entry['_growMonthParent'] = self._growMonthParent
                    supply_entry['item_type'] = self.item_type
                    supply = ItemMonthSupply(self._fsClient,**supply_entry)
                    self._loaded_supply[supply.id] = supply

    def base_path(self):
        return self.parent_path+'/Supply'

    @property
    def id(self):
        return self.item_type
    
    @property
    def inventory_location(self):
        if self._inventory_location is None:
            invLoc = InventoryLocation.getInstance()
            if self.exists:
                self._inventory_location = invLoc.get_location_from_path(self.path)
        return self._inventory_location

    @classmethod
    def getInstance(cls,docRef,gwParent):
        ref,snap = MonthSupplyCollection.getDocuments(docRef)
        docDict = snap.to_dict() if snap.exists else {}
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        docDict['_growMonthParent'] = gwParent
        return MonthSupplyCollection(MonthSupplyCollection.get_firestore_client(),**docDict)

    @classmethod
    def getOrCreateInstance(cls,docRef,gwParent):
        col = cls.getInstance(docRef,gwParent)
        if not col.exists:
            col.update_ndb(True)
        return col

    @property
    def _growMonthParent(self):
        if self._in_growMonthParent is None:
            gwParDoc = self.get_firestore_client().document(self.parent_doc_path)
            self._in_growMonthParent = GetInstance("GrowMonth",gwParDoc)
        return self._in_growMonthParent

    def getSupplyByItemId(self,item_id):
        return [supply for supply in list(self._loaded_supply.values()) if supply.item_id == item_id]

    def getSupplyById(self,supply_id):
        return self._loaded_supply.get(supply_id,None)

    def create_supply(self, item_id, supplier_id, inforecast,confirmation_num,note=''):
        supply_id = self._get_doc_id('Supply')
        supply_entry = {}
        supply_entry['_supplyCollection'] = self
        supply_entry['_growMonthParent'] = self._growMonthParent
        supply_entry['item_type'] = self.item_type
        supply_entry['item_id'] = item_id
        supply_entry['supplier'] = MonthSupplyCollection.GetSupplierInfo(supplier_id)
        supply_entry['forecast'] = int(inforecast)
        supply_entry['confirmation_num'] = confirmation_num
        supply_entry['note'] = note
        supply_entry['id'] = supply_id
        supply = ItemMonthSupply(self._fsClient,**supply_entry)
        self._loaded_supply[supply.id] = supply
        supply._set_add_entries()
        supply._set_update_entries()
        self.update_ndb()
        return supply

    @classmethod
    def GetSupplierInfo(cls, supplier_id):
        supplier = SalesInvBase.GetByDNL(supplier_id,Supplier)
        suppInfo = {'name': supplier.name,'id': supplier.id,'path': supplier.path}
        return suppInfo

    def delete_supply(self, supply_id):
        del self._loaded_supply[supply_id]
        self.update_ndb()

    def update_ndb(self, doCreate=False):
        self.supply = {}
        supply_ids = self._loaded_supply.keys()
        for supply_id in supply_ids:
            sup = self._loaded_supply[supply_id]
            supply_array = self.supply.get(sup.item_id,[])
            supply_array.append(sup.get_dict())
            self.supply[sup.item_id] = supply_array

        return super(MonthSupplyCollection,self).update_ndb(doCreate)


class ItemMonthSupply(SalesInvBase):
    """ This is the class represents all plants that are available during a specific week """

    ext_fields = ['id','supplier','item_name','item_id','item_type','forecast','confirmation_num','cost','note','soft_delete']
    COLLECTION_NAME = 'application_data'
    
    def __init__(self, fsClient, **kwargs):
        self.soft_delete = kwargs.get('soft_delete',False)
        self.supplier = kwargs.get('supplier',{}) 
        self.forecast = kwargs.get('forecast',0) 
        self.supply_id = kwargs.get('id',ItemMonthSupply.GetNextDNL('Supply'))
        self.item_name = kwargs.get('item_name','')
        self.item_id = kwargs.get('item_id','')
        self.item_type = kwargs.get('item_type','')
        self.cost = kwargs.get('cost','')
        self.note = kwargs.get('note','')
        self.confirmation_num = kwargs.get('confirmation_num','') 
        self._growMonthParent = kwargs.get('_growMonthParent',None)
        self._supplyCollection = kwargs.get('_supplyCollection',None)
        super(ItemMonthSupply, self).__init__(fsClient, **kwargs)

    def base_path(self):
        return self._supplyCollection.path
    
    @classmethod
    def get_active(cls):
        return SalesInvBase.GetActive('ItemMonthSupply',ItemMonthSupply)

    @property
    def id(self):
        return self.supply_id

    
    @property
    def path(self):
        return self._supplyCollection.path

    @property
    def parent_path(self):
        return self._supplyCollection.parent_path

    def get_schema(self):
        schema = self.get_bq_schema()
        return schema

    def get_values_dict(self):
        values = self.get_dict()
        return values

    def get_forecast(self):
        if self.forecast:
            return self.forecast
        return 0

    def update(self,argSupplier, argForecast=0, argConfirmation=None, argCost=0):
        #pgs = SalesInvBase.GetByDNL(argId,ItemMonthSupply) #.get_by_id(int(argId))
        if self.supplier['id'] != argSupplier:
            supplier = SalesInvBase.GetByDNL(argSupplier,Supplier)
            suppInfo = {'name': supplier.name,'id': supplier.id,'path': supplier.path}
            self.supplier = suppInfo

        self.forecast = int(argForecast)
        self.confirmation_num = str(argConfirmation)
        self.cost = int(argCost)
        return self.update_ndb()

    def get_ItemMonthSupply_dict(self):
        pgs = {}
        pgs['id'] = self.id
        pgs['supplier_name'] = self.supplier.get('name','none')
        pgs['supplier_id'] = self.supplier.get('id','none')
        pgs['forecast'] = self.forecast
        pgs['note'] = self.note
        pgs['itemweek'] = self.item_id
        pgs['confirmation_num'] = self.confirmation_num
        return pgs

    def get_supply2(self):
        pgsdb = {}
        pgsdb['_id'] = self.id
        pgsdb['supplier'] = self.supplier.get('name','none')
        pgsdb['supplier_id'] = self.supplier.get('id','none')
        pgsdb['forecast'] = self.forecast
        pgsdb['week_id'] = self._growMonthParent.id
        pgsdb['note'] = self.note
        pgsdb['add_date'] = self.timestamp
        pgsdb['item'] = self.item
        #pg = self._growMonthParent.plantgrow.get(self.plantgrow,None)
        #pgsdb['plant_id'] = pg.plant_id if pg is not None else 'none'
        pgsdb['soft_delete'] = "Y" if self.soft_delete and (True == self.soft_delete) else "N"
        return pgsdb

    def update_ndb(self,doCreate=True):
        if doCreate:
            self._set_add_entries()
        self._set_update_entries()
        self._supplyCollection._loaded_supply[self.id] = self
        return self._supplyCollection.update_ndb(doCreate)

    def delete_resp(self):
        if self._supplyCollection._loaded_supply.get(self.id,None) is not None:
            del self._supplyCollection._loaded_supply[self.id]
        
        self._supplyCollection.update_ndb()