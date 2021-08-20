###############################################################################################################################
# Licensed to the part of the ownership of Analytics Supply LLC.
#  All updates to this file should only be done at the sole discretion of the 
#  officers of Analytics Supply:
#  
##################################
##  Module Name:  inventory_active_items.py
##################################
#
#  Description:
#  --  This module will have all recipe items by item type and will have a "tracked" attribute to tell us wether or not this is an item to track for inventory
#
##################################
#
#  Created:  ???  Somewhere around July 2020
#
##################################
#  UPDATES:
#  Date, Issue #, Name of Developer, Short description of bug
#  9/11/2020, ct:85, Jason Bowles, Update to stop tracking items by type and name:  https://gitlab.com/AnalyticsSupply/customer-tracking/-/issues/85
# 10/13/2020, ct:86, Jason Bowles, Make sure a newly active inventory item has loaded cache: https://gitlab.com/AnalyticsSupply/customer-tracking/-/issues/86
#
#
#
#################################################################################################################################
import re
from .sales_inv_utils import SalesInvBase
from .utils import FSObjSummary
from datetime import datetime
import jmespath

from . import GetInstance, CallClassMethod2
from . import DataNumber, DataNumberLookup

'''
In order to make the production view screen return relatively quickly.. I needed a way to identify when a new item was entered and needed tracked
... 

This adds an extra step for the user, that they have to add it as a "recipe item"... and also add it here to configure it to be tracked.

However, this also allows more control on how items in a recipe are tracked... by turning some off (cleaning up the view) or remapping on the fly
'''
class InventoryActiveItems(SalesInvBase):
    """ This is the class represents all items that are available during a specific week """

    ext_fields = ['item_type', 'items','soft_delete','inventory_type','parent_path','path']
    COLLECTION_NAME = 'application_data'

    DefaultFieldValues = {'tracked':False, 'order':99, 'id': 'None', 'id':'NoIdGiven', 'path':'NoPathGiven'}
    
    def __init__(self, fsClient, **kwargs):
        self.soft_delete = kwargs.get('soft_delete',False)
        self.item_type = kwargs.get('item_type','')
        self.items = kwargs.get('items',{})
        self.inventory_type = kwargs.get('inventory_type','week')
    
        super(InventoryActiveItems, self).__init__(fsClient, **kwargs)

    def base_path(self):
        return InventoryActiveItems.__basePath(self._fsClient)

    @classmethod
    def basePath(cls):
        return InventoryActiveItems.__basePath(InventoryActiveItems.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return InventoryActiveItems.COLLECTION_NAME+'/'+inClient.company+'/Sales_Inventory/Converted/InventoryActiveItems'

    @classmethod
    def getInstance(cls,fsDocument):
        ref,snap = InventoryActiveItems.getDocuments(fsDocument)
        docDict = snap.to_dict() if snap.exists else {}
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        return InventoryActiveItems(InventoryActiveItems.get_firestore_client(),**docDict)
  
    def get_schema(self):
        schema = self.get_bq_schema()
        return schema

    def get_values_dict(self):
        values = self.get_dict()
        return values

    def get_inventory_type(self):
        return self.inventory_type
    
    def set_inventory_type(self,typeInv):
        self.inventory_type = typeInv
    
    def set_inventory_monthly(self):
        self.set_inventory_type('month')
    
    def set_inventory_weekly(self):
        self.set_inventory_type('week') 

    @classmethod
    def __clean_item_type(cls,item_type):
        return cls.CleanItemType(item_type)

    @classmethod
    def display_recipe_items(cls,item_type,tracked_only=False):
        productionViewItems = InventoryActiveItems.get_all_dict(item_type,tracked_only)      
        return {'item_type':item_type,'items':productionViewItems}


    @classmethod
    def get_active_recipe_items(cls,item_type, fldKey='name'):
        path = 'application_data/Color_Orchids/Customer_Tracking/StorageBlob/recipe_costing'
        colRef = InventoryActiveItems.get_firestore_client().collection(path)
        q = colRef.where('item_type','==',item_type)
        q = q.where('status','==','Active')
        snaps = q.stream()
        plts = {x.get(fldKey):InventoryActiveItems.GetStorageBlobInstance(x) for x in snaps if x.get('name') != 'N/A'}
        return plts

    @classmethod
    def remove_item(cls,activeItemId):
        recipeItem = InventoryActiveItems.GetSBObjByDNL(activeItemId)
        return InventoryActiveItems.AddItem(recipeItem,doTrack=False)

    @classmethod
    def add_item_by_id(cls, recipe_id):
        recipeItem = InventoryActiveItems.GetSBObjByDNL(recipe_id)
        return InventoryActiveItems.AddItem(recipeItem,doTrack=True)

    @classmethod
    def add_item_order(cls, recipe_id, order):
        recipeItem = InventoryActiveItems.GetSBObjByDNL(recipe_id)
        return InventoryActiveItems.AddItem(recipeItem,itemOrder=order)

    @classmethod
    def _setup_entry(self,item_type):
        doc_path = InventoryActiveItems.basePath()+"/"+item_type
        sap = InventoryActiveItems.getInstance(InventoryActiveItems.get_firestore_client().document(doc_path))
        sap.item_type = item_type
        recipeItems = InventoryActiveItems.get_active_recipe_items(item_type,fldKey='data_number_lookup')
        recipes = list(recipeItems.values())
        for recipeEntry in recipes:
            sap.add_item(recipeEntry,doTrack=False)
        sap.update_ndb()
        return sap

    #@classmethod
    #def GetItemByName(cls, itemType, itemName):
    #    items = InventoryActiveItems.get_all(itemType)
    #    for item_key in items.keys():
    #        item = items[item_key]
    #        name = item.name
    #        cleanName = ItemWeek.CleanItemName(name)
    #        if itemName == name or itemName == cleanName:
    #            return item
    #    return None
    
    @classmethod
    def GetItemById(cls,itemType,itemId,onlyTracked=True):
        '''
        Updates are now going to be by item_id: (ct:85)
        '''
        items = InventoryActiveItems.get_all_active(itemType,onlyTracked)
        return items.get(itemId,None)

    @classmethod
    def AddItem(cls, recipe_entry,doTrack=None, itemOrder=None):
        sap = cls.get_entry(recipe_entry.item_type)
        return sap.add_item(recipe_entry,doTrack,itemOrder)

    def add_item(self, recipe_entry,doTrack=None, itemOrder=None):
        itemD = self.items.get(recipe_entry.id,{})
        itemD['id'] = recipe_entry.id
        itemD['name'] = recipe_entry.name
        itemD['clean_name'] = InventoryActiveItems.CleanItemName(recipe_entry.name)
        itemD['item_type'] = recipe_entry.item_type
        itemD['image'] = recipe_entry.image
        itemD['path'] = recipe_entry.path
        
        currentTracked = itemD.get('tracked',None)
        if doTrack is not None:
            itemD['tracked'] = doTrack
            currentTracked = doTrack
            
        if currentTracked is None:
            itemD['tracked'] = False # Default value for tracking
        
        currentOrder = itemD.get('order',None)
        if itemOrder is not None:
            itemD['order'] = itemOrder
            currentOrder = itemOrder

        if currentOrder is None:
            itemD['order'] = 99 # Default value for order

        self.items[recipe_entry.id] = itemD
        
        self.update_ndb()
        ##
        # update to fix ct:86
        # -- Hard coded "Vase" --- FOR NOW
        ##
        if itemD['tracked'] and recipe_entry.item_type == 'Vase':
            print("Publishing to the refresh topic: "+recipe_entry.id)
            for loc in InventoryLocation.getInstance().inventory_locations:
                CallClassMethod2("ItemMonthSummary","PublishRefreshListsName",{'parameters':(recipe_entry.item_type,recipe_entry.id,loc)})
            #ItemMonthSummary.PublishRefreshListsName(recipe_entry.item_type,recipe_entry.id)
        return itemD

    @classmethod
    def get_entry(cls, item_type):
        docRef = InventoryActiveItems.get_firestore_client().document(InventoryActiveItems.basePath()+'/'+item_type)
        activeItem = InventoryActiveItems.getInstance(docRef)
        if activeItem.exists:
            return activeItem
        return cls._setup_entry(item_type)
    
    @classmethod
    def _getActiveEntries(cls,itemType, only_tracked=True):
        aps = InventoryActiveItems.get_entry(itemType)
        if only_tracked:
            return jmespath.search("* | [?tracked == `true`]",aps.items)
        return aps.items
    
    @classmethod
    def get_all_active(cls,item_type,only_tracked=True):
        '''
        return all active entries
        '''
        activeEntries = InventoryActiveItems._getActiveEntries(item_type,only_tracked)
        return {x['id']:FSObjSummary(**cls._get_item_entry(x,fields=['id','path','name'])) for x in activeEntries}
        #for key in aps.items.keys():
        #    if aps.items[key]['tracked']:
        #        objDict[key] = FSObjSummary(**aps.items[key])
       # 
        #return objDict
    
    @classmethod
    def get_all_active_dict(cls,item_type):
        activeEntries = InventoryActiveItems._getActiveEntries(item_type)
        return {x['id']:cls._get_item_entry(x) for x in activeEntries}
    
    @classmethod
    def _get_item_entry(cls, itemEntry, fields=None):
        if fields is None:
            entry = {}
            defKeys = list(cls.DefaultFieldValues.keys())
            for key in defKeys:
                entry[key] = itemEntry.get(key,cls.DefaultFieldValues[key])
            for key in list(itemEntry.keys()):
                if key not in defKeys:
                    entry[key] = itemEntry[key]
            return entry

        if fields[0] == 'all':
            return itemEntry

        return {k:v for k,v in itemEntry.items() if k in fields}


    @classmethod
    def get_all_dict(cls,item_type,tracked_only=False):
        aps = InventoryActiveItems.get_entry(item_type)
        item_filter = '[*]'
        if tracked_only:
            item_filter = '[?tracked == `true`]'
        return {x['id']:cls._get_item_entry(x) for x in jmespath.search(f"* | {item_filter}",aps.items)}


class InventoryItems(SalesInvBase):
    """ This is the class represents all items that are available during a specific week """

    ext_fields = ['tracked_items','soft_delete','parent_path','path']
    COLLECTION_NAME = 'application_data'
    
    def __init__(self, fsClient, **kwargs):
        self.soft_delete = kwargs.get('soft_delete',False)
        self.tracked_items = kwargs.get('tracked_items',[])
        super(InventoryItems, self).__init__(fsClient, **kwargs)

    def base_path(self):
        return InventoryItems.__basePath(self._fsClient)

    @classmethod
    def basePath(cls):
        return InventoryItems.__basePath(InventoryItems.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return InventoryItems.COLLECTION_NAME+'/'+inClient.company+'/Sales_Inventory/Converted/InventoryItems'


    @classmethod
    def getInstance(cls):
        fsDocument = InventoryItems.get_firestore_client().document(cls.basePath()+'/InventoryItems')
        ref,snap = InventoryItems.getDocuments(fsDocument)
        docDict = snap.to_dict() if snap.exists else {}
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        ii = InventoryItems(InventoryItems.get_firestore_client(),**docDict)
        if not ii.exists:
            ii.update_ndb(True)
        return ii

class InventoryLocation(SalesInvBase):
    """
    The class that has inventory location names hard coded, will transition to DB later

    Attributes
    ----------
        inventory_locations : array[str]
            List of locations that we are tracking inventory
        inventory_coll_name : dict
            The lookup to what the collection name will be for this location
        rev_inventory_coll_name : dict
            a reverse lookup for location based on collection name
        default_location : str
            The location to use when no location is given
    
    Methods
    -------
        get_location_from_path(path):
            Given the path to a document can we get the location from it
        get_location_from_collection(collectionName):
            If we know the collection name, give the location name
        getGrowMonthPath(growMonthPath,invLoc):
            Create the correct path for the Item month given the grow month
        get_collection_name(location):
            the convenience method to get the collection name, not found returns None
    """
    __instance = None
    ext_fields = []
    
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if InventoryLocation.__instance == None:
            InventoryLocation()
        return InventoryLocation.__instance
    
    def __init__(self):
        if InventoryLocation.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.inventory_locations = ['Virginia','Texas']
            self.inventory_coll_name = {'Virginia':'InventoryLoc__Virginia',
                                    'Texas':'InventoryLoc__Texas'}
            self.rev_inventory_coll_name = {v:k for k,v in self.inventory_coll_name.items()}
            self.default_location = 'Virginia'
            InventoryLocation.__instance = self
    
    def base_path(self):
        return ''

    def get_location_from_path(self,path : str) -> str:
        '''
        Given the path to a document, can we get the location
        '''
        mm = re.match(self.grow_pattern,path)
        if mm is not None:
            grpD = mm.groupdict()
            return self.get_location_from_collection(grpD.get('invloc_collname',self.default_location))
        return self.default_location

    def get_collection_name(self,location : str) -> str:
        """
        Grab the collection name in the database for a location

        Parameters
        ----------
            location : str
                The name of the location where the inventory is being tracked
        """
        defCollName = self.inventory_coll_name[self.default_location]
        return self.inventory_coll_name.get(location,defCollName)
    
    def get_location_from_collection(self, locationCollName : str) -> str:
        '''
        If I have the colleciton name, need to get the inventory location name

        Parameters
        ----------
            locationCollName : str
                The collection name used for the location
        '''

        return self.rev_inventory_coll_name.get(locationCollName,self.default_location)
    
    def getGrowMonthPath(self, growMonthPath : str, invLoc : str) -> str:
        '''
        Given the path to the grow month instance, can we get the equivalent inventory location path

        Parameters
        ----------
            growMonthPath : str
                The path to the grow month
            invLov : str
                The inventory location where we need a path
        '''
        return self._getLocationFromGrowObj(growMonthPath,invLoc)
    
    def getGrowWeekPath(self, growWeekPath : str, invLoc : str) -> str:
        '''
        Given the path to the grow week instance, can we get the equivalent inventory location path

        Parameters
        ----------
            growWeekPath : str
                The path to the grow week
            invLov : str
                The inventory location where we need a path
        '''
        return self._getLocationFromGrowObj(growWeekPath,invLoc)

    def _getLocationFromGrowObj(self, growPath : str, invLoc : str) -> str:
        '''
        <private>
        Given the path to the grow week/month instance, can we get the equivalent inventory location path

        Parameters
        ----------
            growPath : str
                The path to the grow week/month instance
            invLov : str
                The inventory location where we need a path
        '''
        invCollName = self.get_collection_name(invLoc)
        newPath = growPath.replace("Converted", invCollName)
        return newPath
  
class InventoryTracking(object):
    """
    The class that has inventory tracking items hard coded for now:  will transition this to the DB at some point

    Attributes
    ----------
        tracked_items : array[str]
            Array of items that will be tracked either monthly or weekly
        weekly_items : array[str]
            Array of items that are tracked at a weekly level
        monthly_items : array[str]
            Array of items that are tracked at a monthly level
        item_lookup : dict
            Dictionary to look up the field name that the tracked item is stored on in the reserve

    Methods
    -------
        type_to_field(inType):
            Retrieve the field name for this tracked item
    """

    __instance = None

    @staticmethod 
    def getInstance():
        """ Static access method. """
        if InventoryTracking.__instance == None:
            InventoryTracking()
        return InventoryTracking.__instance

    def __init__(self):
        if InventoryTracking.__instance != None:
            raise Exception("InventoryTracking is a singleton, use getInstance!!")
        else:
            self.tracked_items = ['Plants','Vase','Box','Branches','Ethyl Block',
                                'Heat Pack','Insert','Pick','Simple Wick','Sleeve',
                                'Tag','Top Dressing','Tray']
            self.weekly_items = ['Plants']
            self.item_lookup = {'Vase':'Vase_Style',
                                'Ethyl Block':'Ethyl_Block',
                                'Heat Pack':'Heat_Pack',
                                'Tag':'Tag_Type',
                                'Simple Wick':'Simple_Wick',
                                'Top Dressing':'Top_Dressing'}
            self.count_item_types = ['Ethyl Block','Heat Pack']
            self.jmespath_summ = self._create_jmespath_entries()
            self.jPath_Suffix = ",".join(list(self.jmespath_summ.values()))
            
            self.monthly_items = [x for x in self.tracked_items if x not in self.weekly_items]
            InventoryTracking.__instance = self
    
    def _create_jmespath_entries(self):
        jmPath = {}
        jmPath['Plants'] = "plants: Plants[*].{plant: plant.name, qty:qty, id: plant.id, name: plant.name}"
        #jmPath['Ethyl Block'] = "ethyl_blocks: Ethyl_Block[*].{ethyl_block: ethyl_block.name, qty:qty, id: ethyl_block.id, name: ethyl_block.name}"
        jmPath['Vase'] = "vases: Vase.[{vase: name, qty: `1`, id: id, name: name}]"
        #jmPath['Box'] = "boxs: Box.[{box: name, qty: `1`, id: id, name: name}]"
        #jmPath['Branches'] = "branches: Branches.[{branch: name, qty: `1`, id: id, name: name}]"
        #jmPath['Heat Pack'] = "heat_packs: Heat_Pack[*].{heat_pack: heat_pack.name, qty:qty, id: heat_pack.id, name: heat_pack.name}"
        #jmPath['Insert'] = "inserts: Insert.[{insert: name, qty: `1`, id: id, name: name}]"
        #jmPath['Pick'] = "picks: Pick.[{pick: name, qty: `1`, id: id, name: name}]"
        #jmPath['Simple Wick'] = "simple_wicks: Simple_Wick.[{simple_wick: name, qty: `1`, id: id, name: name}]"
        #jmPath['Sleeve'] = "sleeves: Sleeve.[{sleeve: name, qty: `1`, id: id, name: name}]"
        #jmPath['Tag'] = "tags: Tag.[{tag: name, qty: `1`, id: id, name: name}]"
        #jmPath['Top Dressing'] = "top_dressings: Top_Dressing.[{top_dressing: name, qty: `1`, id: id, name: name}]"
        #jmPath['Tray'] = "trays: Tray.[{tray: name, qty: `1`, id: id, name: name}]"
        return jmPath
        
    def type_to_field(self,inType : str) -> str:
        """
        Convenience method to get the field name for an item being tracked

        Parameters
        ----------
            inType : str
                The item type being tracked, returns itself if not found
        """
        if inType in self.tracked_items:
            return self.item_lookup.get(inType,inType)
        return None
        