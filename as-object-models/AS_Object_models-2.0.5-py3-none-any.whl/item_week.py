###############################################################################################################################
# Licensed to the part of the ownership of Analytics Supply LLC.
#  All updates to this file should only be done at the sole discretion of the 
#  officers of Analytics Supply:
#  
##################################
##  Module Name:  item_week.py
##################################
#
#  Description:
#  --  This module trackes items from a recipe for a weekly inventory
#
##################################
#
#  Created:  ???  Somewhere around July 2020
#
##################################
#  UPDATES:
#  Date, Issue #, Name of Developer, Short description of bug
#  9/15/2020, ct:85, Jason Bowles, Update to stop tracking items by type and name:  https://gitlab.com/AnalyticsSupply/customer-tracking/-/issues/85
#  2/28/2021, asfc:8, Jason Bowles, Allow inventory to be tracked by location
#
#
#
#################################################################################################################################
from .sales_inv_utils import SalesInvBase
from datetime import datetime
import pytz
import jmespath

from .item_week_notes import ItemWeekNotes, NotesCollection
from .item_week_supply import ItemWeekSupply, SupplyCollection
from .inventory_active_items import InventoryLocation
from .supplier import Supplier
from . import GetInstance

class ItemWeekCollection(SalesInvBase):
    '''
    Class to collect all of the things that need to be monitored at a week level

    Reserves still have a central place but inventory monitoring happens at the inventory location paths

    Attributes
    ----------
        items : array
            the items
        item_type : str
            the type of item we are tracking at the week level
        finish_week : str
            The string id of the week for which this item inventory is watching
        _in_growWeekParent : GrowWeek
            The grow week that this inventory is attached
        _loaded_items : dict
            the items loaded for this inventory week
    
    Class Methods
    -------------
        getInstance(docRef,gwParent):
            get an instance of ItemWeek given the GrowWeek and the firestore document
        getOrCreateInstance(invLoc,item_type, gwParent):
            Get an instance of ItemWeek with location, itemType and GrowWeek
    
    Methods
    -------
        base_path():
            The base path for all inventory item weeks
        post_create_activities():
            load up needed attributes after class creation
        create_itemweek_entry(item,gwPar):
            create an item week by item and grow week
        get_itemweek(itemId):
            get the item week for this id
        get_supply():
            Get all of the supply for this item week
        get_notes():
           Get all of the notes for this item week
        
    '''
    ext_fields = ['items','item_type','finish_week','inventory_location','soft_delete','parent_path','path']
    COLLECTION_NAME = 'application_data'

    IWS = "Supply"
    IWN = "Notes"

    def __init__(self,fsClient, **kwargs):
        self.soft_delete = kwargs.get('soft_delete',False)
        self.items = kwargs.get('items',None)
        self.item_type = kwargs.get('item_type','')
        self._inventory_location = kwargs.get('inventory_location',None)
        self.finish_week = kwargs.get('finish_week','')
        self._in_growWeekParent = kwargs.get('_growWeekParent',None)
        self._loaded_items = {}

        super(ItemWeekCollection,self).__init__(fsClient, **kwargs)

        if self.exists:
            self.post_create_activities()
    
    def post_create_activities(self):
        """
        After init of the class object... load up relevant data
        1. Collections
        2. Items (Active Items)
        3. Item Weeks
        """
        self._notes_collection = NotesCollection.getOrCreateInstance(self._fsClient.document(self.notes_path))
        self._supply_collection = SupplyCollection.getOrCreateInstance(self._fsClient.document(self.supply_path))

        if self.items is not None:
            item_ids = self.items.keys()
            for item_id in item_ids:
                item_dict = self.items[item_id]
                item_dict['_itemCollection'] = self
                item_dict['_notesCollection'] = self._notes_collection
                item_dict['_supplyCollection'] = self._supply_collection
                item_dict['_growWeekParent'] = self._growWeekParent
                iw = ItemWeek(self._fsClient,**item_dict)
                self._loaded_items[iw.item_id] = iw 

        
    def base_path(self):
        '''
        Get the base path to find all
        '''
        return self.parent_path+'/Items'

    @property
    def id(self):
        return self.item_type

    @property
    def notes_path(self):
        gwPath = InventoryLocation.getInstance().getGrowWeekPath(self._growWeekParent.path, self.inventory_location)
        return f'{gwPath}/{self.IWN}/{self.item_type}'
    
    @property
    def supply_path(self):
        gwPath = InventoryLocation.getInstance().getGrowWeekPath(self._growWeekParent.path, self.inventory_location)
        return f'{gwPath}/{self.IWS}/{self.item_type}'

    @classmethod
    def getInstance(cls,docRef,gwParent):
        '''
        Get an instance of the Item Week Collection

        Parameters
        ----------
            docRef : Firestore Object
                the Firestore Document object
            gwParent : The grow week that is a parent to this ItemWeek
        '''
        ref,snap = ItemWeekCollection.getDocuments(docRef)
        docDict = snap.to_dict() if snap.exists else {}
        docDict['inventory_location'] = InventoryLocation.getInstance().get_location_from_path(ref.path)
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        docDict['_growWeekParent'] = gwParent
        return ItemWeekCollection(ItemWeekCollection.get_firestore_client(),**docDict)

    @classmethod
    def getOrCreateInstance(cls,invLoc : str, item_type : str, gwParent):
        '''
        Get an instance of ItemWeekCollection and create it if it doesn't exist

        Parameters
        ----------
            invLoc : str
                The inventory location for tracking
            item_type : str
                The item type being tracked
            gwParent : GrowWeek
                The grow week that is the parent
        '''
        invLocPath = InventoryLocation.getInstance().getGrowWeekPath(gwParent.path,invLoc)
        iwc = cls.getInstance(gwParent._fsClient.document(f'{invLocPath}/Items/{item_type}'),gwParent)
        if not iwc.exists:
            iwc.item_type = item_type
            iwc.finish_week = gwParent.id
            iwc.update_ndb(True)
            iwc.post_create_activities()
        return iwc


    @property
    def _growWeekParent(self):
        if self._in_growWeekParent is None:
            gwParDoc = self.get_firestore_client().document(self.parent_path)
            self._in_growWeekParent = GetInstance("GrowWeek",gwParDoc)
        return self._in_growWeekParent
    
    @property
    def inventory_location(self):
        if self._inventory_location is None:
            if self.exists:
                self._inventory_location = InventoryLocation.getInstance().get_location_from_path(self.path)
            else:
                self._inventory_location = InventoryLocation.getInstance().default_location
        return self._inventory_location

    def create_itemweek_entry(self, item, gwPar):
        ''' Input is going to be recipe item '''
        #cleanName = ItemWeek.CleanItemName(item.name)
        iw = self._loaded_items.get(item.id,None)
        if iw is None:
            item_dict = {}
            itemObj = self._get_sb_instance_by_path(item.path)
            item_dict['item'] = {'name':itemObj.name,'id':itemObj.id,'path':itemObj.path}
            item_dict['name'] = itemObj.name
            item_dict['item_type'] = self.item_type
            item_dict['inventory_location'] = self.inventory_location
            item_dict['finish_week'] = self.finish_week
            item_dict['actual'] = 0
            item_dict['want_qty'] = 0
            item_dict['color_groupings'] = {}
            item_dict['groupings'] = {}
            item_dict['total_reserved'] = 0
            item_dict['_growWeekParent'] = gwPar
            item_dict['_itemCollection'] = self
            item_dict['_notesCollection'] = self._notes_collection
            item_dict['_supplyCollection'] = self._supply_collection
            iw = ItemWeek(self._fsClient,**item_dict)
            iw.update_ndb()
        return iw

    def get_itemweek(self,itemId):
        '''
        Get the item week by id
        '''
        #cleanName = ItemWeek.CleanItemName(itemName)
        return self._loaded_items.get(itemId,None)

    def get_supply(self):
        '''
        Get all supplies for this item week
        '''
        return self._supply_collection

    def get_notes(self):
        '''
        Get all the notes for this item week
        '''
        return self._notes_collection

    def update_ndb(self, doCreate=False):
        '''
        Wrapped update to make sure loaded objects in memory get updated
        '''
        if self.items is None:
            self.items = {}

        item_ids = self._loaded_items.keys()
        for item_id in item_ids:
            self.items[item_id] = self._loaded_items[item_id].get_dict()

        super(ItemWeekCollection,self).update_ndb(doCreate)


class ItemWeek(SalesInvBase):
    """ This is the class represents all plants that are available during a specific week 
    
    Attributes
    ----------
        name : str
            The name of the item being tracked
        inventory_location : str
            The location where inventory is being tracked
        item_type : str
            The type of item we are tracking
        _collection_parent : ItemWeekCollection
            The collection to which this belongs (optional)
        _notesCollection : ItemWeekNotes
            The link to the notes for this item week
        _supplyCollection : ItemWeekSupply
            The link to the supplies for this item week
        item : FSObject
            The id, name and path to the item that is being tracked
        finish_week : str
            The string id for the finish week i.e. 2021_38 is <year>_<week number>
        actual : str
            The actual inventory amount that is being tracked
        want_qty : int
            The quantity that is wanted (unused)
        color_groupings : dict
            Key Value pair of color and quantity
        groupings : dict
            Deprecated:  Not used
        _in_growWeekParent : GrowWeek
            The instance of the grow week for this ItemWeek
        item_name : str
            the name of the item name, cleaned
        item_id : str
            The unique id of the item for this inventory
        item_path : str
            The firestore path to the document for this item
        path : str
            The path to this item week entry
        parent_path : str
            The path to the parent document for this item week

    Class Methods
    -------------
        ParseItemWeekId(itemWeekId):
            Given a item week id, parse it to get the item_id and the week_id out
        getInstance(docDict):
            Given a dict of information create an ItemWeek entry
        CleanItemName(inName):
            Clean and make url safe the name
        get_or_create(invLoc : str, itemType : str, itemInfo : FSObject, growWeek : GrowWeek):
            The method to get an instance of ItemWeek
        CleanItemType(itemTypeName):
            The lower case version of the item type that doesn't end in 's'
    
    Methods
    -------
        update_ndb(doCreate=True):
            Wrapped method that updates the list of items
        get_itemweek_dict() : dict
            Get the item week summary dictionary
            
        
    """

    ext_fields = ['item','name','item_name','item_type','item_id','finish_week','actual','want_qty','total_reserved','availability',
    'total_forecasted','color_groupings','groupings','inventory_location','actual_upd_dt','soft_delete','parent_path','path']
    COLLECTION_NAME = 'application_data'
    
    def __init__(self, fsClient, **kwargs):
        self.soft_delete = kwargs.get('soft_delete',False)
        self.name = kwargs.get('name','')
        self._inventory_location = kwargs.get('inventory_location',None)
        self.item_type = kwargs.get('item_type',None)
        self._collection_parent = kwargs.get('_itemCollection',None)
        self._notesCollection = kwargs.get('_notesCollection',None)
        self._supplyCollection = kwargs.get('_supplyCollection',None)
        self.item = kwargs.get('item',{}) 
        self.finish_week = kwargs.get('finish_week','')
        self.actual = kwargs.get('actual','')
        self._total_reserved = kwargs.get('total_reserved',None)
        self._availability = kwargs.get('availability',None)
        self.want_qty = kwargs.get('want_qty','')
        self.actual_upd_dt = kwargs.get('actual_upd_dt',None)
        self.color_groupings = kwargs.get('color_groupings','')
        self.groupings = kwargs.get('groupings',{})
        self._total_forecasted = kwargs.get('total_forecasted',None)
        self._in_growWeekParent = kwargs.get('_growWeekParent',None)
        self._supplies = None
        self._notes = None
        super(ItemWeek, self).__init__(fsClient, **kwargs)
        
    
    def base_path(self):
        return self.parent_path+'/Items'
    
    @property
    def inventory_location(self):
        if self._inventory_location is None:
            if self.exists:
                self._inventory_location = InventoryLocation.getInstance().get_location_from_path(self.path)
            else:
                self._inventory_location = InventoryLocation.getInstance().default_location
        return self._inventory_location
    
    def refresh_actual_update_date(self):
        self.actual_upd_dt = datetime.now().isoformat()

    @property
    def id(self):
        return ItemWeek.CreateItemWeekId(self.finish_week,self.inventory_location,self.item_id)

    @classmethod
    def GetBasePath(cls,invLoc,growWeek,itemType):
        inventory_location = InventoryLocation.getInstance().get_collection_name(invLoc)
        basePath = f'application_data/Color_Orchids/Sales_Inventory/{inventory_location}/GrowWeek/{growWeek}/__SECTION__/{itemType}'
        return basePath

    @classmethod
    def GetItemsBasePath(cls,invLoc,growWeek,itemType):
        basePath = cls.GetBasePath(invLoc,growWeek,itemType)
        itemPath = basePath.replace("__SECTION__","Items")
        return itemPath

    @classmethod
    def GetNotesBasePath(cls,invLoc,growWeek,itemType):
        basePath = cls.GetBasePath(invLoc,growWeek,itemType)
        itemPath = basePath.replace("__SECTION__","Notes")
        return itemPath
    
    @classmethod
    def GetSupplyBasePath(cls,invLoc,growWeek,itemType):
        basePath = cls.GetBasePath(invLoc,growWeek,itemType)
        itemPath = basePath.replace("__SECTION__","Supply")
        return itemPath
    
    @classmethod
    def CreateItemWeekId(cls, weekId, invLoc,itemId):
        return f"{weekId}__{invLoc}__{itemId}"

    @classmethod
    def ParseItemWeekId(cls,itemWeekId : str) -> dict:
        '''
        Given a item week id, parse it to get the item_id and the week_id out

        Parameters
        ----------
            itemWeekId : str
                the Item and Week ids and inventory location... separated by double underscore <year>_<week number>__<inventory_location>__<item_id>
        '''
        parts = itemWeekId.split("__")
        week_id = parts[0]
        invLoc = InventoryLocation.getInstance().default_location
        if len(parts) > 1:
            invLoc = parts[1]
        item_id = None
        if len(parts) > 2:
            item_id = parts[2]
        return {"item_id": item_id, "week_id": week_id, "inventory_location":invLoc}

    @property
    def item_name(self):
        return ItemWeek.CleanItemName(self.item.get('name','NoItemName'))

    @property
    def get_lookup_entry(self):
        return {'key': self.item_id, 'value': self.item_id}
    
    @property
    def item_id(self):
        return self.item.get('id',"NoItemId")

    @property
    def item_path(self):
        return self.item.get('path',"NoItemPath")

    @property
    def _growWeekParent(self):
        if self._in_growWeekParent is None:
            gwPath = InventoryLocation.getInstance().get_grow_path(self.parent_path)
            gwParDoc = self.get_firestore_client().document(gwPath)
            self._in_growWeekParent = GetInstance("GrowWeek",gwParDoc)
        return self._in_growWeekParent

    @classmethod
    def getInstance(cls,docDict):
        '''
        Get an instance of the Item Week

        Parameters
        ----------
            docDict : dict
                A dictionary with attributes for the Item Week loaded
        '''
        return ItemWeek(ItemWeek.get_firestore_client(),**docDict)

    @property
    def path(self):
        return self._collection_parent.path

    @property
    def parent_path(self):
        return self._collection_parent.parent_path

    def update_ndb(self,doCreate=True):
        '''
        The wrapped update method
        '''
        self._collection_parent._loaded_items[self.item_id] = self
        return self._collection_parent.update_ndb(doCreate)

    def delete_resp(self):
        '''
        Wrapped delete method
        '''
        if self._collection_parent._loaded_items.get(self.item_id,None) is not None:
            del self._collection_parent._loaded_items[self.item_id]
        
        self._collection_parent.update_ndb()

    @property
    def notes(self):
        if self._notes is None:
            notes = self._notesCollection.getNotesByItemId(self.item_id)
            self._notes = notes
        return self._notes

    @property
    def notes_dict(self):
        return [note.get_dict() for note in self.notes]

    @property
    def supply(self):
        if self._supplies is None:
            #supplies = self._supplyCollection.getSupplyByItemName(self.item_name)
            supplies = self._supplyCollection.getSupplyByItemId(self.item_id)
            self._supplies = supplies
        return self._supplies

    @property
    def total_forecasted(self):
        if self._total_forecasted is None:
            self._total_forecasted = jmespath.search("[*].forecast | sum(@)",self.supply)
        return self._total_forecasted

    def create_note(self, note):
        return self._notesCollection.create_note(self.item_id, note)

    def delete_note(self, note_id):
        return self._notesCollection.delete_note(note_id)
        
    def create_supply(self,supplier_id, inForecast, confirmation_num):
        return self._supplyCollection.create_supply(self.item_id,supplier_id,inForecast,confirmation_num)

    @classmethod
    def GetItemWeekDict(cls,invLoc,growWeek, itemType, itemId) -> dict:
        itemsPath = cls.GetItemsBasePath(invLoc,growWeek,itemType)
        itemsFsDoc = cls.returnFSDocByPath(itemsPath)
        notesFsDoc = cls.returnFSDocByPath(cls.GetNotesBasePath(invLoc,growWeek,itemType))
        supplyFsDoc = cls.returnFSDocByPath(cls.GetSupplyBasePath(invLoc,growWeek,itemType))
        dflt = {'name':itemId,'item_id':itemId,'finish_week':growWeek,'actual':0,'want_qty':0,'color_groupings':{},'total_reserved':0}
        itemInfo = itemsFsDoc.getData("items").get(itemId,dflt)
        supplyInfo = supplyFsDoc.getData("supply").get(itemId,[])
        supplyInfo2 = [cls.GetTransformedSupply(x) for x in supplyInfo]
        actDate = itemInfo.get('actual_upd_dt','')
        if actDate is None:
            actDate = ''
        if actDate != '' and actDate.find('EST') < 0:
            actDate = cls.convert_utc_to_timezone_str(actDate)
        notesInfo = notesFsDoc.getData("notes").get(itemId,[])
        d = {'name': itemInfo['name'],
             'item_id': itemInfo['item_id'],
             'finish_week': itemInfo['finish_week'],
             'actual': itemInfo['actual'],
             'actual_upd_dt': actDate,
             'want_qty': itemInfo['want_qty'],
             'color_groupings': itemInfo['color_groupings'],
             'total_reserved' : itemInfo['total_reserved'],
             'inventory_location': invLoc,
             'item_type': itemType,
             'notes': jmespath.search("[*].{note_id: id, note: note, author: updated_by, updated: up_timestamp}",notesInfo),
             'forecasted': supplyInfo2}
             #'forecasted': jmespath.search("[*].{forecast: forecast, update_dt: up_timestamp, note: note, supply_id: id,  item_id: item_id, supplier_info: {id: supplier.id,name:supplier.name}}",supplyInfo)}

        return d
    
    @classmethod
    def GetTransformedSupply(cls,entry):
        info = {}
        info['forecast'] = entry['forecast']
        info['update_dt'] = cls.convert_utc_to_timezone_str(entry['up_timestamp'])
        info['note'] = entry.get('note','')
        info['supply_id'] = entry['id']
        info['item_id'] = entry['item_id']
        info['supplier_info'] = {'id':entry['supplier']['id'],'name':entry['supplier']['name']}
        return info

    @classmethod
    def UpdateTotalForecasted(cls, invLoc,growWeek,itemType, itemId) -> dict:
        itemsPath = cls.GetItemsBasePath(invLoc,growWeek,itemType)
        itemsFsDoc = cls.returnFSDocByPath(itemsPath)
        supplyFsDoc = cls.returnFSDocByPath(cls.GetSupplyBasePath(invLoc,growWeek,itemType))
        itemSupplyArr = []
        totForecasted = 0
        try:
            itemSupplyArr = supplyFsDoc.getData(f"supply.`{itemId}`")
            totForecasted = jmespath.search("[*].forecast | sum(@)",itemSupplyArr)
        except KeyError as e:
            itemSupplyArr = []
            # no supplies found for itemId
        
        update_dict = {f"items.`{itemId}`.total_forecasted": totForecasted}
        #self.up_timestamp = datetime.now().isoformat()
        update_dict['up_timestamp'] = datetime.now().isoformat()
        #self.updated_by = self.get_client().user_email
        update_dict['updated_by'] = ItemWeek.get_client().user_email
        #self.updated_system = 'Firestore_Backend_2020'
        update_dict['updated_system'] = 'Firestore_Backend_2020'
        update_dict[f"items.`{itemId}`.supply_upd_dt"] = datetime.now().isoformat()
        itemsFsDoc.setData(update_dict)
        return totForecasted


    def get_itemweek_dict(self):
        d = {'name': self.item['name'],
             'item_id': self.item_id,
             'finish_week': self._growWeekParent.get_growweek_dict(),
             'actual': self.actual,
             'want_qty': self.want_qty,
             'color_groupings': self.color_groupings,
             'total_reserved' : self.total_reserved,
             #'groupings': self.groupings,
             '_id':self.id}

        return d

    def update_groupings(self, grouping, reset=False):
        """
        TODO
        """
        total_qnt = 0
        vals = False
        for key in grouping.keys():
            vals = True
            qnt = grouping[key]
            total_qnt = total_qnt + int(qnt)

        if vals or reset:
            self.actual = total_qnt

        self.grouping = grouping
        self.update_ndb()
        return True


    def update_color_grouping(self, color_grouping, reset=False):
        """
        The color grouping object should be a dict where the keys are colors and a quantity
        This function will add the json object and then go through and count the numbers and update the actual quantity
        :param color_grouping:
        :return:
        """
        total_qnt = 0
        vals = False
        for key in color_grouping.keys():
            vals = True
            qnt = color_grouping[key]
            total_qnt = total_qnt + int(qnt)

        if vals or reset:
            self.actual = total_qnt

        self.color_groupings = color_grouping
        self.refresh_actual_update_date()
        self.update_ndb()
        return True

    def get_schema(self):
        schema = self.get_bq_schema()
        return schema

    def get_values_dict(self):
        return self.get_dict()

    @property
    def next(self):
        return ItemWeek.get_or_create(self.inventory_location, self.item_type, self.item, self._growWeekParent.next_week)

    @property
    def prior(self):
        return ItemWeek.get_or_create(self.inventory_location,self.item_type, self.item, self._growWeekParent.prior_week)

    @property
    def forecasts(self):
        fcast = jmespath.search("[*].forecast | sum(@)",self.supply)
        #for supp in self.supply:
        #   fcast = fcast + supp.get_forecast()
        return fcast

    @property
    def reserves(self):
        """Pulling this information through the _growWeekParent"""
        return self._growWeekParent.getSummary().getItemReserves(self.item_type, self.item_id,invLoc=self.inventory_location)

    @property
    def total_reserved(self):
        if self._total_reserved is None:
            self._total_reserved = self.get_total_reserved()
        return self._total_reserved

    def get_total_reserved(self):
        return self._growWeekParent.getSummary().getReserveAmtByItem(self.item_type, self.item_id,invLoc=self.inventory_location)

    @classmethod
    def get_or_create(cls,invLoc, itemType, itemInfo, growWeek):
        '''
        Get an instance of ItemWeek

        Parameters
        ----------
            invLoc : str
                The inventory location where inventory will be tracked
            itemType : str
                The item type for the inventory tracking
            itemInfo : FSObject
                The item info of the item Type, (id, name, path)
            growWeek : GrowWeek
                The GrowWeek that this is tracked against
        '''
        itemObj = ItemWeek.GetSBObj(itemInfo['path'])
        return growWeek.get_or_create_itemweek(invLoc,itemType,itemObj)
    
    @property
    def clean_item_type(self):
        return ItemWeek.CleanItemType(self.item_type)

    def iw_summary(self):
        ps = {}
        ps['_id'] = self.id
        ps['item'] = self.item['name']
        ps['clean_name'] = self.item_name
        ps['inventory_location'] = self.inventory_location
        ps['item_id'] = self.item['id']
        ps['week_id'] = self.finish_week
        ps['actual'] = self.actual
        ps['forecast'] = self.forecasts
        ps['num_reserved'] = self.get_total_reserved()
        return ps

    @property
    def availability(self):
        '''
        What is the amount of inventory given the number reserved
        '''
        if self._availability is None:
            self._availability = self._calc_availability()
        return self._availability
    
    def _calc_availability(self,rsvs=None):
        if rsvs is None:
            rsvs = self.total_reserved
        fcast = self.forecasts
        if self.actual > 0:
            return self.actual - rsvs

        return fcast - rsvs
    
    def refresh(self, allowUpdate=True):
        priorAvailability = self._availability
        priorReserved = self._total_reserved
        # reset total forecasted
        self._total_forecasted = None
        newReserved = self.get_total_reserved()
        newAvailability = self._calc_availability(rsvs=newReserved)
        doSave = False

        if priorReserved != newReserved:
            self._total_reserved = newReserved
            doSave=True

        if priorAvailability != newAvailability:
            self._availability = newAvailability
            doSave=True
        
        if doSave and allowUpdate:
            self.update_ndb()
        
        return doSave