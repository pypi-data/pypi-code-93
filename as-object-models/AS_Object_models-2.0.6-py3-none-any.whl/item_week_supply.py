from .sales_inv_utils import SalesInvBase
from datetime import datetime
import pytz
import jmespath
from threading import Lock

from . import GetInstance
from . import Supplier
from .inventory_active_items import InventoryLocation

lock = Lock()

class SupplyCollection(SalesInvBase):
    ext_fields = ['finish_week','grow_period','period_type','item_type','supply','soft_delete','parent_path','path']
    COLLECTION_NAME = 'application_data'

    __instances = {}
    

    def __init__(self,fsClient, **kwargs):
        super(SupplyCollection,self).__init__(fsClient, **kwargs)
        self.soft_delete = kwargs.get('soft_delete',False)
        self._item_type = kwargs.get('item_type',self.id)
        self.supply = kwargs.get('supply',None)
        self.finish_week = kwargs.get('finish_week',self.grow_period)
        self._loaded_supply = {}
        if self.supply is not None:
            supply_itemnames = self.supply.keys()
            for supplyname in supply_itemnames:
                supplies = self.supply[supplyname]
                for supply_entry in supplies:
                    supply_entry['_supplyCollection'] = self
                    supply_entry['item_type'] = self.item_type
                    supply = ItemWeekSupply(self._fsClient,**supply_entry)
                    self._loaded_supply[supply.id] = supply

    def base_path(self):
        return self.parent_path+'/Supply'

    @property
    def item_type(self):
        if self._item_type is None:
            self._item_type = self.id
        return self._item_type

    @classmethod
    def getInstance(cls,docRef):
        with lock:
            fsDoc = SupplyCollection.returnFSDoc(docRef)
            key = f"{fsDoc.grow_period}__{fsDoc.inventory_location}__{fsDoc.id}"
            if SupplyCollection.__instances.get(key,None) == None:
                docDict = fsDoc.snap.to_dict() if fsDoc.snap.exists else {}
                docDict['fs_docSnap'] = fsDoc.snap
                docDict['fs_docRef'] = fsDoc.ref
                supColl = SupplyCollection(SupplyCollection.get_firestore_client(),**docDict)
                if not supColl.exists:
                    supColl.update_ndb()
                SupplyCollection.__instances[key] = supColl
            return SupplyCollection.__instances[key]

    @classmethod
    def getOrCreateInstance(cls,docRef):
        col = cls.getInstance(docRef)
        return col

    @classmethod
    def GetOrCreateItemWeekSupply(cls, itemType, invLoc, periodType, growPeriod):
        pathPeriodType = 'GrowWeek'
        if periodType.lower() == 'month':
            pathPeriodType = 'GrowMonth'

        pathInvLoc = InventoryLocation.getInstance().get_collection_name(invLoc)
        basePath = f'application_data/Color_Orchids/Sales_Inventory/{pathInvLoc}/{pathPeriodType}/{growPeriod}/Supply/{itemType}'
        return cls.getOrCreateInstance(cls.get_firestore_client().document(basePath))
    
    @classmethod
    def _transformSupply(cls, supply):
        #'id','supplier','item_name','item_type','item_id','forecast','confirmation_num'
        resp = {'supply_id':supply.id}
        resp['supplier_info'] = {'id': supply.supplier['id'],'name':supply.supplier['name']}
        resp['item_id'] = supply.item_id
        resp['note'] = supply.note
        resp['forecast'] = supply.forecast
        resp['update_dt'] = cls.convert_utc_to_timezone_str(supply.up_timestamp)
        return resp

    def getSupplyByItemId(self,item_id):
        return [SupplyCollection._transformSupply(supply) for supply in list(self._loaded_supply.values()) if supply.item_id == item_id]

    def getSupplyById(self,supply_id):
        return self._loaded_supply.get(supply_id,None)

    def create_supply(self, item_id, supplier_id, inforecast,confirmation_num, note=None):
        supply_id = self._get_doc_id('Supply')
        supply_entry = {}
        supply_entry['_supplyCollection'] = self
        supply_entry['item_type'] = self.item_type
        supply_entry['item_id'] = item_id
        supply_entry['supplier'] = SupplyCollection.GetSupplierInfo(supplier_id)
        supply_entry['forecast'] = int(inforecast)
        supply_entry['confirmation_num'] = confirmation_num
        supply_entry['note'] = '' if note is None else note
        supply_entry['id'] = supply_id
        supply = ItemWeekSupply(self._fsClient,**supply_entry)
        self._loaded_supply[supply.id] = supply
        supply._set_add_entries()
        supply._set_update_entries()
        self.update_ndb()
        return SupplyCollection._transformSupply(supply)

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

        return super(SupplyCollection,self).update_ndb(doCreate)


class ItemWeekSupply(SalesInvBase):
    """ This is the class represents all plants that are available during a specific week """

    ext_fields = ['id','supplier','item_name','item_type','item_id','forecast','confirmation_num','note','grow_period','period_type','cost','soft_delete']
    COLLECTION_NAME = 'application_data'
    
    def __init__(self, fsClient, **kwargs):
        self.soft_delete = kwargs.get('soft_delete',False)
        self.supplier = kwargs.get('supplier',{}) 
        self.forecast = kwargs.get('forecast',0) 
        self.supply_id = kwargs.get('id',ItemWeekSupply.GetNextDNL('Supply'))
        self.item_name = kwargs.get('item_name','')
        self.item_type = kwargs.get('item_type','')
        self.item_id = kwargs.get('item_id','')
        self.cost = kwargs.get('cost','')
        self.confirmation_num = kwargs.get('confirmation_num','')
        self.note = kwargs.get('note','')
        self._supplyCollection = kwargs.get('_supplyCollection',None)
        super(ItemWeekSupply, self).__init__(fsClient, **kwargs)

    def base_path(self):
        return self._supplyCollection.path
    
    @classmethod
    def get_active(cls):
        return SalesInvBase.GetActive('ItemWeekSupply',ItemWeekSupply)

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

    def update(self,argSupplier, argForecast=0, argConfirmation=None, argCost=0, note=None):
        #pgs = SalesInvBase.GetByDNL(argId,ItemWeekSupply) #.get_by_id(int(argId))
        if self.supplier['id'] != argSupplier:
            supplier = SalesInvBase.GetByDNL(argSupplier,Supplier)
            suppInfo = {'name': supplier.name,'id': supplier.id,'path': supplier.path}
            self.supplier = suppInfo

        self.forecast = int(argForecast)
        self.confirmation_num = str(argConfirmation)
        self.note = '' if note is None else note
        self.cost = int(argCost)
        return self.update_ndb()

    def get_itemweeksupply_dict(self):
        pgs = {}
        pgs['id'] = self.id
        pgs['supplier_name'] = self.supplier.get('name','none')
        pgs['supplier_id'] = self.supplier.get('id','none')
        pgs['forecast'] = self.forecast
        pgs['itemweek'] = self.item_name
        pgs['item_id'] = self.item_id
        pgs['confirmation_num'] = self.confirmation_num
        pgs['note'] = self.note
        return pgs

    def get_supply2(self):
        pgsdb = {}
        pgsdb['_id'] = self.id
        pgsdb['supplier'] = self.supplier.get('name','none')
        pgsdb['supplier_id'] = self.supplier.get('id','none')
        pgsdb['forecast'] = self.forecast
        pgsdb['week_id'] = self.grow_period
        pgsdb['add_date'] = self.timestamp
        pgsdb['item'] = self.item
        #pgsdb['plant_id'] = pg.plant_id if pg is not None else 'none'
        pgsdb['soft_delete'] = "Y" if self.soft_delete and (True == self.soft_delete) else "N"
        pgsdb['note'] = self.note
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