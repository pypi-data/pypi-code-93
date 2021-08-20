from .sales_inv_utils import SalesInvBase
from datetime import datetime
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import jmespath

from .item_month import ItemMonthCollection, ItemMonth
from .item_reserve import ItemReserve
from .reserve_summary import ReserveSummary
from .inventory_active_items import InventoryActiveItems, InventoryItems, InventoryLocation

'''
This will be the new converted class GrowMonth
'''
class GrowMonth(SalesInvBase):

    ext_fields = ['month_number','year','grow_weeks','start_week','end_week','item_month','parent_path','path']
    COLLECTION_NAME = 'application_data'
    
    def __init__(self, fsClient, **kwargs):
        self._month_number = kwargs.get('month_number',None) 
        self._year = kwargs.get('year',None) 
        self.item_month = kwargs.get('item_month',[])
        self._grow_weeks = kwargs.get('grow_weeks',[])
        self._start_week = kwargs.get('start_week',None)
        self._end_week = kwargs.get('end_week',None)

        self._itemmonth = {}

        super(GrowMonth, self).__init__(fsClient, **kwargs)
    
    def base_path(self):
        return GrowMonth.__basePath(self._fsClient)

    @classmethod
    def basePath(cls):
        return GrowMonth.__basePath(GrowMonth.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return GrowMonth.COLLECTION_NAME+'/'+inClient.company+'/Sales_Inventory/Converted/GrowMonth'

    @classmethod
    def getInstance(cls,fsDocument):
        ref,snap = GrowMonth.getDocuments(fsDocument)
        docDict = snap.to_dict() if snap.exists else {}
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        return GrowMonth(GrowMonth.get_firestore_client(),**docDict)

    @property
    def year(self):
        if self._year is None or self._year == '':
            self._year = int(self.id.split("_")[0])
        return self._year

    @property
    def month_number(self):
        if self._month_number is None or self._month_number == '':
            self._month_number = int(self.id.split("_")[1])
        return self._month_number
    
    @property
    def grow_weeks(self):
        if len(self._grow_weeks) == 0:
            week = self._get_start_date()
            while week.month == self.month_number:
                wkNum = week.isocalendar()[1]
                year = week.isocalendar()[0]
                self._grow_weeks.append(str(year)+"_"+str(wkNum).zfill(2))
                week = week + timedelta(days=7)
        return self._grow_weeks
    
    @property
    def start_week(self):
        if self._start_week is None or self._start_week == '':
            self._start_week = self.grow_weeks[0]
        return self._start_week
    
    @property
    def end_week(self):
        if self._end_week is None or self._end_week == '':
            self._end_week = self.grow_weeks[-1]
        return self._end_week

    def _get_start_date(self):
        weekday, _ = monthrange(self.year,self.month_number)
        day1Month = date(self.year,self.month_number,1)
        while weekday > 0:
            weekday = weekday + 1
            if weekday == 7:
                weekday = 0
            day1Month = day1Month + timedelta(days=1)
        return day1Month

    def get_itemmonth_type(self,invLoc, item_type):
        imKey = f"{invLoc}__{item_type}"
        im = self._itemmonth.get(imKey,None)
        if im is None:
            basePath = InventoryLocation.getInstance().getGrowMonthPath(self.path,invLoc)
            item_path = f'{basePath}/Items/{item_type.replace(" ","_")}'
            iw = ItemMonthCollection.getInstance(self._fsClient.document(item_path),self)
            if not im.exists:
                im.item_type = item_type
                im.grow_month = self.id
                im._inventory_location = invLoc
                im._in_growMonthParent = self
                im.update_ndb(True)
                self._itemmonth[imKey] = im
        return im
    
    @classmethod
    def getGrowMonthInstance(cls, month_id):
        path = GrowMonth.basePath()+'/'+month_id
        gm = GrowMonth.getInstance(GrowMonth.get_firestore_client().document(path))
        if not gm.exists:
            gm.update_ndb()
        return gm

    @classmethod
    def getGrowMonthNow(cls):
        dt = datetime.now()
        return cls.getGrowMonthInstance(f"{dt.year}_{str(dt.month).zfill(2)}")

    @property
    def next(self):
        dt = datetime.strptime(self.id,"%Y_%m")
        dt = dt+relativedelta(months=1)
        return GrowMonth.getGrowMonthInstance(dt.strftime("%Y_%m"))

    @property
    def prev(self):
        dt = datetime.strptime(self.id,"%Y_%m")
        dt = dt+relativedelta(months=-1)
        return GrowMonth.getGrowMonthInstance(dt.strftime("%Y_%m"))

    @classmethod
    def getGrowMonthByWeek(cls, week_id):
        path = GrowMonth.basePath()
        coll = GrowMonth.get_firestore_client().collection(path)
        q = coll.where('grow_weeks','array_contains',week_id)
        gms = []
        for docSnap in q.stream():
            gms.append(docSnap)
        
        if len(gms) > 0 and gms[0].exists:
            return GrowMonth.getInstance(gms[0])
        
        return None

    @classmethod
    def get_active(cls):
        return GrowMonth.get_active_any(GrowMonth.get_firestore_client(), GrowMonth.basePath, GrowMonth)

    def get_growmonth_dict(self):
        d = {'month_number': self.month_number,
             'year': self.year,
             '_id':self.id}
        return d

    def _getItemMonthCollection(self, invLoc : str, item_type : str) -> ItemMonthCollection:
        itemMonthCollection = self._itemmonth.get(item_type,None)
        if itemMonthCollection is None:
            itemMonthCollection = ItemMonthCollection.getOrCreateInstance(invLoc, item_type,self)
            self._itemmonth[item_type] = itemMonthCollection
        return itemMonthCollection
    
    def get_or_create_itemmonth(self,invLoc, item_type,itemObj):
        itemMonthCollection = self._getItemMonthCollection(invLoc, item_type)
        return itemMonthCollection.create_itemmonth_entry(itemObj,self)