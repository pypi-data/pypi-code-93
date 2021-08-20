from .. reserve_summary import ReserveSummary
from typing import Any
from .. import GrowWeek
from .. import GrowMonth
from .. import ItemMonth
from .. import ItemMonthReserves
from .. import ItemMonthSummary
from .. import ItemReserve
from .. import ItemMonthCollection
from .. import DataNumberLookup
from .. import InventoryActiveItems
from .. import InventoryTracking
from .. import QuickStorage

import jmespath, datetime, logging

class SalesInventoryAPI(object):
    '''
    This organizes all the functions to use for REST API calls

    Methods
    -------
        __init__(self,logger):
            Constructor, a logger needs to be passed for this constructor
        createReserveAPI(reserveDate, customer_id, location_id, product_id, reserved, invLoc)
            Create the reserve
    '''

    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger('SalesInventoryAPI')
        self.logger = logger

    def createReserveAPI(self, reserveDate, customer_id : str, location_id : str, product_id : str, reserved : int, invLoc=None) -> list:
        '''
        create a reserve

        Parameters
        ----------
            reserveDate : date
                The date for this reserve
            customer_id : str
                The string key to lookup the customer
            location_id : str
                The string key to lookup the location
            product_id : str
                The string key to lookup the product
            reserved : int
                The number of reservations
            invLoc : str
                The inventory location for the reserve, if not provided defaults to location inventory location
        '''
        gw = GrowWeek.GetGrowWeekByDate(reserveDate)
        docRef = gw.get_reserve_reference()
        ir = ItemReserve.create_reserve(docRef,customer_id,location_id,product_id,reserved,gw.id,reserveDate, invLoc)
        summ = ReserveSummary.getReserveSummary(gw.id)
        return summ.add_reserve(ir)

    def updateReserveAPI(self, reserve_id : str, customer_id : str, location_id : str, product_id : str, reserved : int, reserveDate : datetime, invLoc=None) -> list:
        '''
        Update the reserve given the reserve id

        Parameters
        ----------
            reserve_id : str
                The string key to this reserve
            customer_id : str
                The string key to lookup the customer
            location_id : str
                The string key to lookup the location
            product_id : str
                The string key to lookup the product
            reserved : int
                The number of reservations
            reserveDate : date
                The date for this reserve
            invLoc : str
                The inventory location for the reserve, if not provided defaults to location inventory location
            
        '''
        gw = GrowWeek.GetGrowWeekByDate(reserveDate)
        ir = ItemReserve.getItemReserveInstance(reserve_id)
        ir = ir.update_reserve(customer_id, location_id, product_id, reserved, gw, reserveDate, invLoc)
        summ = ReserveSummary.getReserveSummary(gw.id)
        return summ.update_reserve(ir)

    def deleteReserveAPI(self, reserve_id : str) -> dict:
        '''
        Delete the reserve given the reserve id

        Parameters
        ----------
            reserve_id : str
                The string key that is unique identifier for a reserve
        '''
        ir = ItemReserve.getItemReserveInstance(reserve_id)
        if ir is not None and ir.exists:
            gw = GrowWeek.getGrowWeekInstance(ir.grow_period)
            summ = ReserveSummary.getReserveSummary(gw.id)
            summ.delete_reserve(ir)
            ItemReserve.hardDelete(ir.id)
            return {"status": "success"}
        else:
            path = DataNumberLookup.get_path_for_dnl(reserve_id)
            docRef = ir._fsClient.document(path)
            gw_id = docRef.parent.parent.id
            gw = GrowWeek.getGrowWeekInstance(gw_id)
            summ = ReserveSummary.getReserveSummary(gw.id)
            summ._delete_reserve(reserve_id)
            return {"status": "success"}

    def getAllReservesAPI(self, reserveDate : datetime) -> list:
        '''
        Get all of the reserves given a reserve date

        Parameters
        ----------
            reserveDate : date
                The date to use to look up the reserves
        '''
        gw = GrowWeek.GetGrowWeekByDate(reserveDate)
        irList = gw.reserves
        return [resv.get_dict() for resv in irList]

    def getSummReservesAPI(self, reserveDate : datetime) -> list:
        '''
        Get a summary of reserves for this reserve date.. get the week number for this date

        Parameters
        ----------
            reserveDate : date
                The date to use to look up the reserves
        '''
        gw = GrowWeek.GetGrowWeekByDate(reserveDate)
        irList = gw.getSummary().summary
        return irList

    def getReserveAPI(self, reserve_id : str) -> dict:
        '''
        Get the summary of the reserve given it's id

        Parameters
        ----------
            reserve_id : str
                The string key to this reserve
        '''
        ir = ItemReserve.getItemReserveInstance(reserve_id)
        return ir.get_dict()

    def process_productionview_item_update(self, item_id : str, status : str) -> dict:
        '''
        Process an update from the production view, which is just updating the inventory tracking status

        Parameters
        ----------
            item_id : str
                The unique id of the item that you want to update
            status : str
                True you want to track this item, False, you do not (pass either 'true' or 'false')
        '''
        resp = {'status':'success','value':status,'outcome':{}}
        if status and status == 'true':
            # means we're adding it
            resp['outcome'] = InventoryActiveItems.add_item_by_id(item_id)
        else:
            resp['outcome'] = InventoryActiveItems.remove_item(item_id)
        
        return resp

    def process_productionview_item_order(self, item_id : str, order : int) -> dict:
        '''
        Update the order to which an item displays on the production view

        Parameters
        ----------
            item_id : str
                The unique id of the item that you want to update
            order : int
                The order to display, lower numbers are displayed first
        '''
        resp = {'status':'success','value':order, 'outcome':{}}
        orderNumber = float(order)
        resp['outcome'] =InventoryActiveItems.add_item_order(item_id,orderNumber)
        return resp
    

    def getMonthlyItemTypes(self,force=False) -> list:
        '''
        Get a list of items that will be tracked for inventory monthly


        '''
        mi = QuickStorage.getValue('MonthlyInventoryItems')
        if mi is None or force:
            monthItems = InventoryTracking.getInstance().monthly_items
            dictCreate = []
            dictCreate.append({'key_name':'image'})
            mi = []
            for monthItem in monthItems:
                entry = {'item_type':monthItem, 'items_url':f'/rest/api/v1/recipe_items/{monthItem}','image':None}
                items = InventoryActiveItems.get_active_recipe_items(monthItem,fldKey='data_number_lookup')
                items = {k:v.get_custom_dict(dictCreate) for k,v in items.items()}
                #images = jmespath.search("items.[*][] | [*].image[] | [*].image_url",items)
                images = jmespath.search("*.image[] | [*].image_url",items)
                if len(images) > 0:
                    entry['image'] = images[0]
                else:
                    entry['image'] = '/static/img/missing_image.png'
                    
                mi.append(entry)
            QuickStorage.setValue('MonthlyInventoryItems',mi,10080)
        return mi
    
    def get_active_items(self, itemType : str) -> list:
        '''
        Given the item type, what are the active items

        Parameters
        ----------
            itemType : str
                The type of item for which you want an active list
        '''
        return InventoryActiveItems.display_recipe_items(itemType,tracked_only=True)

    def _getItemMonth(self, invLoc : str, gmId : str, itT : str, itI : str) -> ItemMonth:
        '''
        Get an Item Month

        Parameters
        ----------
            invLoc : str
                The inventory location for the reserve, if not provided defaults to location inventory location
            gmId : str
                The grow month id for the item month
            itT : str
                The item type for which we want an ItemMonth instance
            itI : str
                The item id for the ItemMonth instance to load
        '''
        #cleanName = ItemMonth.CleanItemName(itN)
        return ItemMonth.getItemMonthInstance(invLoc, gmId, itT, itI)

    def getItemMonthAPI(self,invLoc : str, growMonthId : str, itemType : str, itemId : str) -> dict:
        '''
        This returns the summary for the Item Month

        Parameters
        ----------
            invLoc : str
                The inventory location for the reserve, if not provided defaults to location inventory location
            growMonthId : str
                The grow month id for the item month
            itemType : str
                The item type for which we want an ItemMonth instance
            itemId : str
                The item id for the ItemMonth instance to load
        '''
        #im = self._getItemMonth(invLoc, growMonthId, itemType, itemId)
        #return self._getItemMonthAPI(im)
        return ItemMonth.GetItemMonthDict(invLoc,growMonthId,'Month',itemType,itemId)

    def _getGrowMonthAPI(self, month_id : str) -> GrowMonth:
        '''
        Given a month_id, grap a GrowMonth Instance

        Parameters
        ----------
            month_id : str
                The string key for an instance of GrowMonth
        '''
        return GrowMonth.getGrowMonthInstance(month_id)

    def _getItemMonthAPI(self, itemMonth : ItemMonth) -> dict:
        '''
        Get the dictionary that explains an itemMonth

        Parameters
        ----------
            itemMonth : ItemMonth
                An instance of ItemMonth
        '''
        restSummary = itemMonth.dict_summary(includeSupply=True,includeNotes=True)
        return restSummary
    
    def refreshItemMonthInventory(self,invLoc : str, growMonthId : str, itemType : str, itemId : str) -> dict:
        '''
        Refresh the inventory level for a given an Item Month

        Parameters
        ----------
            invLoc : str
                The inventory location for the reserve, if not provided defaults to location inventory location
            growMonthId : str
                The grow month id for the item month
            itemType : str
                The item type for which we want an ItemMonth instance
            itemId : str
                The item id for the ItemMonth instance to load
        '''
        im = self._getItemMonth(invLoc, growMonthId, itemType, itemId)
        return self._refreshItemMonthInventory(im)
    
    def _refreshItemMonthInventory(self,itemMonth : ItemMonth) -> dict:
        '''
        Refresh the inventory level for a given an Item Month (internal)

        Parameters
        ----------
            itemMonth : ItemMonth
                An instance of ItemMonth
        '''
        itemMonth._refreshInventoryLevels()
        ItemMonthSummary.UpdateItemMonthSummary(itemMonth)
        return self._getItemMonthAPI(itemMonth)

    def setItemMonthInventory(self,invLoc : str, growMonthId : str, itemType : str, itemId : str, inventoryAmount : int) -> dict:
        '''
        Set the inventory amount for an instance of ItemMonth

        Parameters
        ----------
            invLoc : str
                The inventory location for the reserve, if not provided defaults to location inventory location
            growMonthId : str
                The grow month id for the item month
            itemType : str
                The item type for which we want an ItemMonth instance
            itemId : str
                The item id for the ItemMonth instance to load
            inventoryAmount : int
                The level for which to set the inventory for this ItemMonth
        '''
        im = self._getItemMonth(invLoc, growMonthId, itemType, itemId)
        im.set_actual(inventoryAmount)
        ItemMonthSummary.UpdateItemMonthSummary(im)
        return self._getItemMonthAPI(im)

    def addItemMonthInventory(self, invLoc : str, growMonthId : str, itemType : str, itemId : str, addedInventory : int) -> dict:
        '''
        Add to amount of inventory for this ItemMonth

        Parameters
        ----------
            invLoc : str
                The inventory location for the reserve, if not provided defaults to location inventory location
            growMonthId : str
                The grow month id for the item month
            itemType : str
                The item type for which we want an ItemMonth instance
            itemId : str
                The item id for the ItemMonth instance to load
            addedInventory : int
                The amount of inventory to add for this ItemMonth
        '''
        im = self._getItemMonth(invLoc, growMonthId, itemType, itemId)
        im.add_inventory(addedInventory)
        ItemMonthSummary.UpdateItemMonthSummary(im)
        return self._getItemMonthAPI(im)

    def unsetItemMonthInventory(self, invLoc : str, growMonthId : str, itemType : str, itemId : str) -> dict:
        '''
        Un Set the inventory amount for an instance of ItemMonth or remove the set inventory level

        Parameters
        ----------
            invLoc : str
                The inventory location for the reserve, if not provided defaults to location inventory location
            growMonthId : str
                The grow month id for the item month
            itemType : str
                The item type for which we want an ItemMonth instance
            itemId : str
                The item id for the ItemMonth instance to load
        '''
        im = self._getItemMonth(invLoc, growMonthId, itemType, itemId)
        im.unset_actual()
        ItemMonthSummary.UpdateItemMonthSummary(im)
        return self._getItemMonthAPI(im)

    def createItemMonthEntryAPI(self, invLoc : str, growMonthId : str, itemType : str, itemId : str) -> bool:
        '''
        create an ItemMonth entry in the database

        Parameters
        ----------
            invLoc : str
                The inventory location for the reserve, if not provided defaults to location inventory location
            growMonthId : str
                The grow month id for the item month
            itemType : str
                The item type for which we want an ItemMonth instance
            itemId : str
                The item id for the ItemMonth instance to load
        '''
        im = self._getItemMonth(invLoc, growMonthId, itemType, itemId)
        if not im.exists:
            im._refreshInventoryLevels()
        return True
    
    def getProductionViewData(self, invLoc : str, itemType : str, startDate : str) -> dict:
        '''
        Get the product view data to display for this itemType

        Parameters
        ----------
            invLoc : str
                The inventory location for the production view data
            itemType : str
                The item type for which we want the production view data
            startDate : date
                The date in which we'll gather the production view data (format: '%Y-%m-%d')
        '''
        center_date = datetime.datetime.strptime(startDate, '%Y-%m-%d')
        return GrowWeek.get_9_itemweek(invLoc, itemType,center_date)

    def getReservesByName(self, invLoc : str, growMonthId : str, itemType : str, itemId : str) -> list:
        '''
        Given information, get the reserves, so that they can be viewed

        Parameters
        ----------
            invLoc : str
                The inventory location for the reserve, if not provided defaults to location inventory location
            growMonthId : str
                The grow month id for the item month
            itemType : str
                The item type for which we want an ItemMonth instance
            itemId : str
                The item id for the ItemMonth instance to load
        '''
        gm = self._getGrowMonthAPI(growMonthId)
        imr = ItemMonthReserves.getOrCreateMonthReserve(gm,itemType,invLoc,True)
        reserves = imr.week_summaries
        return reserves.get(itemId,[])
    
    def _updateArray(self, arrItem : dict, itemType : str) -> dict:
        '''
        Internal function to update an array to display the Item View screen correctly

        Parameters
        ----------
            arrItem : array of Items
                The item array that we need to update
            itemType : str
                The item type for which the array will be updated to
        '''
        arrItem['item_type'] = itemType
        itemName = [x[:-4] for x in list(arrItem.keys()) if x.endswith("_qty")][0]
        arrItem['qty'] = arrItem[itemName+"_qty"]
        arrItem['item_name'] = itemName
        return arrItem

    def getReservesAll(self,growMonthId : str,itemType : str,invLoc : str) -> list:
        '''
        Get all of the reserves for a given month for an itemType

        Parameters
        ----------
            growMonthId : str
                The grow month id for the item month
            itemType : str
                The item type for which we want an ItemMonth instance
            invLoc : str
                The inventory location for the reserve, if not provided defaults to location inventory location
            
        '''
        gm = self._getGrowMonthAPI(growMonthId)
        imr = ItemMonthReserves.getOrCreateMonthReserve(gm,itemType,invLoc,True)
        reserves = imr.week_summaries
        rArray = jmespath.search("*[]",reserves)
        return rArray #[self._updateArray(x,itemType) for x in rArray]

    def _monthSummaryDict(self, itemMonthReserves : ItemMonthReserves) -> dict:
        '''
        Return a summary dictionary for the reserves in a given month

        Parameters
        ----------
            itemMonthReserves : ItemMonthReserves
                An instance of ItemMonthReserves
        '''
        return {'details':itemMonthReserves.week_summaries,'summary':itemMonthReserves.month_summary}

    def refreshMonthReservesByWeek(self, growWeekId : str, itemType : str, invLoc : str) -> dict:
        '''
        Given a week that was updated, update the reserve summary at the month level

        Parameters
        ----------
            growWeekId : str
                The string representation of a grow week entry (format: <year>_<week number>)
            itemType : str
                The item type for which we want to refresh
            invLoc : str
                The inventory location we'll be refreshing
        '''
        gm = GrowMonth.getGrowMonthByWeek(growWeekId)
        return self._doRefreshMonthReserves(gm,itemType,invLoc)

    def refreshNext_12_ItemMonths(self,startMonthId : str, invLoc : str, itemType : str) -> list:
        '''
        Refresh the next 12 months for this inventory location, and itemType starting at the given month

        Parameters
        ----------
            startMonthId : str
                The id of the start month for the refresh
            invLoc : str
                The inventory location for which we want to refresh
            itemType : str
                The inventory item type that needs refreshed
        '''
        gm = self._getGrowMonthAPI(startMonthId)
        results = []
        for _ in range(12):
            print('Refreshing... '+str(gm.id))
            results.append(self._refreshItemMonthReserves(invLoc, gm,itemType))
            gm = gm.next
        return jmespath.search("[*][]",results)

    def refreshItemMonthReservesByWeek(self,invLoc : str, growWeekId : str, itemType : str) -> list:
        '''
        Refresh this inventory location, and itemType given a certain week

        Parameters
        ----------
            invLoc : str
                The inventory location for which we want to refresh
            growWeekId : str
                The id of the week to find the month for the refresh
            itemType : str
                The inventory item type that needs refreshed
        '''
        gm = GrowMonth.getGrowMonthByWeek(growWeekId)
        return self._refreshItemMonthReserves(invLoc, gm,itemType)

    def refreshItemMonthReservesByMonth(self,invLoc : str, growMonthId : str, itemType : str) -> list:
        '''
        Refresh this inventory location, and itemType given a certain week

        Parameters
        ----------
            invLoc : str
                The inventory location for which we want to refresh
            growMonthId : str
                The id of the month for the refresh
            itemType : str
                The inventory item type that needs refreshed
        '''
        gm = self._getGrowMonthAPI(growMonthId)
        return self._refreshItemMonthReserves(invLoc, gm,itemType)
    
    def _refreshItemMonthReserves(self,invLoc : str, growMonth : GrowMonth, itemType : str) -> list:
        '''
        <private>
        Internal Method to call and get a refresh of ItemMonthReserves (should this refresh 1 location or both??)

        Parameters
        ----------
            invLoc : str
                The string location of where the inventory is tracked
            growMonth : GrowMonth
                An Instance of GrowMonth
            itemType : str
                The type/category of the item we are tracking

        '''
        imc = ItemMonthCollection.getOrCreateInstance(invLoc, itemType,growMonth)
        ims = imc.refresh_loaded_items()
        resp = []
        for im in ims:
            ItemMonthSummary.UpdateItemMonthSummary(im)
            resp.append(self._getItemMonthAPI(im))
        return resp

    def _doRefreshMonthReserves(self, growMonth : GrowMonth, itemType : str, invLoc : str) -> dict:
        '''
        Internal function to refresh some month reserves

        Parameters
        ----------
            growMonth : GrowMonth
                An instance of GrowMonth
            itemType : str
                The item type for which we want to refresh
            invLoc : str
                The inventory location we need to refresh
        '''
        imr = ItemMonthReserves.getOrCreateMonthReserve(growMonth,itemType,invLoc,True)
        imr.load_reserves()
        return self._monthSummaryDict(imr)
    
    def doRefreshMonthReserves(self, growMonthId : str, itemType : str, invLoc : str) -> dict:
        '''
        Internal function to refresh some month reserves

        Parameters
        ----------
            growMonth : str
                A string representation of a key to look up a grow month
            itemType : str
                The item type for which we want to refresh
            invLoc : str
                The inventory location we need to refresh
        '''
        gm = self._getGrowMonthAPI(growMonthId)
        return self._doRefreshMonthReserves(gm,itemType, invLoc)
        
    def getMonthReserveSummary(self, growMonthId : str, itemType : str, invLoc : str) -> dict:
        '''
        Get the Month Reserve Summary for a given Month_ID

        Parameters
        ----------
            growMonthId : str
                A string representation of a key to look up a grow month
            itemType : str
                The item type for which we want to fetch
            invLoc : str
                The inventory location we need to fetch
        '''
        gm = self._getGrowMonthAPI(growMonthId)
        imr = ItemMonthReserves.getOrCreateMonthReserve(gm,itemType,invLoc,True)
        return self._monthSummaryDict(imr)

    def _getGrowMonthRange(self,startGrowMonth : str, numMonths : int) -> list:
        '''
        Get a list of grow months starting from a specific grow month and extending numMonths

        Parameters
        ----------
            startGrowMonth : str
                the grow month id to start from
            numMonths : int
                The number of months to create a list from the start month
        '''
        year, month = startGrowMonth.split("_")
        retList = [startGrowMonth]
        for _ in range(numMonths-1):
            month = int(month) + 1
            if month == 13:
                year = int(year)+1
                month = 1
            retList.append(str(year)+"_"+str(month).zfill(2))
        return retList

    def getItemMonthSummary(self, invLoc : str,itemType : str, startGrowMonth : str, numMonths=6) -> dict:
        '''
        Using the Item Month Summary, which summarizes things by year, get a list of summaries for display

        Parameters
        ----------
            invLoc : str
                The location of the inventory
            itemType : str
                The item type for which we want a summary
            startGrowMonth : str
                The grow month to start the summary
            numMonths : int
                The number of months for which we want a summary
        '''
        growMonths = self._getGrowMonthRange(startGrowMonth,numMonths)
        growMonths.sort()
        years = list(set([x.split("_")[0] for x in growMonths]))
        summs = []
        jPath = "[?status.grow_month == '"+growMonths[0]+"' && status.inventory_location == '"+invLoc+"'] | [*].{name: status.name, clean_name: status.clean_name, item_id: status.item_id}"
        for year in years:
            startMonth = min([x for x in growMonths if x.split("_")[0] == year]).split("_")[1]
            endMonth = max([x for x in growMonths if x.split("_")[0] == year]).split("_")[1]
            ims = ItemMonthSummary.getInstanceByYearType(year,itemType)
            summs.append(ims.summary_info(startMonth,endMonth))
        summary = [item for sublist in summs for item in sublist]
        items = jmespath.search(jPath,summary)
        items = sorted(items, key = lambda i: i['name']) 
        return {'months': growMonths, 'items': items, 'summary': summary}
