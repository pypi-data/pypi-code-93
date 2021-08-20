import logging,os

instance_classes = {'loaded':False}

def CallClassMethod2(instanceName,methodName,arguments=None):
    globals()["LoadInstanceClasses"]()  #LoadInstanceClasses()
    
    func = getattr(instance_classes[instanceName],methodName)
    if arguments:
        return func(*arguments.get('parameters',()),**arguments.get('keywords',{}))
    return func()

def CallClassMethod(instanceName,methodName,arguments=None):
    globals()["LoadInstanceClasses"]()  #LoadInstanceClasses()
    
    func = getattr(instance_classes[instanceName],methodName)
    if arguments:
        return func(arguments)
    return func()

def GetInstance(instanceName,firestoreDocument):
    return CallClassMethod(instanceName,'getInstance',firestoreDocument)

def GetBasePath(instanceName):
    return CallClassMethod(instanceName,'basePath')

# Base Application: Item Tracking
from .data_storage_type import DataStorageType, StorageField
from .image import Image
from .storage_blob import StorageBlob
from .api_user import ApiUser
from .data_number import DataNumber,DataNumberLookup
from .reporting_config import ReportingConfig
from .utils import LoggingMessages, FireStoreBase, FSDocument
from .app_configuration import AppConfiguration
from .quick_storage import QuickStorage

# Sales Inventory
from .supplier import Supplier
from .email_notifications import EmailNotifications
from .grow_week import GrowWeek
from .item_week import ItemWeek
from .grow_month import GrowMonth
from .item_month import ItemMonth, ItemMonthReserves, ItemMonthCollection, ItemMonthSummary
from .item_week_notes import ItemWeekNotes, NotesCollection
from .item_week_supply import ItemWeekSupply, SupplyCollection
from .item_month_notes import ItemMonthNotes, MonthNotesCollection
from .item_month_supply import ItemMonthSupply, MonthSupplyCollection
from .item_reserve import ItemReserve
from .inventory_active_items import InventoryActiveItems, InventoryTracking, InventoryLocation

def LoadInstanceClasses():
    global instance_classes
    if not instance_classes['loaded']:
        instance_classes = {'loaded':True,'DataStorageType':DataStorageType,'Image':Image,'StorageBlob':StorageBlob,
                            'ApiUser':ApiUser,'DataNumber':DataNumber,'DataNumberLookup':DataNumberLookup,'ReportingConfig':ReportingConfig,
                            'LoggingMessages':LoggingMessages,'AppConfiguration':AppConfiguration,'ItemWeek':ItemWeek,'GrowWeek':GrowWeek,
                            'Supplier':Supplier,'EmailNotifications':EmailNotifications,'ItemWeekNotes':ItemWeekNotes,'ItemWeekSupply':ItemWeekSupply,
                            'NotesCollection':NotesCollection,'SupplyCollection':SupplyCollection,'GrowMonth':GrowMonth,
                            'ItemMonth':ItemMonth,'ItemMonthNotes':ItemMonthNotes,'ItemMonthSupply':ItemMonthSupply, "ItemMonthSummary":ItemMonthSummary,
                            'MonthNotesCollection':MonthNotesCollection,'MonthSupplyCollection':MonthSupplyCollection}


def LoadInstance_DNL(dnl, clzzName):
    return DataNumberLookup.get_obj_by_dnl(dnl,instance_classes.get(clzzName,None))

# Restful code
from .rest import SalesInventoryAPI

