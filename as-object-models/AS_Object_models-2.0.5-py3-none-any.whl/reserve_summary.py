from . inventory_active_items import InventoryLocation, InventoryTracking
from . import FSDocument
from .sales_inv_utils import SalesInvBase
from datetime import datetime
import jmespath,logging

from . import GetInstance
from .item_week import ItemWeek
from .item_reserve import ItemReserve

class ReserveSummary(SalesInvBase):
    """ The summary of reserves for this grow week"""

    ext_fields = ['summary','id','grow_week','parent_path','path']
    COLLECTION_NAME = 'application_data'
    
    def __init__(self,fsClient, **kwargs):
        super(ReserveSummary,self).__init__(fsClient,**kwargs)
        self.summary = kwargs.get('summary',[])
        self._item_reserves_tot = {}  # {"Plants":{"Belita":5,"Bonita":8},"Vase":{"CoolX":3}}
        self._item_reserves = {}  # {"Plants":{"Belita":5,"Bonita":8},"Vase":{"CoolX":3}}
        base = "[*].{id: id, reserve_date: reserve_date, finish_week: finish_week, customer: customer.name, customer_id: customer.id, location: location.name, location_id: location.id, inventory_location: inventory_location, num_reserved: num_reserved, type: item.type item_name: item.name, item_id: item.id "
        self.inventory_tracking = InventoryTracking.getInstance()
        self.update_jpath = base+","+self.inventory_tracking.jPath_Suffix+"}"
        

    def base_path(self):
        return self.grow_path+'/ReservesSummary/'

    @classmethod
    def getInstance(cls,fsDocument):
        ref,snap = ReserveSummary.getDocuments(fsDocument)
        docDict = snap.to_dict() if snap.exists else {}
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        return ReserveSummary(ReserveSummary.get_firestore_client(),**docDict)
    
    @classmethod
    def getReserveSummary(cls,growWeekId):
        clt = ReserveSummary.get_client()
        path = f'{ReserveSummary.COLLECTION_NAME}/{clt.company}/Sales_Inventory/Converted/GrowWeek/{growWeekId}/ReservesSummary/summary'
        docRef = clt.fsClient.document(path)
        return ReserveSummary.getInstance(docRef)
    
    def update_reserve(self,item_reserve):
        return self._update_reserve(item_reserve)
    
    def _update_reserve(self,item_reserve):
        updated_entry = self._apply_summary(item_reserve)
        old_entry = jmespath.search("[?id == '"+item_reserve.id+"'] | [0]",self.summary)
        if old_entry:
            old_entry.update(updated_entry)
            self.update_ndb()
            self.update_item_type_summary(item_reserve)
            return updated_entry
        return self._add_reserve(item_reserve)
    
    def delete_reserve(self,item_reserve):
        return self._delete_reserve(item_reserve.id)
    
    def _delete_reserve(self,reserveId):
        newSumm = [x for x in self.summary if x.get('id','') != reserveId]
        self.summary = newSumm
        self.update_ndb()
        self.delete_item_type_summary(reserveId)
        return reserveId
    
    def add_reserve(self,item_reserve):
        return self._update_reserve(item_reserve)
    
    def _add_reserve(self,item_reserve):
        added_entry = self._apply_summary(item_reserve)
        self.summary.append(added_entry)
        self.update_ndb()
        self.add_item_type_summary(item_reserve)
        return added_entry

    def _get_reserves(self):
        col = self.get_firestore_client().collection(self.reference.parent.parent.path+"/Reserves")
        docs = col.list_documents()
        return docs
    
    def _refresh_reserve_summary(self,reserve_id):
        _ir = ReserveSummary.GetByDNL(reserve_id,ItemReserve)
        return self._apply_summary(_ir)

    def _refresh_all_reserves(self):
        docs = self._get_reserves()
        docArr = []
        for doc in docs:
            d = doc.get().to_dict()
            self._refresh_all_reserves_inner(docArr,d,doc)

        #docArr = [x.get().to_dict() for x in docs]
        self.summary = jmespath.search(self.update_jpath,docArr)
        self.update_ndb()
        return self.summary
        
    def _refresh_all_reserves_inner(self,holdArr, docDict,docRef):
        docDict['id'] = docRef.id
        holdArr.append(docDict)

    def _get_item_type_summary(self):
        docs = self._get_reserves()
        reserves = []
        for doc in docs:
            d = doc.get().to_dict()
            self._get_item_type_summary_inner(reserves,d,doc)
        
        self._save_item_type_summaries(reserves)
    
    def _save_item_type_summaries(self,reserves,base_path=None):
        if base_path is None:
            base_path = self.reference.parent.parent.path
        for itemType in self.inventory_tracking.tracked_items:
            itemTypeArr = jmespath.search("[]",[self._process_reserve(x,itemType) for x in reserves])
            self.save_itemTypeSummary(itemType,itemTypeArr)
    
    def save_itemTypeSummary(self,item_type, newSummary):
        doc = self.get_firestore_client().document(self.reference.parent.parent.path+"/ReservesSummary/"+item_type.replace(" ","_"))
        doc.set({'summary':newSummary})

    def update_item_type_summary(self, itemReserve):
        resEntry = self.create_reserve_entry_ir(itemReserve)
        for itemType in self.inventory_tracking.tracked_items:
            summary = self.get_itemTypeSummary(itemType)
            base_summary = jmespath.search(f"[?reserve_id !='{itemReserve.id}']",summary)
            new_entries = self._process_reserve(resEntry,itemType)
            for entry in new_entries:
                base_summary.append(entry)
            self.save_itemTypeSummary(itemType,base_summary)
    
    def add_item_type_summary(self, itemReserve):
        self.update_item_type_summary(itemReserve)
    
    def delete_item_type_summary(self, reserve_id):
        for itemType in self.inventory_tracking.tracked_items:
            summary = self.get_itemTypeSummary(itemType)
            base_summary = jmespath.search(f"[?reserve_id !='{reserve_id}']",summary)
            self.save_itemTypeSummary(itemType,base_summary)

    
    def _get_item_type_summary_inner(self,holdArr, docDict, docRef):
        entry = self.create_reserve_entry(docDict,docRef)
        holdArr.append(entry)

    def create_reserve_entry(self,reserveDict, reserveRef):
        entry = {'reserve_id': reserveRef.id}
        entry['recipes'] = reserveDict.get('recipe_items',[])
        entry['num_reserved'] = reserveDict['num_reserved']
        entry['inventory_location'] = reserveDict.get('inventory_location',InventoryLocation.getInstance().default_location)
        return entry

    def create_reserve_entry_ir(self,itemReserve):
        return self.create_reserve_entry(itemReserve.get_dict(),itemReserve.reference)
        
    def _process_reserve(self,itemReserve,itemType):
        itemArr = jmespath.search(f"[recipes[?item_type == '{itemType}'][]] | []",itemReserve)
        for i in itemArr:
            i['reserve_id'] = itemReserve['reserve_id']
            i['num_reserved'] = self._toNum(itemReserve.get('num_reserved',0),defaultNum=0)
            i['inventory_location'] = itemReserve['inventory_location']
            qty = self._toNum(i.get('qty',0),defaultNum=0)
            i['total_reserved'] = qty * i['num_reserved']
        return itemArr
    

    def refresh(self):
        docs = self._get_reserves()
        summ_arr = []
        reserve_arr = []
        for doc in docs:
            d = doc.get().to_dict()
            self._get_item_type_summary_inner(reserve_arr,d,doc)
            self._refresh_all_reserves_inner(summ_arr,d,doc)

        self.summary = jmespath.search(self.update_jpath,summ_arr)
        self._save_item_type_summaries(reserve_arr)
        self.update_ndb()

    def _apply_summary(self,item_reserve):
        return jmespath.search(self.update_jpath+" | [0]",[item_reserve.get_dict()])
    
    def get_itemTypeSummary(self,item_type):
        fsDoc = FSDocument(self.get_firestore_client().document(self.parent_path+"/"+item_type.replace(" ","_")))
        if fsDoc.exists:
            return fsDoc.get('summary')
        return []
    
    def get_ReserveItemTypeSummary(self,itemType, reserveId):
        itemTypeSumm = self.get_itemTypeSummary(itemType)
        return jmespath.search(f"[?reserve_id == '{reserveId}']",itemTypeSumm)

    def getReserveItemAmts(self,item_type,invLoc=None):
        typeSummary = self.get_itemTypeSummary(item_type)
        uniqueItems = [*set(jmespath.search("[].id",typeSummary)),]
        location_filter = ""
        if invLoc is not None:
            location_filter = f" && inventory_location == '{invLoc}'"
        retAmts = {}
        retAmts['total'] = {x:sum(jmespath.search(f"[?id == '{x}'{location_filter}].total_reserved",typeSummary)) for x in uniqueItems}
        retAmts['by_item'] = {x:jmespath.search(f"[?id == '{x}'{location_filter}]",typeSummary) for x in uniqueItems}
        return retAmts

    def getReserveItemAmtsOLD(self,item_type):
        item_reserves = self._item_reserves.get(item_type,{})
        if len(item_reserves.keys()) == 0:
            item_reserves_tot = self._item_reserves_tot.get(item_type,{})
            item_singular = ItemWeek.CleanItemType(item_type)
            item_key = item_singular+"s"
            for resv in self.summary:
                c = resv['customer']
                l = resv['location']
                i = resv['item_name']
                n = resv['num_reserved']
                _id = resv['id']

                if resv.get(item_key,None) is not None:
                    for item in resv.get(item_key,[]):
                        try:
                            itemName = item.get('name',item.get(item_singular,None))
                            itemId = item.get('id',None)
                            if itemId is None:
                                itemId = item_singular+"_No_Name"
                            if itemName is None:
                                itemName = item_singular+"_No_Name"
                            _key = itemId #ItemWeek.CleanItemName(itemName)
                            amt = ReserveSummary._toNum(item_reserves_tot.get(_key,0),0)
                            num_items = ReserveSummary._toNum(resv.get('num_reserved',0),0) * ReserveSummary._toNum(item['qty'],1)
                            amt = amt + num_items
                            item_reserves_tot[_key] = amt
                            iRsvs = item_reserves.get(_key,[])
                            reserve_dict = {'id':_id,
                                            'customer':c,
                                            'location':l,
                                            'reserved_item':i,
                                            item_singular+'_name': itemName,
                                            'item_type': item_type, 
                                            'item_id':_key,
                                            'num_reserved':n,
                                            ItemWeek.CleanItemName(itemName)+"_qty":num_items}
                            iRsvs.append(reserve_dict)
                            item_reserves[_key] = iRsvs
                        except Exception as e:
                            print("ERROR:  "+str(item))
                            raise e
            self._item_reserves[item_type] = item_reserves
            self._item_reserves_tot[item_type] = item_reserves_tot
        return {'total':self._item_reserves_tot[item_type],'by_item':self._item_reserves[item_type]}
    
    def getReserveAmtByItem(self,item_type, item_id,invLoc=None):
        pltSumm = self.getReserveItemAmts(item_type,invLoc)
        return pltSumm['total'].get(item_id,0)

    def getItemReserves(self,item_type, item_id,invLoc=None):
        pltSumm = self.getReserveItemAmts(item_type,invLoc)
        return pltSumm['by_item'].get(item_id,[])
