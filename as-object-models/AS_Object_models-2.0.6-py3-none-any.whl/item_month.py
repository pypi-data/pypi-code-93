###############################################################################################################################
# Licensed to the part of the ownership of Analytics Supply LLC.
#  All updates to this file should only be done at the sole discretion of the 
#  officers of Analytics Supply:
#  
##################################
##  Module Name:  item_month.py
##################################
#
#  Description:
#  --  This module is intended to track items in a plant recipe that need to have a monthly tracking mechanism
#  --  Each part of the recipe has a "Type" and these types are inventory items that could be tracked.
##################################
#
#  Created:  ???  Somewhere around July 2020
#
##################################
#  UPDATES:
#  Date, Issue #, Name of Developer, Short description of bug
#  9/11/2020, ct:85, Jason Bowles, Update to stop tracking items by type and name:  https://gitlab.com/AnalyticsSupply/customer-tracking/-/issues/85
#  2/28/2021, asfc:8, Jason Bowles, Allow inventory to be tracked by location
#
#
#################################################################################################################################
from pyasn1.type.univ import Boolean
from .sales_inv_utils import SalesInvBase
from datetime import datetime
import pytz
from dateutil.relativedelta import SU, relativedelta
import jmespath

from .quick_storage import QuickStorage
from .item_week_notes import NotesCollection
from .item_week_supply import SupplyCollection
from .inventory_active_items import InventoryActiveItems, InventoryTracking, InventoryLocation
from .supplier import Supplier
from .reserve_summary import ReserveSummary
from .utils import FSDocument
from .pub_sub import publish_message,UPDATE_MONTH_INVENTORY
from . import GetInstance

class ItemMonthSummary(SalesInvBase):
    """
    A class to summarize all of the ItemMonths for a given Item in a year.

    This class was created to quickly get a summary of inventory levels across months in a given year.
    The idea is to keep this up to date and then you can quickly see the inventory across multiple years

    In this doc an itemType is something that is tracked in inventory:  Vase, Insert

    And within these "Item Types" are different variations:  Pink Vase, Skull Vase, etc..

    A plant recipe will include 1 or more of an ItemType and we need to know if a reserve is using something from inventory

    UPDATES
    -------
    1. Updates to the summary are done via published info from an update to an underlying ItemMonth.
    2. The updates must be sequential so updates include:
       * Update Info
       * List of years and months to update next
    3. Since inventory from a prior month impact the current month... 
       * A refresh of January 2021, means that February 2021 must be refreshed
       * This chain is setup to go out for 24 months minimum

    ...

    Attributes
    ----------
        soft_delete : boolean
            Whether or not this record is deleted (not used)
        year : int
            The year that this ItemMonth is in
        item_type : str
            The item type, Vase, Branch, etc..
        inventory_summary : dict
            A dictionary with a summary for this ItemMonth in dict object
        id : str
            A unique identifier for the ItemMonth

    Class Methods
    -------------
        getInstanceByYearType(year, itemType):
            Get a summary for all inventory in a given itemType for a given Year
        CreateId(year, itemType):
            create a unique identifier for year and itemType combination
        _PublishYearsMonth(startMonth=None):
            create a list of years and months to refresh from a given month in the current year
        PublishRefreshLists(itemType, startMonth=None,doPublish=True):
            Create a list of entries that must be updated for an itemType, this will publish for all items in this itemType
        PublishRefreshListsName(itemType, itemId, startMonth=None,doPublish=True)
            Create a refresh list of year/months for a specific item in an itemType
        _publishRefreshListsName(refreshList):
            Internal Method to handle concurrent updates with publishing updates
        _createQsKey(itemType,itemId):
            Create a QuickStorage lookup Key
        _getItemIdPublishList(itemType, itemId, years, months, startMonth)
            Create a dictionary that can be published for this itemType and itemId
        yearMonthGreaterEq(currYearMonth, compYearMonth):
            Compare yearMonth combinations
        FinishPublishChain(publishInfo,doPublish=True):
            Do we want to publish further updates (default: True)
        PopProcessPublishStr(publishInfo, doPublish=True):
            Setup the next entry to be refreshed (list is string)
        PopProcessPublish(publishInfo,doPublish=True)
            Setup the next entry to be refreshed (list is array)
        UpdateItemMonthSummary(itemMonth):
            Update the ItemMonth Summary given an ItemMonth entry
            
        
    Methods
    -------
        add_summary(self, itemMonth):
            Takes in an instance of ItemMonth and adds to the summary and updates the underlying DB
        get_summary(self, itemId, month):
            Pull out the summary for a specific month and a specific itemId
        _getMonths(self, startMonth, endMonth="12"):
            create a list of months in an array
        summary_info(self,startMonth="01",endMonth="12"):
            Grab the summary for a given year in the ItemMonthSummary

    """
    ext_fields = ['year', 'item_type', 'inventory_summary','soft_delete', 'parent_path','path']
    COLLECTION_NAME = 'application_data'
    valid_item_types = ['Vase']

    def __init__(self, fsClient, **kwargs):
        self.soft_delete = kwargs.get('soft_delete',False)
        self.year = kwargs.get('year',None)
        self.item_type = kwargs.get('item_type',None)
        self.inventory_summary = kwargs.get('inventory_summary',{})

        super(ItemMonthSummary,self).__init__(fsClient,**kwargs)

    def base_path(self):
        return ItemMonthSummary.__basePath(self._fsClient,invLoc=self.inventory_location)

    @classmethod
    def basePath(cls):
        return ItemMonthSummary.__basePath(ItemMonthSummary.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return f'{ItemMonthSummary.COLLECTION_NAME}/{inClient.company}/Sales_Inventory/Converted/ItemMonthSummary'

    @classmethod
    def getInstance(cls,fsDocument):
        ref,snap = ItemMonthSummary.getDocuments(fsDocument)
        docDict = snap.to_dict() if snap.exists else {}
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        return ItemMonthSummary(ItemMonthSummary.get_firestore_client(),**docDict)

    @classmethod
    def getInstanceByYearType(cls, year, itemType):
        """
        Get a summary for all inventory in a given itemType and year

        Parameters
        ----------
            year : int
                The year from which to get the summary
            itemType : str
                The itemType to grab the summary for
        """
        docId = cls.CreateId(year,itemType)
        docPath = f"{cls.basePath()}/{docId}"
        return cls.getInstance(cls.get_firestore_client().document(docPath))

    @classmethod
    def CreateId(cls, year, itemType):
        """
        Create an unique identifer for your year/itemType combination

        Parameters
        ----------
            year : int
                The year for the summary
            itemType : str
                The itemType for the summary
        """
        return f"{str(year)}__{itemType.replace(' ','_')}"

    @property
    def id(self):
        """
        This will be the document id in the Database
        """
        return ItemMonthSummary.CreateId(self.year,self.item_type)

    @classmethod
    def _PublishYearsMonths(cls, startMonth=None):
        """
        Grab a list of months and years to do a publish of summary update
        The refresh will start from the current year and the month given, if 

        Parameters
        ----------
            startMonth : str
                The month from which to start the refresh lists
                (format: <year>_<month>, i.e. 2021_02)
        """
        years = [(datetime.now().year-1)+x for x in range(3)]
        months = [str(x+1).zfill(2) for x in range(12)]
        if startMonth is None:
            startMonth = str(years[0])+"_"+months[0]
        
        return years, months, startMonth

    @classmethod
    def PublishRefreshLists(cls, itemType, invLoc, startMonth=None,doPublish=True):
        '''
        Create a list of entries that must be updated for an itemType, this will publish \
            for all items in this itemType

        Updates are now going to be by item_id: (ct:85)

        Parameters
        ----------
            itemType : str
                The item type we want a refresh list for:  Vase, Insert, etc.
            invLoc : str
                The inventory location that will be used for refreshing
            startMonth : str
                The month from which to start the refresh lists
                (format: <year>_<month>, i.e. 2021_02)
            doPublish : boolean
                Do we want to publish the refresh on the pub/sub topic

        '''
        years, months, startMonth = cls._PublishYearsMonths(startMonth)

        ia_items = InventoryActiveItems.get_all_active(itemType) #ct:85
        publish_lists = []
        for key in ia_items.keys():
            ia_item = ia_items[key]
            publish_lists.append(cls._getItemIdPublishList(itemType,ia_item.id,years,months,startMonth,invLoc)) #ct:85

        for pl in publish_lists:
            if doPublish:
                strGrowMonths = ":".join(pl['grow_months'])
                pubList = {"item_id":pl['item_id'],'item_type':pl['item_type'],'inventory_location': invLoc,'grow_months':strGrowMonths,'start_month':startMonth}
                publish_message(UPDATE_MONTH_INVENTORY,'Start Processing Refresh',pubList)

        return publish_lists
    
    @classmethod
    def PublishRefreshListsName(cls, itemType, itemId, invLoc, startMonth=None, doPublish=True): #ct:85
        '''
        Create a refresh list of year/months for a specific item in an itemType

        Updates are now going to be by item_id: (ct:85)

        Parameters
        ----------
            itemType : str
                The item type we want a refresh list for:  Vase, Insert, etc.
            itemId : str
                The specific identifier for the item we want refreshed
            invLoc : str
                The inventory location that will be used for refreshing
            startMonth : str
                The month from which to start the refresh lists
                (format: <year>_<month>, i.e. 2021_02)
            doPublish : boolean
                Do we want to publish the refresh on the pub/sub topic
        '''
        years, months, startMonth = cls._PublishYearsMonths(startMonth)
        nameRefreshList = cls._getItemIdPublishList(itemType, itemId, years, months, startMonth, invLoc)
        if doPublish:
            strGrowMonths = ":".join(nameRefreshList['grow_months'])
            pubList = {"item_id":nameRefreshList['item_id'],
                       'item_type':nameRefreshList['item_type'],
                       'inventory_location':nameRefreshList['inventory_location'],
                       'grow_months':strGrowMonths,
                       'start_month':startMonth}
            publish_message(UPDATE_MONTH_INVENTORY,'Start Processing Name Refresh',pubList)
        return nameRefreshList
    
    @classmethod
    def _publishRefreshListsName(cls, refreshList):
        """
        Internal Method to handle concurrent updates with publishing updates.  If a refresh is in process,
        While the refresh is taking place, a placeholder is added and then cleaned out once 
        the refresh is complete

        Parameters
        ----------
            refreshList : dict
                item_type : str
                    The ItemType being refreshed
                item_id : str
                    The itemId in the itemType being refreshed
                inventory_location : str
                    The inventory location that will be used for refreshing
                grow_months : array
                    An array of months to be refreshed
        """
        qsKey = cls._createQsKey(refreshList['item_type'],refreshList['item_id'],refreshList['inventory_location'])
        qsVal = QuickStorage.getValue(qsKey)
        if qsVal is None:
            refreshList['added_months'] = []
            QuickStorage.setValue(qsKey,refreshList,expireMins=5)
            strGrowMonths = ":".join(refreshList['grow_months'])
            pubList = {"item_id":refreshList['item_id'],
                       'item_type':refreshList['item_type'],
                       'inventory_location':refreshList['inventory_location'],
                       'grow_months':strGrowMonths,
                       'start_month':refreshList.get('start_month','')}
            publish_message(UPDATE_MONTH_INVENTORY,'Start Processing Name Refresh',pubList)
        else:
            print(f"This item combo (itemType: {refreshList['item_type']}, itemId: {refreshList['item_id']}, invLoc: {refreshList['inventory_location']} ) is in the middle of a refresh.. will try later..")
            gms = qsVal['grow_months']
            for gm in refreshList['grow_months']:
                if not gm in gms:
                    qsVal['added_months'].append(gm)
            QuickStorage.setValue(qsKey,qsVal,expireMins=5)

    @classmethod
    def _createQsKey(cls,itemType, itemId,invLoc) -> str:
        """
        Create a QuickStorage lookup Key

        Parameters
        ----------
            itemType : str
                The item Type for the lookup
            itemId : str
                the unique id for the item
            invLoc : str
                The inventory location that will be used for refreshing
        """
        return f"{itemType}__{itemId}__{invLoc}__refresh"

    @classmethod
    def _getItemIdPublishList(cls, itemType, itemId, years, months, startMonth, invLoc) -> dict:
        '''
        Create a dictionary that can be published for this itemType and itemId
        Updates are now going to be by item_id: (ct:85)

        Parameters
        ----------
            itemType : str
                The item type we want a refresh list for:  Vase, Insert, etc.
            itemId : str
                The specific identifier for the item we want refreshed
            startMonth : str
                The month from which to start the refresh lists
                (format: <year>_<month>, i.e. 2021_02)
            years : array
                list of years to publish
            months : array
                List of months to publish
            invLoc : str
                The inventory location that will be used for refreshing
        '''
        itemList = {"item_type": itemType,"item_id": itemId, "inventory_location": invLoc, "grow_months": []}
        for year in years:
            for month in months:
                growMonth = str(year)+"_"+month
                if cls.yearMonthGreaterEq(growMonth,startMonth):
                    itemList['grow_months'].append(growMonth)
        itemList['grow_months'].sort()
        itemList['grow_months'].reverse()
        return itemList

    @classmethod
    def yearMonthGreaterEq(cls, currYearMonth, compYearMonth):
        """
        Method to compare a given yearMonth combo with another returns True if curr is greater or equal to comp

        Parameters
        ----------
            currYearMonth : str
                Current Year and Month:  i.e. 2021_02
            compYearMonth : str
                comparison year and month: i.e. 2021_01
        """
        return int(currYearMonth.replace("_","")) >= int(compYearMonth.replace("_",""))

    @classmethod
    def FinishPublishChain(cls,publishInfo,doPublish=True):
        """
        Final method to clean up Quick Storage after finishing a refresh

        Parameters
        ----------
            publishInfo : dict
                item_type : str
                    The ItemType being refreshed
                item_id : str
                    The itemId in the itemType being refreshed
                inventory_location : str
                    The inventory location for the tracking
                grow_months : array
                    An array of months to be refreshed
            doPublish : boolean
                Do we want to publish further updates (default: True)
        """
        keys = list(publishInfo.keys())
        if 'item_type' in keys and 'item_id' in keys:
             print(f"Finishing Publish String.. type: {publishInfo['item_type']}, id: {publishInfo['item_id']}, inventory location: {publishInfo['inventory_location']}")
             qsKey = cls._createQsKey(publishInfo['item_type'],publishInfo['item_id'],publishInfo['inventory_location'])
             qsVal = QuickStorage.getValue(qsKey)
             if qsVal is not None:
                 QuickStorage.deleteValue(qsKey)
                 added_months = qsVal.get('added_months',[])
                 if len(added_months) > 0:
                     startMonth = min(added_months)
                     print("Restarting a previously delayed refresh... this prevents a document contention..hopefully")
                     cls.PublishRefreshListsName(publishInfo['item_type'], publishInfo['item_id'], publishInfo['inventory_location'],startMonth, doPublish)
    
    @classmethod
    def PopProcessPublishStr(cls,publishInfo,doPublish=True):
        '''
        This looks to process the next refresh in the list.  If the list of months is empty, then the refrehs is complete
           The months is stored as a string (for simplicity), so this extracts that into a list
        Updates are now going to be by item_id: (ct:85)

        Parameters
        ----------
            publishInfo : dict
                item_type : str
                    The ItemType being refreshed
                item_id : str
                    The itemId in the itemType being refreshed
                grow_months : str
                    An string of months separated by ':'
                inventory_location : str
                    The location where the inventory is tracked
            doPublish : boolean
                Do we want to publish further updates (default: True)
                
        '''
        if publishInfo is None or publishInfo == {}:
            return None
        
        if publishInfo.get('grow_months',None) is None:
            cls.FinishPublishChain(publishInfo,doPublish)
            return None
        elif publishInfo['grow_months'] == '':
            cls.FinishPublishChain(publishInfo,doPublish)
            return None

        if publishInfo.get('item_type', None) is None:
            return None
        
        if publishInfo.get('item_id',None) is None:
            return None

        publishInfo['grow_months'] = publishInfo['grow_months'].split(":")
        return cls.PopProcessPublish(publishInfo,doPublish)

    @classmethod
    def PopProcessPublish(cls,publishInfo,doPublish=True):
        '''
        Given the dict of update, lets you publish the next round of refreshes
        if emtpy list of refreshes... calls FinishPublishChain
        Updates are now going to be by item_id: (ct:85)

        Parameters
        ----------
            publishInfo : dict
                item_type : str
                    The ItemType being refreshed
                item_id : str
                    The itemId in the itemType being refreshed
                grow_months : array
                    An array of months to be refreshed
                inventory_location : str
                    The location where the inventory is tracked
            doPublish : boolean
                Do we want to publish further updates (default: True)

        '''
        if len(publishInfo['grow_months']) == 0:
            cls.FinishPublishChain(publishInfo,doPublish)
            return None

        gms = publishInfo['grow_months']
        itemType = publishInfo['item_type']
        itemId = publishInfo['item_id']
        inventory_location = publishInfo['inventory_location']
        startMonth = publishInfo.get('start_month','')
        growMonth = gms.pop()

        #ims = ItemMonthSummary.getInstanceByYearType(growMonth.split("_")[0],itemType)
        
        try:
            im = ItemMonth.getItemMonthInstance(inventory_location,growMonth,itemType,itemId)
        except Exception:
            print(f"Not able to pull Item Month ({growMonth}) for item: {itemType} - {itemId}, in location: {inventory_location}")
            return None

        print(f"Refreshing... ItemMonth for month: ({growMonth}) for item: {itemType} - {itemId}, in location: {inventory_location}")
        updResult = im._refreshInventoryLevels()
        
        #ims.add_summary(im)
        # 8/22/2021  Not sure we still need this because we've updated pages
        if doPublish:
            if updResult['updated'] or (growMonth == publishInfo.get('start_month',None)):
                cls.doRePublish(gms, itemType, itemId, inventory_location, startMonth)
            else:
                ## only stop if the year_month is greater than the current date and hasn't changed
                nowDate = int(f'{datetime.now().year}{str(datetime.now().month).zfill(2)}')
                compDate = int(growMonth.strip('_'))
                if nowDate >= compDate:
                    cls.doRePublish(gms, itemType, itemId, inventory_location, startMonth)
                else:
                    print(f"Refresh for Item Month: {growMonth}, {itemType}:{itemId}, did not change... refreshing is stopping")

        return im.dict_summary()

    @classmethod
    def doRePublish(cls, gms, itemType, itemId, inventory_location, startMonth):
        strGms = ":".join(gms)
        newPubInfo = {'item_type':itemType,'item_id':itemId,'inventory_location':inventory_location,'grow_months':strGms,'start_month':startMonth}
        publish_message(UPDATE_MONTH_INVENTORY,'Process Inventory Refresh',newPubInfo)

    @classmethod
    def UpdateItemMonthSummary(cls, itemMonth):
        """
        Update the Month Summary given a specific itemMonth

        Parameters
        ----------
            itemMonth : ItemMonth
                The ItemMonth that has the inventory data to update the summary
        """
        ims = ItemMonthSummary.getInstanceByYearType(itemMonth.year,itemMonth.item_type)
        ims.add_summary(itemMonth)

    def add_summary(self, itemMonth):
        """
        Takes in an instance of ItemMonth and adds to the summary and updates the underlying DB

        Parameters
        ----------
            itemMonth : ItemMonth
                The ItemMonth we are adding to the summary
        """
        month = itemMonth.grow_month.split("_")[1]
        updateData = itemMonth.dict_summary()
        month_summary = self.inventory_summary.get(month,{})
        mon_loc_summary = month_summary.get(itemMonth.inventory_location,{})
        mon_loc_summary[itemMonth.item_id] = updateData
        month_summary[itemMonth.inventory_location] = mon_loc_summary
        self.inventory_summary[month] = month_summary
        self.update_ndb()

    def get_summary(self, itemId, month, invLoc=None):
        """
        Pull out the summary for a specific month and a specific itemId

        Parameters
        ----------
            itemId : str
                String id for the item we want a summary
            month : str
                The month for which we want the summary ("01","02","03", ..., "12")
        """

        locations = [x for x in InventoryLocation.getInstance().inventory_locations if invLoc is None or x == invLoc]
        resp = []
        month_summary = self.inventory_summary.get(month,{})
        for loc in locations:
            mon_loc_summary = month_summary.get(loc,None)
            if mon_loc_summary is not None:
                entry = mon_loc_summary.get(itemId,None)
                if entry is not None:
                    resp.append(entry)
        if len(resp) == 1:
            return resp[0]
        
        if len(resp) > 1:
            resp[0]['status']['inventory_location'] = locations
            resp[0]['stats']['set_inventory'] = sum([int(x['stats']['set_inventory']) for x in resp])
            resp[0]['stats']['added_inventory'] = sum([int(x['stats']['added_inventory']) for x in resp])
            resp[0]['stats']['remaining_inventory'] = sum([int(x['stats']['remaining_inventory']) for x in resp])
            resp[0]['stats']['prev_month_inventory'] = sum([int(x['stats']['prev_month_inventory']) for x in resp])
            resp[0]['stats']['month_reserves'] = sum([int(x['stats']['month_reserves']) for x in resp])
            return resp[0]

        return None
    
    def _getMonths(self, startMonth, endMonth="12"):
        """
        Inner (private) function to create a list of months in an array for getting a summary, the startMonth 
           must come before the endMonth

        Parameters
        ----------
            startMonth : str
                The month that the array should be begin
            endMonth : str
                The month that the array should end
        """
        return [str(x+int(startMonth)).zfill(2) for x in range(13-int(startMonth)) if (x+int(startMonth)) <= int(endMonth)]

    def summary_info(self, startMonth="01", endMonth="12",invLoc=None):
        """
        Function to grab the summary for the Summary year for the months supplyed 
        i.e. given 01 as the startMonth and 04 as the endMonth, we will see a summary for months 1 - 4

        Parameters
        ----------
            startMonth : str
                The month that the array should be begin
            endMonth : str
                The month that the array should end
        """ 

        # TODO:  Update location information
        if int(startMonth) == 1 and int(endMonth) == 12:
            return jmespath.search("*.[*][][]",self.inventory_summary)
        else:
            mos = self._getMonths(startMonth,endMonth)
            return jmespath.search("*.[*][][]",{k : v for (k,v) in self.inventory_summary.items() if k in mos})


class ItemMonthCollection(SalesInvBase):
    """
    A Place to manage the Collection of data objects that are related to a ItemMonth:
    - Notes
    - Supply
    - Other...

    Attributes
    ----------
        _items : dict
            Loaded dictionary of active items (passed in)
        items : dict
            Loaded dictionary of active items (calculated/pulled)
        item_type : str
            The type for this inventory collection
        inventory_location : str
            The location where inventory will be tracked
        grow_month : str
            The string representation of the grow month
        _in_growMonthParent : object
            this is the db object representation of the parent GrowMonth entry
        _loaded_items : dict
    
    Class Methods
    -------------
        getInstance(docRef, itemType, gmParent):
            Grab an instance of ItemCollectionMonth
        getOrCreateInstance(invLoc, item_type, gmParent):
            Grab an instance and if it doesn't exit, create it
        GetOrCreateItemMonth(imPath, itemMonthCollection, item_id):
            Grab the ItemMonth, and if it doesn't exist create it
    

    Methods
    -------
        post_create_activities():
            load up needed attributes after class creation
        load_collections():
            Load up collections of data... notes, supply, month reserves
        load_item_months():
            From the active items list, load them into memory
        load_item_months():
            Load the Item Months
        refresh_loaded_items():
            Refresh the items that have been loaded into memory
        update_month_reserves():
            Go through the reserves for this month and load them for refreshing
        create_itemmonth_entry(item, gwPar):
            Create an ItemMonth Entry based on the item and the GrowMonth Parent
        get_itemmonth(itemId):
            Grab the loaded ItemMonth using the itemId
        get_supply():
            Get a link to the supply collection
        get_notes():
            Get a link to the notes collection
        update_ndb()
            Overloaded update method since this is a wrapper class
            
    """
    ext_fields = ['items','item_type','grow_month','inventory_location','soft_delete','parent_path','path']
    COLLECTION_NAME = 'application_data'
    collection = {}

    IWS = "Supply"
    IWN = "Notes"

    def __init__(self,fsClient, **kwargs):
        self.soft_delete = kwargs.get('soft_delete',False)
        self._items = kwargs.get('items',None)
        self.item_type = kwargs.get('item_type','')
        self.grow_month = kwargs.get('grow_month','')
        self.inventory_location = kwargs.get('inventory_location')
        self._in_growMonthParent = kwargs.get('_growMonthParent',None)
        self._loaded_items = {}

        super(ItemMonthCollection,self).__init__(fsClient, **kwargs)
    
    def post_create_activities(self):
        """
        After init of the class object... load up relevant data
        1. Collections
        2. Items (Active Items)
        3. Item Months
        """
        self.load_collections()
        self.load_items()
        self.load_item_months()

    def load_collections(self):
        """
        Load up collections of data Notes, Supply and Reserves
        """
        #self._notes_collection = MonthNotesCollection.getOrCreateInstance(self._fsClient.document(self.notes_path),self._in_growMonthParent)
        self._notes_collection = NotesCollection.GetOrCreateItemWeekNotes(self.item_type,self.inventory_location,'Month',self.grow_month)
        #self._supply_collection = MonthSupplyCollection.getOrCreateInstance(self._fsClient.document(self.supply_path),self._in_growMonthParent)
        self._supply_collection = SupplyCollection.GetOrCreateItemWeekSupply(self.item_type,self.inventory_location,'Month',self.grow_month)
        self._month_reserves = ItemMonthReserves.getOrCreateMonthReserve(self._in_growMonthParent,self.item_type,self.inventory_location)

    def load_items(self):
        """
        From the active items list, load them into memory
        """
        if self._items is None:
            ia_items = InventoryActiveItems.get_all_active(self.item_type)
            self._items = {k:v.get_dict() for k,v in ia_items.items()}
    
    def load_item_months(self):
        """
        Load the Item Months for this collection
        """
        item_ids = self.items.keys()
        for item_id in item_ids:
            inPath = ItemMonth.GetPathNm(self._growMonthParent,self.item_type,item_id,self.inventory_location)
            ItemMonthCollection.GetOrCreateItemMonth(inPath,self,item_id)

    @classmethod
    def GetOrCreate__ItemMonth(cls,invLoc, growMonthId, itemType, itemId):
        ItemMonthCollection.getOrCreateInstance(invLoc,itemType)

    
    @classmethod
    def GetOrCreateItemMonth(cls, imPath, itemMonthCollection, item_id):
        '''
        Grab the ItemMonth, and if it doesn't exist create it

        Updates to conform to matching by recipe_costing_id
        9/15/2020: ct:85

        Parameters
        ----------
            imPath : str
                path to the ItemMonth (the path will bootstrap creation)
            itemMonthCollection : ItemMonthCollection
                An instance of ItemMonthCollection to help create the ItemMonth
            item_id : str
                this will be the unique id of the identifier for the Active Item
        '''
        fsDocument = ItemMonth.get_firestore_client().document(imPath)
        ref,snap = ItemMonth.getDocuments(fsDocument)
        item_dict = snap.to_dict() if snap.exists else {}
        item_dict['fs_docSnap'] = snap
        item_dict['fs_docRef'] = ref
        item_dict['_itemCollection'] = itemMonthCollection
        item_dict['_notesCollection'] = itemMonthCollection._notes_collection
        item_dict['_supplyCollection'] = itemMonthCollection._supply_collection
        item_dict['_growMonthParent'] = itemMonthCollection._growMonthParent
        if not snap.exists:
            imcItem = itemMonthCollection.items[item_id]
            item_dict['name'] = imcItem['name']
            item_dict['item_name'] = imcItem['name']
            item_dict['item_id'] = imcItem['id']
            item_dict['grow_month'] = itemMonthCollection.grow_month
            item_dict['item_type'] = itemMonthCollection.item_type
            item_dict['item'] = imcItem
        im = ItemMonth(itemMonthCollection._fsClient,**item_dict)
        itemMonthCollection._loaded_items[item_id] = im
        if not im.exists:
            im.update_ndb()
    
    def refresh_loaded_items(self):
        """
        Iterate through the loaded items and run the ItemMonth.refreshInventoryLevels()

        """
        for item_id in list(self._loaded_items.keys()):
            im = self._loaded_items[item_id]
            im._refreshInventoryLevels()
        
        return jmespath.search('*',self._loaded_items)

    
    @property
    def items(self):
        """
        Creates the `.items` attribute if `._items` doesn't exist
        """
        if self._items is None:
            ia_items = InventoryActiveItems.get_all_active(self.item_type) #ct:85
            self._items = {k:v.get_dict() for k,v in ia_items.items()} #ct:85
        return self._items

    def update_month_reserves(self):
        self._month_reserves = ItemMonthReserves.getOrCreateMonthReserve(self._growMonthParent,self.item_type,self.inventory_location)
        self._month_reserves.load_reserves()

    def base_path(self):
        return self.im_location_path+'/Items'
    
    @property
    def im_location_path(self):
        return ItemMonthCollection._imLocationPath(self._growMonthParent.path,self.inventory_location)

    @classmethod
    def _imLocationPath(cls,gmPath,invLoc):
        return InventoryLocation.getInstance().getGrowMonthPath(gmPath,invLoc)

    @property
    def id(self):
        return self.item_type

    @property
    def notes_path(self):
        return f'{self.im_location_path}/{self.IWN}/{self.item_type}'
    
    @property
    def supply_path(self):
        return f'{self.im_location_path}/{self.IWS}/{self.item_type}'
    
    @property
    def month_reserve_path(self):
        return f'{self.im_location_path}/MonthReserves/{self.item_type}'

    @classmethod
    def _get_active_items(cls,item_type):
        return InventoryActiveItems.get_all_active(item_type)

    @classmethod
    def getInstance(cls,invLoc, docRef,itemType, gmParent):
        """
        Get an instance of ItemMonthCollection

        Parameters
        ----------
            docRef : DocumentReference
                the document reference instance of this object
            invLoc : str
                The inventory location for the ItemMonthCollection
            itemType : str
                The item type for this ItemMonthCollection
            gmParent : GrowMonth
                The GrowMonth instance reference
        """
        key = f'{str(itemType)}__{invLoc}__{str(gmParent.id)}'
        imc = ItemMonthCollection.collection.get(key,None)
        if imc is None:
            ref,snap = ItemMonthCollection.getDocuments(docRef)
            docDict = snap.to_dict() if snap.exists else {}
            docDict['fs_docSnap'] = snap
            docDict['fs_docRef'] = ref
            docDict['item_type'] = itemType
            docDict['inventory_location'] = invLoc
            docDict['_growMonthParent'] = gmParent
            imc = ItemMonthCollection(ItemMonthCollection.get_firestore_client(),**docDict)
            ItemMonthCollection.collection[key] = imc
        return imc

    @classmethod
    def getOrCreateInstance(cls,invLoc, item_type,gmParent):
        """
        Grab an instance of ItemMonthCollection, if it doesn't exist create it

        Paramenters
        -----------
            invLoc : str
                The inventory location for the ItemMonthCollection
            item_type : str
                The item type for this ItemMonthCollection
            gmParent : GrowMonth
                The GrowMonth instance that this is based on
        """
        #key = str(item_type)+'_'+str(gmParent.id)
        key = f'{str(item_type)}__{invLoc}__{str(gmParent.id)}'
        imc = ItemMonthCollection.collection.get(key,None)
        if imc is None:
            gmInvPath = InventoryLocation.getInstance().getGrowMonthPath(gmParent.path,invLoc)
            imc = cls.getInstance(invLoc, gmParent._fsClient.document(f"{gmInvPath}/Items/{item_type}"),item_type, gmParent)
            if not imc.exists:
                imc.item_type = item_type
                imc.grow_month = gmParent.id
                #iwc.update_ndb(True)
                imc.post_create_activities()
            ItemMonthCollection.collection[key] = imc
        return imc

    @property
    def _growMonthParent(self):
        if self._in_growMonthParent is None:
            gmPath = InventoryLocation.getInstance().get_grow_path(self.parent_path)
            gwParDoc = self.get_firestore_client().document(gmPath)
            self._in_growMonthParent = GetInstance("GrowMonth",gwParDoc)
        return self._in_growMonthParent

    def create_itemmonth_entry(self, item, gmParent):
        ''' 
        Create an ItemMonth Entry based on the item and the GrowMonth Parent
        Input is going to be recipe item 

        Parameters
        ----------
            item : FSObjSummary
                The item that is representing the ItemMonth
            gmParent : GrowMonth
                The GrowMonth instance for this itemmonth entry
        '''
        iw = self._loaded_items.get(item.id,None)
        if iw is None:
            item_dict = {}
            itemObj = self._get_sb_instance_by_path(item.path)
            item_dict['item'] = {'name':itemObj.name,'id':itemObj.id,'path':itemObj.path}
            item_dict['name'] = itemObj.name
            item_dict['inventory_location'] = self.inventory_location
            item_dict['item_type'] = self.item_type
            item_dict['item_id'] = itemObj.id
            item_dict['grow_month'] = self.grow_month
            item_dict['actual'] = None
            item_dict['inventory_set'] = False
            item_dict['color_groupings'] = {}
            item_dict['_growMonthParent'] = gmParent
            item_dict['_itemCollection'] = self
            item_dict['_notesCollection'] = self._notes_collection
            item_dict['_supplyCollection'] = self._supply_collection
            iw = ItemMonth(self._fsClient,**item_dict)
            iw.update_ndb()
        return iw

    def get_itemmonth(self,itemId):
        """
        Get an item month from the loaded items
        
        Parameters
        ----------
            itemId : str
                The id that represents the active item for the needed ItemMonth
        """
        return self._loaded_items.get(itemId,None)

    def get_supply(self):
        """
        Return an object representation of the supply collection
        """
        return self._supply_collection

    def get_notes(self):
        """
        Return an object representation of the notes collection
        """
        return self._notes_collection

    def update_ndb(self, doCreate=False):
        """
        Overloaded update method since this is a wrapper class

        Calls the embedded update_ndb for each item
        """
        if self.items is None:
            self.items = {}

        item_ids = self._loaded_items.keys()
        for item_id in item_ids:
            self.items[item_id] = self._loaded_items[item_id].get_dict()

        super(ItemMonthCollection,self).update_ndb(doCreate)

class ItemMonthReserves(SalesInvBase):
    """ 
    This represents a summary of reserves for this Item

    A Document is created for each itemType
    
    Attributes
    ----------
        item_types : array[str]
            Array of items that are tracked at a the monthly inventory level
        week_summaries : dict
            dictionary summary of each item in a week
        month_summary : dict
            summary of items that are tracked monthly
        _grow_month : str
            The GrowMonth id that this tracked i.e. 2020_11 (<year>_<month>)
        _in_growMonthParent : GrowMonth
            The GrowMonth instance that this is tracked under
        inventoryLocation : str
            The location the inventory is tracked
        
    Class Methods
    -------------
        getInstance(fsDocument,gmParent):
            Get an instance of the ItemMonthReserve
        getOrCreateMonthReserve(gmParent, itemType, invLoc,load_doc=True):
            Get a link to the ItemMonthReserve and create if it doesn't exist
    
    Methods
    -------
        load_reserves():
            Initialize the reserve summaries and then pull them in and create a new summary
        load_month_reserves():
            Load up the reserves for the month and summarize
        load_week_reserves():
            Load up the reserves and summarize by week       
    """
     
    ext_fields = ['week_summaries','month_summary','item_type','grow_month','inventory_location','soft_delete','parent_path','path','item_type']
    COLLECTION_NAME = 'application_data'

    def __init__(self, fsClient, **kwargs):
        self.inventItems = InventoryTracking.getInstance()
        #self.item_type = self.inventItems.monthly_items
        self.soft_delete = kwargs.get('soft_delete',False)
        self.week_summaries = kwargs.get('week_summaries',{})
        self.month_summary = kwargs.get('month_summary',{})
        self._grow_month = kwargs.get('grow_month',None)
        self.item_type = kwargs.get('item_type',None)
        self._in_growMonthParent = kwargs.get('_growMonthParent',None)
        self.invLocObj = InventoryLocation.getInstance()
        self._inventory_location = kwargs.get('inventoryLocation',None)
        super(ItemMonthReserves, self).__init__(fsClient, **kwargs)

    def base_path(self):
        return self.im_location_path+'/MonthReserves'
    
    @property
    def im_location_path(self):
        return ItemMonthCollection._imLocationPath(self._growMonthParent.path,self.inventory_location)

    @property
    def inventory_location(self):
        if self._inventory_location is None:
            invLoc = InventoryLocation.getInstance().get_location_from_path(self.path)
            self._inventory_location = invLoc
        return self._inventory_location
    
    @classmethod
    def getInstance(cls,fsDocument,gmParent):
        """
        Get an instance of ItemMonthReserve

        Parameters
        ----------
            fsDocument : DocumentReference
                Reference to the firestore document
            gmParent : GrowMonth
                Instance of the GrowMonth object that is a parent to this
            
        """
        ref,snap = ItemMonthReserves.getDocuments(fsDocument)
        docDict = snap.to_dict() if snap.exists else {}
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        docDict['_growMonthParent'] = gmParent
        imr = ItemMonthReserves(ItemMonthReserves.get_firestore_client(),**docDict)
        imr.item_type = imr.id
        return imr

    @classmethod
    def getOrCreateMonthReserve(cls, gmParent: object, itemType : str, invLoc : str, load_doc=True):
        """
        Using the GrowMonth parent, get a link to the ItemMonth reserve

        Parameters
        ----------
            gmParent : GrowMonth
                The instance of GrowMonth that is the parent to the Reserves
            itemType : str
                The item_type for this summary
            invLoc : str
                The location where inventory is tracked
            load_doc : boolean
                whether or not to load reserves if this is a first call
                
        """
        basePath = ItemMonthCollection._imLocationPath(gmParent.path,invLoc)
        imr = cls.getInstance(gmParent._fsClient.document(f'{basePath}/MonthReserves/{itemType}'), gmParent)
        if not imr.exists and load_doc:
            imr.load_reserves()
        return imr

    def load_reserves(self):
        """
        Initialize the week summaries and month summary and reload from reserves
        """
        self.week_summaries = {}
        self.load_week_reserves()

        self.month_summary = {}
        self.load_month_reserves()
        self.update_ndb()

    def load_month_reserves(self):
        """
        This method goes through and pulls the reserves by week to build the month summary
        """
        gws = self._growMonthParent.grow_weeks
        #for itemType in self.item_types:
            #typeSummary = self.month_summary.get(itemType,{})
        typeSummary = {}
        for gw in gws:
            weekSummary = self._load_growweek_reserves(gw,'total')
            for key in weekSummary.keys():
                amt = weekSummary[key]
                monthTotal = typeSummary.get(key,0)
                monthTotal = monthTotal + amt
                if key != '':
                    typeSummary[key] = monthTotal    
        self.month_summary = typeSummary

    def load_week_reserves(self):
        """
        Load up the reserves for the weeks and create a summary
        """
        gws = self._growMonthParent.grow_weeks
        #for itemType in self.item_types:
        #typeSummary = self.week_summaries.get(self.item_type,{})
        for gw in gws:
            item_week_summ = self._load_growweek_reserves(gw)
            for itemId in item_week_summ.keys():
                nameList = self.week_summaries.get(itemId,[])
                reserves = item_week_summ[itemId]
                for reserve in reserves:
                    reserve['finish_week'] = gw
                    nameList.append(reserve)
                if itemId != '':
                    self.week_summaries[itemId] = nameList
            #self.week_summaries[itemType] = typeSummary
    
    def _load_growweek_reserves(self,growWeekId,summType='by_item'):
        """
        Given a week of reserves return a summary
        """
        rs = ReserveSummary.getReserveSummary(growWeekId)
        summ = rs.getReserveItemAmts(self.item_type,invLoc=self.inventory_location)
        return summ.get(summType,{})
    
    @property
    def grow_month(self):
        return self._growMonthParent.id

    @property
    def _growMonthParent(self):
        if self._in_growMonthParent is None:
            gmPath = InventoryLocation.getInstance().get_grow_path(self.parent_path)
            gwParDoc = self.get_firestore_client().document(gmPath)
            self._in_growMonthParent = GetInstance("GrowMonth",gwParDoc)
        return self._in_growMonthParent
        

class ItemMonth(SalesInvBase):
    """ 
    This is the class represents all items that are available during a specific Month
    Setup by "item_type" in the RecipeCosting collection 


    Attributes
    ----------
        inventory_location : str
            the location where the inventory is stored
        item_type : str
            the item type for the ItemMonth instance
        item_id : str
            the unique id for the item this ItemMonth is tracking
        _collection_parent : object
            The collection object parent, should be the ItemMonthCollection
        _notesCollection : object
            The reference to the notes regarding this ItemMonth
        _supplyCollection : object
            The reference to the suppliers for this ItemMonth
        item : RecipeCosting
            The reference to the Recipe Costing entry (item_type and item_id reference this)
        grow_month : str
            the year and month that this ItemMonth belongs to
        reserve_total : int
            The total number of reserves for this item in this month
        actual : int
            This is the actual amount of inventory, set when somone does an inventory count
            This overrides the calculated inventory amount
        inventory_add : int
            If someone purchases more inventory, the amount purchases is added to the calculated amount
        calc_actual : int
            This is the calculated actual based on rolled over inventory minus reserves
        prev_actual : int
            this is the actual inventory for this item in the previous month
        _inventory_set : int
            This is an entered inventory amount to 'reset' the inventory for a month
        previous_inventory : int
            <placeholder not used>
        next_inventory : int
            <placeholder not used>
        _previous_month_path : str
            The path to the previous ItemMonth entry
        _next_month_path : str
            The path to the next ItemMonth entry
        color_groupings : dict
            This can be used to bucket the inventory by color
        _in_growMonthParent : object
            The object instance of the parent GrowMonth
        _inventory_location : str
            The location for this inventory, will be set by path, but store it here too!
        _supplies : array
            lazy property, sets up the ability to grab the supplies on demand
        _notes : array
            lazy property, sets up the ability to grab the notes on demand
        next : ItemMonth
            Points to the next ItemMonth for this item
        prior : ItemMonth
            Points to the previous ItemMonth for this item
        forecasts : int
            The forecast for this inventory
        reserves : List<ItemReserves>
            An array of item reserves for this specific ItemMonth
        clean_item_type : str
            The clean name of item name
    
    Class Methods
    -------------
        GetPathNm(growMonth, itemType, itemId, invLoc):
            Get the path based on the GrowMonth, ItemType and ItemId
        GetPathNmStr(growMonthPath, itemType, itemId, invLoc):
            Based on the path to the growMonth, get an instance of ItemMonth
        RefreshInventoryLevels(invLoc, growMonthId,itemType,itemId):
            Get the ItemMonth and force a refresh
        getItemMonthInstance(invLoc, growMonthId, itemType, itemId):
            Get an ItemMonth instance given the inventory location, growmonth, type and item id
        getItemMonthInstance(inPath):
            Get an instance of ItemMonth given a path to the database entry
        getInstanceItem(fsDocument):
            Get an instance of ItemMonth, may or may not exist yet
        getInstance(fsDocument):
            Get an instance of ItemMonth given the firestore document object
        CleanItemName(inName):
            create a URL safe version of an Item Name
        get_or_create(invLoc, itemType, itemInfo, growMonth):
            The class method to get an instance of ItemMonth
        CleanItemType(item_type):
            Make the standard format for the item type
    
    Methods
    -------
        _refreshInventoryLevels(repull=True):
            Internal method to refresh the inventory balance, if repull is true, get reserves again
        _getReservesTotal():
            Get the total reserves for this item from the Monthly Item Summary
        _getPrevMonthActual():
            Get the actual inventory from the previous month
        _format_month_date(monthDate):
            The monthDate field is a datetime, pull the year and month out to form the growMonth id
        add_inventory(added_inventory):
            The amount of inventory to add to the actual inventory amount, doesn't replace but adds
        set_actual(inventory_amt):
            This is a way to set the inventory and override anything set previously
        unset_actual():
            Remove the actual amount used to set the inventory
        create_note(note):
            Create a note associated to this Item for the Month inventory
        delete_note(note_id):
            Remove a note associated to this Item for Month Inventory
        create_supply(supplier_id, inForecast, confirmation_num):
            Create a supply forecast based on a supplier for this Item Month inventory
        get_itemmonth_dict():
            Get a dictionary summary of the item month
        update_groupings(grouping,reset=False): **Deprecated**
            This allows to track by color within a specific item
        update_color_grouping(color_grouping, reset=False):
            Set the inventory and split by color or other key attribute
        get_schema():
            Get the schema for big query
        get_values_dict():
            Get the values of ItemMonth in a dictionary
        got_total_reserved():
            Get all of the reserves and then count the total reserved
        iw_summary():
            The summary for this item month
        availability():
            Given the reserved amount and the inventory, what is the availability
        dict_summary():
            Get the summary for this entry.. .this will be used for ItemMonth summaries
    """

    ext_fields = ['item','name','item_name','item_id','reserve_total','item_type','grow_month','actual',
                  'inventory_add','calc_actual','prev_actual','inventory_set','color_groupings','inventory_location','set_upd_dt',
                  'soft_delete','parent_path','path']

    COLLECTION_NAME = 'application_data'
    _imr_collection = {}
    
    def __init__(self, fsClient, **kwargs):
        self.soft_delete = kwargs.get('soft_delete',False)
        #self.name = kwargs.get('name','')
        self._inventory_location = kwargs.get('inventory_location',None)
        self._item_type = kwargs.get('item_type',None)
        self._item_id = kwargs.get('item_id',None)
        self._collection_parent = kwargs.get('_itemCollection',None)
        self._notesCollection = kwargs.get('_notesCollection',None)
        self._supplyCollection = kwargs.get('_supplyCollection',None)
        self._item = kwargs.get('item',None) 
        self._set_upd_dt = kwargs.get('set_upd_dt',None)
        self._grow_month = kwargs.get('grow_month',None)
        self.reserve_total = kwargs.get('reserve_total',0)
        self.actual = kwargs.get('actual',None)
        self._inventory_add = kwargs.get('inventory_add',None)
        self.calc_actual = kwargs.get('calc_actual',None)
        self.prev_actual = kwargs.get('prev_actual',None)
        self._inventory_set = kwargs.get('inventory_set',False)
        self.previous_inventory = kwargs.get('previous_inventory',0)
        self.next_inventory = kwargs.get("next_inventory",0)
        self._previous_month_path = kwargs.get('previous_month_path',None)
        self._next_month_path = kwargs.get('next_month_path',None)
        self.color_groupings = kwargs.get('color_groupings','')
        self._in_growMonthParent = kwargs.get('_growMonthParent',None)
        if kwargs.get('fs_docRef',None) is None:
            path = ItemMonth.GetPathNmStr(self._growMonthParent.path,self.item_type,self.item_id,self._inventory_location)
            kwargs['fs_docRef'] = fsClient.document(path)

        ## Add some way to get the inventory location:
        self._inventory_location = None

        self._supplies = None
        self._notes = None
        super(ItemMonth, self).__init__(fsClient, **kwargs)
        
    
    def base_path(self):
        return ItemMonth.GetPathNm(self._growMonthParent,self.item_type,self.item_id,self.inventory_location)
    
    @property
    def set_upd_dt(self):
        if self._set_upd_dt is None:
            if self._inventory_set:
                self._set_upd_dt = datetime.now().isoformat()
        return self._set_upd_dt
    
    def refresh_set_upd_dt(self):
        self._set_upd_dt = datetime.now().isoformat()

    @classmethod
    def GetPathNm(cls,growMonth, itemType, itemId, invLoc):
        """
        Get the full path, given the GrowMonth instance, itemType and itemId

        """
        return ItemMonth.GetPathNmStr(growMonth.path,itemType,itemId, invLoc)
    
    @classmethod
    def GetPathNmStr(cls,growMonthPath : str, itemType : str, itemId : str, invLoc : str):
        """
        Based on the path to the growMonth get an instance of ItemMonth

        Parameters
        ----------
            growMonthPath : str
                String path to the growMonth
            itemType : str
                The type of item being tracked
            itemId : str
                The unique id of the specific item being tracked
        """
        invGrowMonthPath = InventoryLocation.getInstance().getGrowMonthPath(growMonthPath,invLoc)
        return invGrowMonthPath+'/Items/'+itemType+"__"+itemId

    @property
    def inventory_location(self):
        if self._inventory_location is None:
            if self.exists:
                l = InventoryLocation.getInstance().get_location_from_path(self.path)
                self._inventory_location = l
            else:
                self._inventory_location = InventoryLocation.getInstance().default_location
        return self._inventory_location
    
    @property
    def item_type(self):
        if self._item_type == '' or self._item_type is None:
            self._item_type = self.id.split("__")[0]
        return self._item_type

    @property
    def item_id(self):
        if self._item_id == '' or self._item_id is None:
            self._item_id = self.id.split("__")[1]
        return self._item_id

    @property
    def grow_month(self):
        if self._grow_month is None:
            self._grow_month = InventoryLocation.getInstance().get_grow_info(self.path)['grow_id']
        return self._grow_month
    
    @property
    def inventory_add(self):
        if self._inventory_add is None:
            self._inventory_add = jmespath.search("[*].forecast | sum(@)",self.supply)
        return self._inventory_add

    @property
    def item(self):
        if self._item is None:
            self._item = self.get_recipe_item_by_id(self.item_id)
            if self._item is not None and self._item['type'] is not None:
                del self._item['type']
        return self._item

    @property
    def previous_month_path(self):
        if self._previous_month_path is None:
            prevMonth = self._format_month_date(self.prev_month_date)
            self._previous_month_path = self.path.replace(self.grow_month,prevMonth)
        return self._previous_month_path

    @property
    def next_month_path(self):
        if self._next_month_path is None:
            nextMonth = self._format_month_date(self.next_month_date)
            self._next_month_path = self.path.replace(self.grow_month,nextMonth)
        return self._next_month_path

    @property
    def year(self):
        return self.grow_month.split("_")[0]


    @classmethod
    def RefreshInventoryLevels(cls, invLoc: str, growMonthId: str, itemType: str, itemId: str, use_imr_cache=False) -> dict:
        '''
        Added inventory location:  asfc:8

        Parameters
        ----------
            invLoc : str
                The location of the inventory (Texas, Virginia, etc.)
            growMonthId : str
                The growMonth id:  i.e. 2021_01 is January 2021
            itemType : str
                The type of item, Vase, Tag, Insert, etc..
            itemId : str
                The unique item of the item being tracked
            
        '''
        im = ItemMonth.getItemMonthInstance(invLoc, growMonthId,itemType,itemId)
        return im._refreshInventoryLevels(use_imr_cache=use_imr_cache)

    def _refreshInventoryLevels(self,repull=True,use_imr_cache=False):
        """
        Based on reserves and previous month inventory refresh the inventory of this ItemMonth
        If "repull" == True, then grab previous month inventory and reserves again

        Parameters
        ----------
            repull : boolean
                (default is True) whether or not to grab outside info again
        """
        new_calc_actual = 0
        total = self.reserve_total
        
        inv_add = self.inventory_add
        new_inv_add = self.inventory_add

        if repull:
            total = self._getReservesTotal(use_imr_cache)
            self._inventory_add = None
            new_inv_add = self.inventory_add

        doSave = False
        if self.reserve_total != total:
            self.reserve_total = total
            doSave = True
        
        if inv_add != new_inv_add:
            doSave = True

        if self.inventory_set:
            if self.actual is None:
                self.actual = 0
            new_calc_actual = self.actual - self.reserve_total
            if new_calc_actual != self.calc_actual:
                doSave = True
        else:
            pmActual = self.prev_actual
            if repull:
                pmActual = self._getPrevMonthActual()

            if pmActual is not None:
                self.prev_actual = pmActual
                new_calc_actual = self.prev_actual - self.reserve_total
                if self.prev_actual != pmActual:
                    doSave = True
            else:
                if pmActual is None:
                    # Being here means that there is no inventory set
                    #   and no previous inventory to use... so subtract
                    #   the reserve_total from zero
                    new_calc_actual = 0 - self.reserve_total
                    doSave = True

        new_calc_actual = new_calc_actual + self.inventory_add
        if new_calc_actual != self.calc_actual:
            self.calc_actual = new_calc_actual
            doSave = True
        
        if doSave or not self.exists:
            doSave = True
            self.update_ndb()
        
        return {'inventory': self.calc_actual, 'reserves': self.reserve_total, 'updated': doSave}
 
    @property
    def _growMonthParent(self):
        if self._in_growMonthParent is None:
            gmPath = InventoryLocation.getInstance().get_grow_path(self.parent_path)
            gwParDoc = self.get_firestore_client().document(gmPath.replace('/Items',''))
            self._in_growMonthParent = GetInstance("GrowMonth",gwParDoc)
        return self._in_growMonthParent
        
    def _getReservesTotal(self,use_cache=False):
        """
            Get the total reserves for this item from the Monthly Item Summary

        """
        imr = None
        imr_key = f"{self.grow_month}__{self.inventory_location}"
        if use_cache:
            imr = ItemMonth._imr_collection.get(imr_key,None)
        if imr is None:
            imr = ItemMonthReserves.getOrCreateMonthReserve(self._growMonthParent,self.item_type,self.inventory_location)
            imr.load_month_reserves()
        ItemMonth._imr_collection[imr_key] = imr
        return imr.month_summary.get(self.item_id,0)

    def _getPrevMonthActual(self):
        """
        Get the actual inventory from the previous month
        """
        pm = ItemMonth.getItemMonthInstanceByPath(self.previous_month_path)
        if pm.exists:
            return pm.calc_actual
        return None

    @property
    def month_date(self):
        return datetime.strptime(self.grow_month,"%Y_%m")

    @property
    def next_month_date(self):
        return self.month_date+relativedelta(months=1)
    
    @property
    def prev_month_date(self):
        return self.month_date+relativedelta(months=-1)

    def _format_month_date(self,monthDate) -> str:
        """
        Given a date in a month, get the GrowMonth Id

        monthDate : date
            Any date, any time
        """
        return monthDate.strftime("%Y_%m")

    def add_inventory(self, added_inventory):
        """
        The amount of inventory to add to the actual inventory amount, doesn't replace but adds

        Parameters
        ----------
            added_inventory : int
                 The amount of inventory to add to the actual amount (purchasing additional)
        """
        self._inventory_add = added_inventory
        results = self._refreshInventoryLevels(repull=False)
        return results

    @property
    def inventory_set(self):
        return self._inventory_set
    
    def set_actual(self, inventory_amt):
        '''
        This is a way to set the inventory and override anything set previously

        Parameters
        ----------
            inventory_amt : int
                The actual amount of inventory after counting
        '''
        self._inventory_set = True
        if inventory_amt != self.actual:
            self.actual = inventory_amt
            self.refresh_set_upd_dt()
            
        results = self._refreshInventoryLevels(repull=False)
        if not results['updated']:
            self.update_ndb()
    
    def unset_actual(self):
        '''
        Lets the database know that we don't care about what actual value is, compute inventory from reserves and adds
        '''
        self._inventory_set = False
        results = self._refreshInventoryLevels(repull=False)
        if not results['updated']:
            self.update_ndb()

    @property
    def item_name(self):
        return ItemMonth.CleanItemName(self.item.get('name','NoItemName'))
    
    @property
    def name(self):
        return self.item.get('name',"No Item Name")

    @property
    def get_lookup_entry(self):
        return {'key': self.item_id, 'value': self.item.get('name','NoItemName')}
    
    #@property
    #def item_id(self):
    #    return self.item.get('id',"NoItemId")

    @property
    def item_path(self):
        return self.item.get('path',"NoItemPath")

    #@property
    #def _growMonthParent(self):
    #    if self._in_growMonthParent is None:
    #        gwParDoc = self.get_firestore_client().document(self.parent_path)
    #        self._in_growMonthParent = GetInstance("GrowMonth",gwParDoc)
    #    return self._in_growMonthParent

    @classmethod
    def getItemMonthInstance(cls, invLoc: str, growMonthId: str, itemType: str, itemId: str):
        '''
        Added inventory location:  asfc:8
        Get an instance of ItemMonth 

        Parameters
        ----------
            invLoc : str
                This is the place where inventory is tracked (Texas, Virginia, etc..)
            growMonthId : str
                This the identifier for the GrowMonth, i.e. 2021_04 --> <year>_<month>
            itemType : str
                The is the item type i.e. Vase, Sleeve, etc.
            itemId : str
                this is the id related to the item in the item type, i.e. an ItemType of vase has (Skull, Strawberry, etc..)
            
        '''
        clt = ItemMonth.get_client()
        item = InventoryActiveItems.GetItemById(itemType,itemId)
        invLocPath = InventoryLocation.getInstance().get_collection_name(invLoc)
        if item is None:
            raise Exception("Item of type {}, with id {}, Not Found.".format(itemType,itemId))
        item = item.get_dict()
        gmPath = f'{ItemMonth.COLLECTION_NAME}/{clt.company}/Sales_Inventory/{invLocPath}/GrowMonth/{growMonthId}'
        imPath = ItemMonth.GetPathNmStr(gmPath,itemType,item.get('id','NoIdGiven'),invLoc)
        return cls.getItemMonthInstanceByPath(imPath)
    
    @classmethod
    def getItemMonthInstanceByPath(cls,inPath):
        '''
        Given a path, grab the instance of ItemMonth

        Parameters
        ----------
            inPath : str
                The full path string to grab the firestore document
        '''
        #fsDocument = ItemMonth.get_firestore_client().document(inPath)
        #ref,snap = ItemMonth.getDocuments(fsDocument)
        fsDocument = SalesInvBase.returnFSDoc(ItemMonth.get_firestore_client().document(inPath))
        docDict = fsDocument.snap.to_dict() if fsDocument.snap.exists else {}
        docDict['fs_docSnap'] = fsDocument.snap
        docDict['fs_docRef'] = fsDocument.ref
        docDict['grow_month'] = fsDocument.grow_period
        parts = fsDocument.id.split("__")
        docDict['item_type'] = parts[0]
        docDict['item_id'] = parts[1]
        return ItemMonth(ItemMonth.get_firestore_client(),**docDict)

    @classmethod
    def getInstanceItem(cls,fsDocument: object ,item=None):
        '''
        Grab an Item Month instance with a document that may or may not exist
        
        Parameters
        ----------
            fsDocument : Firestore Document
                The firestore document (could be not created yet)
            growMonthId : str
                This the identifier for the GrowMonth, i.e. 2021_04 --> <year>_<month>
            itemType : str
                The is the item type i.e. Vase, Sleeve, etc.
        '''
        fsDoc = ItemMonth.returnFSDoc(fsDocument)
        docDict = fsDoc.snap.to_dict() if fsDoc.snap.exists else {}
        docDict['fs_docSnap'] = fsDoc.snap
        docDict['fs_docRef'] = fsDoc.ref
        docDict['grow_month'] = fsDoc.grow_period
        parts = fsDoc.id.split("__")
        docDict['item_type'] = parts[0]
        docDict['_item'] = item
        docDict['item_id'] = parts[1]
        return ItemMonth(ItemMonth.get_firestore_client(),**docDict)

    @classmethod
    def getInstance(cls,fsDocument):
        '''
        Given the firestore document, get an instance of ItemMonth

        Parameters
        ----------
            fsDocument : Firestore Document
                The firestore document that represents the ItemMonth
        '''
        fsDoc = ItemMonth.returnFSDoc(fsDocument)
        docDict = fsDoc.snap.to_dict() if fsDoc.snap.exists else {}
        docDict['fs_docSnap'] = fsDoc.snap
        docDict['fs_docRef'] = fsDoc.ref
        docDict['grow_month'] = fsDoc.grow_period
        parts = fsDoc.id.split("__")
        docDict['item_type'] = parts[0]
        docDict['item_id'] = parts[1]
        return ItemMonth(ItemMonth.get_firestore_client(),**docDict)

    @classmethod
    def GetItemMonthDict(cls,invLoc, growPeriod, periodType, itemType, itemId):
        pathInvLoc = InventoryLocation.getInstance().get_collection_name(invLoc)
        basePath = f"application_data/Color_Orchids/Sales_Inventory/{pathInvLoc}/Grow{periodType}/{growPeriod}"
        itemPath = f"{basePath}/Items/{itemType}__{itemId}"
        supplyPath = f"{basePath}/Supply/{itemType}"
        notesPath = f"{basePath}/Notes/{itemType}"
        itemDoc = FSDocument.getInstance(itemPath)
        resp = {'status':{
                    'entry_exists':False,
                    'inventory_set':False,
                    'inventory_set_dt':'',
                    'name':'',
                    'item_id':itemId,
                    'clean_name':'',
                    'inventory_location':invLoc,
                    'grow_month':growPeriod,
                    'item_type': itemType,
                    'notes':[],
                    'supply':[]},
                'stats':{
                    'set_inventory':0,
                    'added_inventory':0,
                    'remaining_inventory':0,
                    'prev_month_inventory':0,
                    'month_reserves':0
                }}
        if itemDoc.exists:
            data = itemDoc.snap.to_dict()
            invSetInd = data.get('inventory_set',0)
            enteredInventory = 0 if data.get('actual',0) is None else data.get('actual',0)
            remainingInventory = data.get('calc_actual',0)
            prevMonthInventory = data.get('prev_actual',0)
            addedInventory = data.get('inventory_add',0)
            monthReserves = data.get('reserve_total',0)
            itemMonthExists = True
            resp = {'status': {'entry_exists': itemMonthExists, 
                            'inventory_set': invSetInd,
                            'inventory_set_dt': '' if not invSetInd else cls.convert_utc_to_timezone_str(data.get('set_upd_dt','')),
                            'name':data.get('name',''),
                            'item_id':itemId,
                            'clean_name':data.get('item_name',''),
                            'inventory_location': invLoc,
                            'grow_month':growPeriod,
                            'item_type':itemType}, 
                    'stats':
                            {'set_inventory': 0 if enteredInventory is None else enteredInventory,
                            'added_inventory': 0 if addedInventory is None else addedInventory,
                            'remaining_inventory': 0 if remainingInventory is None else remainingInventory,
                            'prev_month_inventory': 0 if prevMonthInventory is None else prevMonthInventory,
                            'month_reserves': monthReserves}}
            resp['status']['notes'] = []
            resp['status']['supply'] = []

        supplyDoc = FSDocument.getInstance(supplyPath)
        if supplyDoc.exists:
            try:
                supplyInfo = supplyDoc.getData("supply").get(itemId,[])
                supplyInfo2 = [cls.GetTransformedSupply(x) for x in supplyInfo]
                resp['status']['supply'] = supplyInfo2 #jmespath.search(jpSupPath,supply)
            except KeyError as e:
                pass
        
        notesDoc = FSDocument.getInstance(notesPath)
        if notesDoc.exists:
            try:
                #notes = notesDoc.getData(f"notes.`{itemId}`")
                notes = []
                notesDict = notesDoc.get('notes')
                if notesDict:
                    notes = notesDict.get(itemId,[])
                jpNotePath = "[*].{note_id: id, note: note, author: updated_by, updated: up_timestamp}"
                resp['status']['notes'] = jmespath.search(jpNotePath,notes)
            except KeyError as e:
                pass
        return resp
    
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
    def UpdateTotalInventoryAdd(cls, invLoc,growMonth,itemType, itemId) -> dict:
        itemsPath = cls.GetItemsBasePath(invLoc,growMonth,itemType, itemId)
        itemsFsDoc = cls.returnFSDocByPath(itemsPath)
        supplyFsDoc = cls.returnFSDocByPath(cls.GetSupplyBasePath(invLoc,growMonth,itemType))
        itemSupplyArr = []
        totForecasted = 0
        try:
            itemSupplyArr = supplyFsDoc.getData(f"supply.`{itemId}`")
            totForecasted = jmespath.search("[*].forecast | sum(@)",itemSupplyArr)
        except KeyError as e:
            itemSupplyArr = []
            # no supplies found

        
        if not itemsFsDoc.exists:
            im = ItemMonth.getItemMonthInstanceByPath(itemsPath)
            im.update_ndb()
            itemsFsDoc = cls.returnFSDocByPath(itemsPath)

        update_dict = {f"inventory_add": totForecasted}
        #self.up_timestamp = datetime.now().isoformat()
        update_dict['up_timestamp'] = datetime.now().isoformat()
        #self.updated_by = self.get_client().user_email
        update_dict['updated_by'] = ItemMonth.get_client().user_email
        #self.updated_system = 'Firestore_Backend_2020'
        update_dict['updated_system'] = 'Firestore_Backend_2020'
        itemsFsDoc.setData(update_dict)

        return totForecasted

    @classmethod
    def GetBasePath(cls,invLoc,growMonth,itemType):
        inventory_location = InventoryLocation.getInstance().get_collection_name(invLoc)
        basePath = f'application_data/Color_Orchids/Sales_Inventory/{inventory_location}/GrowMonth/{growMonth}/__SECTION__/{itemType}'
        return basePath

    @classmethod
    def GetItemsBasePath(cls,invLoc,growMonth,itemType, itemId):
        basePath = cls.GetBasePath(invLoc,growMonth,itemType)
        itemPath = basePath.replace("__SECTION__","Items")
        return itemPath + "__" + itemId

    @classmethod
    def GetNotesBasePath(cls,invLoc,growMonth,itemType):
        basePath = cls.GetBasePath(invLoc,growMonth,itemType)
        itemPath = basePath.replace("__SECTION__","Notes")
        return itemPath
    
    @classmethod
    def GetSupplyBasePath(cls,invLoc,growMonth,itemType):
        basePath = cls.GetBasePath(invLoc,growMonth,itemType)
        itemPath = basePath.replace("__SECTION__","Supply")
        return itemPath

    @classmethod
    def CleanItemName(cls,inName):
        '''
        Create a URL safe version of the item Name

        Parameters
        ----------
            inName : str
                The name that you want cleaned
        '''
        return inName.replace("'","").replace('"','').replace(' ','').replace(".","").replace('&',"")

    @property
    def notes(self):
        if self._notes is None:
            notes = self.notes_collection.getNotesByItemId(self.item_id)
            self._notes = notes
        return self._notes
    
    @property
    def notes_collection(self):
        if self._notesCollection is None:
            self._notesCollection = NotesCollection.GetOrCreateItemWeekNotes(self.item_type,self.inventory_location,'Month',self.grow_month)
        return self._notesCollection

    @property
    def supply(self):
        if self._supplies is None:
            supplies = self.supply_collection.getSupplyByItemId(self.item_id)
            self._supplies = supplies
        return self._supplies
    
    @property
    def supply_collection(self):
        if self._supplyCollection is None:
            self._supplyCollection = SupplyCollection.GetOrCreateItemWeekSupply(self.item_type,self.inventory_location,'Month',self.grow_month)
        return self._supplyCollection

    def create_note(self, note : str):
        '''
        Create a Note for this Item

        Parameters
        ----------
            note : str
                The string message that is to be saved as a "note" for this inventory item
        '''
        return self.notes_collection.create_note(self.item_id, note)

    def delete_note(self, note_id):
        '''
        Given a note_id, delete that note associated to the inventory

        Parameters
        ----------
            note_id : str
                the unique identifier for the note that is to be deleted
        '''
        return self.notes_collection.delete_note(note_id)
        
    def create_supply(self,supplier_id, inForecast, confirmation_num='', supplyNote='', itemType=None, itemName=None):
        '''
        Create a supply for this inventory

        Parameters
        ----------
            suplier_id : str
                the id of the supplier that has the inventory supply
            inForecast : int
                The forecasted amount of inventory received from the supplier
            confirmation_num : str
                The confirmation code/number for the order 
        '''
        return self.supply_collection.create_supply(self.item_id,supplier_id,inForecast,confirmation_num,note=supplyNote)

    def get_itemmonth_dict(self):
        '''
        Get a dictionary summary of the item month
        '''
        d = {'name': self.item['name'],
             'grow_month': self._growMonthParent.get_growweek_dict(),
             'actual': self.actual,
             'inventory_set': self.inventory_set,
             'color_groupings': self.color_groupings,
             '_id':self.id}

        return d

    def update_groupings(self, grouping, reset=False):
        """
        Deprecated:  Use 'update_color_grouping'
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


    def update_color_grouping(self, color_grouping, reset=False) -> Boolean:
        """
        The color grouping object should be a dict where the keys are colors and a quantity
        This function will add the json object and then go through and count the numbers and update the actual quantity
        
        Parameters
        ----------
            color_groupings : dict
                expected key value pair... name=qnt, and then added for total quantity
            reset : boolean (default = False)
                If true or there were values in the grouping reset the actual to the total quantity in the grouping
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
        self.update_ndb()
        return True

    def get_schema(self):
        schema = self.get_bq_schema()
        return schema

    def get_values_dict(self):
        return self.get_dict()

    @property
    def next(self):
        return ItemMonth.get_or_create(self.item_type, self.item, self._growMonthParent.next_week)

    @property
    def prior(self):
        return ItemMonth.get_or_create(self.item_type, self.item, self._growMonthParent.prior_week)

    @property
    def forecasts(self):
        fcast = 0
        for supp in self.supply:
            fcast = fcast + supp.get_forecast()
        return fcast

    @property
    def reserves(self):
        """Pulling this information through the _growMonthParent"""
        return self._growMonthParent.getSummary().getItemReserves(self.item_type, self.item_id)

    def get_total_reserved(self):
        '''
        Get all of the reserves for this item month by item in this item type
        '''
        return self._growMonthParent.getSummary().getReserveAmtByItem(self.item_type, self.item_id)

    @classmethod
    def get_or_create(cls,invLoc, itemType, itemInfo, growMonth):
        '''
        Get an instance of ItemMonth

        Parameters
        ----------
            invLoc : str
                The location where the inventory is tracked
            itemType : str
                The type of item we're tracking
            itemInfo : FSObject
                The id, path and name of the Firestore item object
            growMonth : GrowMonth
                The grow month instance that this ItemMonth should span from
        '''
        itemObj = ItemMonth.GetSBObj(itemInfo['path'])
        return growMonth.get_or_create_itemmonth(invLoc, itemType,itemObj)

    @classmethod
    def CleanItemType(cls,item_type):
        '''
        Basically takes the item type and does the following
        - lower cases the name
        - remove the "s" at the end if it exists
        '''
        lower = item_type.lower()
        if (lower.endswith('s')):
            return lower[:-1]
        return lower
    
    @property
    def clean_item_type(self):
        '''
        Make the clean item type name a property value
        '''
        return ItemMonth.CleanItemType(self.item_type)

    def iw_summary(self):
        ps = {}
        ps['_id'] = self.id
        ps['item'] = self.item['name']
        ps['lookup_name'] = self.item_name
        ps['inventory_location'] = self.inventory_location
        ps['item_id'] = self.item['id']
        ps['month_id'] = self.grow_month
        ps['actual'] = self.actual
        ps['inventory_set'] = self.inventory_set
        ps['forecast'] = self.forecasts
        ps['num_reserved'] = self.get_total_reserved()
        return ps

    def availability(self):
        '''
        Given the reserved amount and the inventory, what is the availability
        '''
        rsvs = self.get_total_reserved()
        fcast = self.forecasts
        if self.actual > 0:
            return self.actual - rsvs

        return fcast - rsvs

    def dict_summary(self,includeNotes=False, includeSupply=False):
        '''
        A dictionary summary for this ItemMonth instance
        '''
        invSetInd = self.inventory_set
        enteredInventory = 0 if self.actual is None else self.actual
        remainingInventory = self.calc_actual
        prevMonthInventory = self.prev_actual
        addedInventory = self.inventory_add
        monthReserves = self.reserve_total
        itemMonthExists = self.exists
        retDict = {'status': {'entry_exists': itemMonthExists, 
                           'inventory_set': invSetInd,
                           'inventory_set_dt': '' if not invSetInd else ItemMonth.convert_utc_to_timezone_str(self.set_upd_dt),
                           'name':self.name,
                           'item_id':self.item_id,
                           'clean_name':self.item_name,
                           'inventory_location': self.inventory_location,
                           'grow_month':self.grow_month,
                           'item_id':self.item_id,
                           'item_type':self.item_type}, 
                'stats':
                         {'set_inventory': 0 if enteredInventory is None else enteredInventory,
                          'added_inventory': 0 if addedInventory is None else addedInventory,
                          'remaining_inventory': 0 if remainingInventory is None else remainingInventory,
                          'prev_month_inventory': 0 if prevMonthInventory is None else prevMonthInventory,
                          'month_reserves': monthReserves}}
        if includeNotes:
            retDict['status']['notes'] = self.notes
        if includeSupply:
            retDict['status']['supply'] = self.supply
        return retDict