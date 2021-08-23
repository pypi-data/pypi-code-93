from .sales_inv_utils import SalesInvBase
from .inventory_active_items import InventoryLocation
from . import GetInstance

class MonthNotesCollection(SalesInvBase):

    ext_fields = ['grow_month','item_type','inventory_locatin','notes','soft_delete','parent_path','path']
    COLLECTION_NAME = 'application_data'

    def __init__(self,fsClient, **kwargs):
        self.soft_delete = kwargs.get('soft_delete',False)
        self.item_type = kwargs.get('item_type','')
        self.notes = kwargs.get('notes',None)
        self.grow_month = kwargs.get('grow_month','')
        self._inventory_location = kwargs.get('inventory_location',None)
        self._in_growMonthParent = kwargs.get('_growMonthParent',None)
        self._loaded_notes = {}
        super(MonthNotesCollection,self).__init__(fsClient, **kwargs)

        if self.notes is not None:
            item_ids = self.notes.keys()
            for item_id in item_ids:
                item_notes = self.notes[item_id]
                for item_note in item_notes:
                    item_note['_noteCollection'] = self
                    item_note['_growMonthParent'] = self._growMonthParent
                    item_note['item_type'] = self.item_type
                    note = ItemMonthNotes(self._fsClient,**item_note)
                    self._loaded_notes[note.id] = note

    def base_path(self):
        return self.parent_path+'/Notes'

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
    def getInstance(cls,docRef,gmParent):
        ref,snap = MonthNotesCollection.getDocuments(docRef)
        docDict = snap.to_dict() if snap.exists else {}
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        docDict['_growMonthParent'] = gmParent
        return MonthNotesCollection(MonthNotesCollection.get_firestore_client(),**docDict)
    
    @classmethod
    def getOrCreateInstance(cls,docRef,gmParent):
        col = cls.getInstance(docRef,gmParent)
        if not col.exists:
            col.update_ndb(True)
        return col

    @property
    def _growMonthParent(self):
        if self._in_growMonthParent is None:
            gwParDoc = self.get_firestore_client().document(self.parent_path)
            self._in_growMonthParent = GetInstance("GrowMonth",gwParDoc)
        return self._in_growMonthParent

    def getNotesByItemId(self,item_id):
        return [note for note in list(self._loaded_notes.values()) if note.item_id == item_id]

    def create_note(self, item_id, note):
        note_id = self._get_doc_id('Notes')
        item_note = {'note':note,'grow_month':self.grow_month,'id':note_id}
        item_note['_growMonthParent'] = self._growMonthParent
        item_note['_noteCollection'] = self
        item_note['_growMonthParent'] = self._growMonthParent
        item_note['item_type'] = self.item_type
        item_note['item_id'] = item_id
        note = ItemMonthNotes(self._fsClient,**item_note)
        self._loaded_notes[note.id] = note
        note._set_add_entries()
        note._set_update_entries()
        self.update_ndb()
        return note

    def delete_note(self, note_id):
        del self._loaded_notes[note_id]
        return self.update_ndb()
        
    def update_ndb(self, doCreate=False):
        self.notes = {}
        note_ids = self._loaded_notes.keys()
        for note_id in note_ids:
            note = self._loaded_notes[note_id]
            notes_array = self.notes.get(note.item_id,[])
            notes_array.append(note.get_dict())
            self.notes[note.item_id] = notes_array

        return super(MonthNotesCollection,self).update_ndb(doCreate)

class ItemMonthNotes(SalesInvBase):

    ext_fields = ['note','id','item_name','item_id','item_type','grow_month','soft_delete']
    COLLECTION_NAME = 'application_data'
    _active_plants = []
    
    """ Represents a Week where we can have reserve orders """

    def __init__(self, fsClient, **kwargs):
        self.soft_delete = kwargs.get('soft_delete',False)
        self.note = kwargs.get('note','') 
        self.note_id = kwargs.get('id',ItemMonthNotes.GetNextDNL('Notes'))
        self.item_name = kwargs.get('item_name','')
        self.item_id = kwargs.get('item_id','')
        self.item_type = kwargs.get('item_type')
        self.grow_month = kwargs.get('grow_month','')
        self._growMonthParent = kwargs.get('_growMonthParent',None)
        self._noteCollection = kwargs.get('_noteCollection',None)
        super(ItemMonthNotes, self).__init__(fsClient, **kwargs)

    def base_path(self):
        return self._noteCollection.path
    
    @classmethod
    def get_active(cls):
        return ItemMonthNotes.GetActive('ItemMonthNotes',ItemMonthNotes)
    
    @property
    def id(self):
        return self.note_id
    
    @property
    def path(self):
        return self._noteCollection.path

    @property
    def parent_path(self):
        return self._noteCollection.parent_path

    def get_schema(self):
        schema = self.get_bq_schema()
        schema['fields'].append({'field_name':'note','field_type':'string'})
        schema['fields'].append({'field_name':'plant_name','field_type':'string','field_required':True})
        schema['fields'].append({'field_name':'grow_month','field_type':'string','field_required':True})
        return schema

    def get_values_dict(self):
        values = self.get_dict()
        values['note'] = self.note
        values['item_name'] = self.item_name
        values['item_id'] = self.item_id
        values['grow_month'] = self.grow_month
        return values

    def get_api_summary(self):
        note = {'noteId':self.id,'note':self.note,'added_by':self.added_by,'added_date':self.timestamp}
        return note

    def update_ndb(self,doCreate=True):
        if doCreate:
            self._set_add_entries()
        self._set_update_entries()
        self._noteCollection._loaded_notes[self.id] = self
        return self._noteCollection.update_ndb(doCreate)

    def delete_resp(self):
        if self._noteCollection._loaded_notes.get(self.id,None) is not None:
            del self._noteCollection._loaded_notes[self.id]
        
        self._noteCollection.update_ndb()