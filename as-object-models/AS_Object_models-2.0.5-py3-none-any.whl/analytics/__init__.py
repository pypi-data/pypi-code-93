from google.cloud import bigquery
import pandas as pd
import jmespath, os, json, logging,sys
from datetime import datetime,date, timedelta

from .. client_utils import FirestoreClient
from .. import ItemReserve, DataStorageType
from .. utils import FireStoreBase

logger = logging.getLogger('ColorOrchids_DataLoad')

class DataLoad(object):
    
    BIGQUERY_FIELDS = {'timestamp':{'field_type':'DATETIME','name': 'added_dt','description':'The date/time that the object was created'},
                    'up_timestamp':{'field_type':'DATETIME','name': 'updated_dt','description':'The date/time that the object was last updated'},
                    'data_type':{'field_type':'STRING','description':'The data type that identifies this data row'},
                    'id':{'field_type':'STRING','description':'Unique identifier for this element in the collection'},
                    'collection':{'field_type':'STRING','description':'The collection name where this object was housed'},
                    'parent_id':{'field_type':'STRING','description':'the unique identifier of the parent object'},
                    'parent_collection':{'field_type':'STRING','description':'the parent collection where the parent object is housed'},
                    'added_by':{'field_type':'STRING','description':'The name of the individual that added this object'},
                    'updated_by':{'field_type':'STRING','description':'The name of the individual that updated this object last'},
                    'added_dt':{'field_type':'DATETIME','description':'The date/time that the object was created'},
                    'updated_dt':{'field_type':'DATETIME','description':'The date/time that the object was last updated'},
                    'path':{'field_type':'STRING','description':'String representation of where this object is located on the database'}}

    BIGQUERY_MAPPING = {'string':'STRING','int':'INTEGER','boolean':'BOOLEAN',
        'float':'FLOAT','currency':'FLOAT','date':'DATE','datetime':'DATETIME',
        'auto_inc':'STRING','image':'STRING','readonly':'STRING'}


    TABLE_NAMES = {'customer':'colororchids_customer.customer_base',
                'supply':'colororchids_inventory.plant_supplies',
                'weeks':'colororchids_weeks.grow_weeks',
                'location':'colororchids_location.locations_base',
                'cust_plant_item':'colororchids_items.items_base',
                'reserves':'colororchids_reserves.reserves_base',
                'reserves_plants':'colororchids_reserves.reserves_plants_base',
                'reserves_vase':'colororchids_reserves.reserves_vase_base',
                'recipe_costing':'colororchids_recipecosting.recipe_costing_base',
                'recipe_costing_plants':'colororchids_recipecosting.recipe_costing_plants_base',
                'recipe_costing_items':'colororchids_recipecosting.recipe_costing_items_base',
                'plant_inventory':'colororchids_inventory.inventory_plant_base',
                'vase_inventory':'colororchids_inventory.inventory_vase_base'}

    def __init__(self):
        self.clt = FirestoreClient.getInstance()
        self.bqClt = bigquery.Client(project=os.environ.get('GOOGLE_CLOUD_PROJECT'))
        self.processed_types = {}
        self.schemas_dict = {}
        self.df_dict = {}
        self.load_schemas()

    def load_schemas(self):
        logger.info("Setting schemas for use in BigQuery")
        self.get_record_type_schema('customer')
        self.get_record_type_schema('location')
        self.get_record_type_schema('recipe_costing')
        #self.add_rc_items_schema()
        self.get_record_type_schema('recipe_costing_items')
        self.create_vase_inv_schema()
        self.add_rc_plants_schema()
        self.create_reserve_schema()
        self.create_plant_schema()
        self.create_vase_schema()
        self.create_plant_inv_schema()
        self.create_week_schema()
        self.create_plant_supply_schema()
        logger.info("Schemas loaded...")

    def add_rc_items_schema(self):
        if self.schemas_dict.get('recipe_costing_items',None) is None:
            rciSchema = {}
            rciSchema['recipe_costing_id'] = {'field_name':'recipe_costing_id','field_type':'string'}
            rciSchema['name'] = {'field_name':'name','field_type':'string'}
            rciSchema['item_value'] = {'field_name':'item_value','field_type':'string'}
            rciSchema['recipe_costing_path'] = {'field_name':'recipe_costing_path','field_type':'string'}
            rciSchema['item_path'] = {'field_name':'item_path','field_type':'string'}
            rciSchema['item_type'] = {'field_name':'type','field_type':'string'}
            rciSchema['item_id'] = {'field_name':'item_id','field_type':'string'}
            rciSchema['qty'] = {'field_name':'qty','field_type':'int'}
            rciSchema['unit_cost'] = {'unit_cost':'qty','field_type':'float'}
            rciSchema['cost'] = {'cost':'qty','field_type':'float'}
            self.schemas_dict['recipe_costing_items'] = {'storage_fields':rciSchema}
    
    def create_vase_inv_schema(self):
        if self.schemas_dict.get('vase_inventory',None) is None:
            pSchema = {}
            self.create_schema_entry(pSchema,'grow_month','string')
            self.create_schema_entry(pSchema,'grow_month_dt','datetime')
            self.create_schema_entry(pSchema,'reserve_total','int')
            self.create_schema_entry(pSchema,'inventory_add','int')
            self.create_schema_entry(pSchema,'calc_actual','int')
            self.create_schema_entry(pSchema,'prev_actual','int')
            self.create_schema_entry(pSchema,'name','string')
            self.create_schema_entry(pSchema,'inventory_set','boolean')
            self.create_schema_entry(pSchema,'item_type','string')
            self.create_schema_entry(pSchema,'actual','int')
            self.create_schema_entry(pSchema,'item_id','string')
            self.create_schema_entry(pSchema,'clean_item_name','string')
            self.schemas_dict['vase_inventory'] = {'storage_fields':pSchema}

    def add_rc_plants_schema(self):
        if self.schemas_dict.get('recipe_costing_plants',None) is None:
            rcpSchema = {}
            rcpSchema['recipe_costing_id'] = {'field_name':'recipe_costing_id','field_type':'string'}
            rcpSchema['name'] = {'field_name':'name','field_type':'string'}
            rcpSchema['item_value'] = {'field_name':'item_value','field_type':'string'}
            rcpSchema['recipe_costing_path'] = {'field_name':'recipe_costing_path','field_type':'string'}
            rcpSchema['item_path'] = {'field_name':'item_path','field_type':'string'}
            rcpSchema['item_type'] = {'field_name':'type','field_type':'string'}
            rcpSchema['item_id'] = {'field_name':'item_id','field_type':'string'}
            rcpSchema['qty'] = {'field_name':'qty','field_type':'int'}
            rcpSchema['unit_cost'] = {'unit_cost':'qty','field_type':'float'}
            rcpSchema['cost'] = {'cost':'qty','field_type':'float'}
            self.schemas_dict['recipe_costing_plants'] = {'storage_fields':rcpSchema}
    
    def create_reserve_schema(self):
        rSchema = {}
        self.create_schema_entry(rSchema,'num_reserved','int')
        self.create_schema_entry(rSchema,'finish_week','string')
        self.create_schema_entry(rSchema,'reserve_date','datetime')
        self.create_schema_entry(rSchema,'customer_id','string')
        self.create_schema_entry(rSchema,'customer_name','string')
        self.create_schema_entry(rSchema,'location_id','string')
        self.create_schema_entry(rSchema,'location_name','string')
        self.create_schema_entry(rSchema,'item_id','string')
        self.create_schema_entry(rSchema,'item_name','string')
        self.schemas_dict['reserves'] = {'storage_fields':rSchema}

    def create_plant_supply_schema(self):
        rs = {}
        self.create_schema_entry(rs,'supplier_name','string')
        self.create_schema_entry(rs,'supplier_id','string')
        self.create_schema_entry(rs,'cost','float')
        self.create_schema_entry(rs,'forecast','int')
        self.create_schema_entry(rs,'plant_id','string')
        self.create_schema_entry(rs,'plant_name','string')
        self.create_schema_entry(rs,'supply_id','string')
        self.create_schema_entry(rs,'finish_week','string')
        self.schemas_dict['supply'] = {'storage_fields':rs}

    def create_plant_schema(self):
        '''
        {'plant_id': 'recipe_costing-139',
        'plant_name': 'Bonita',
        'plant_path': 'application_data/Color_Orchids/Customer_Tracking/StorageBlob/recipe_costing/recipe_costing-139',
        'reserve_id': 'Reserve-791',
        'qty': 1}
        '''
        pSchema = {}
        self.create_schema_entry(pSchema,'plant_id','string')
        self.create_schema_entry(pSchema,'plant_name','string')
        self.create_schema_entry(pSchema,'plant_path','string')
        self.create_schema_entry(pSchema,'reserve_id','string')
        self.create_schema_entry(pSchema,'qty','int')
        self.create_schema_entry(pSchema,'total_reserved','int')
        self.schemas_dict['reserves_plants'] = {'storage_fields':pSchema}

    def create_vase_schema(self):
        '''
        {'vase_id': 'recipe_costing-139',
        'vase_name': 'Bonita',
        'vase_path': 'application_data/Color_Orchids/Customer_Tracking/StorageBlob/recipe_costing/recipe_costing-139',
        'reserve_id': 'Reserve-791',
        'qty': 1}
        '''
        pSchema = {}
        self.create_schema_entry(pSchema,'vase_id','string')
        self.create_schema_entry(pSchema,'vase_name','string')
        self.create_schema_entry(pSchema,'vase_path','string')
        self.create_schema_entry(pSchema,'reserve_id','string')
        self.create_schema_entry(pSchema,'qty','int')
        self.create_schema_entry(pSchema,'total_reserved','int')
        self.schemas_dict['reserves_vase'] = {'storage_fields':pSchema}
    
    def create_week_schema(self):
        '''
        '''
        pSchema = {}
        self.create_schema_entry(pSchema,'week_monday','datetime')
        self.create_schema_entry(pSchema,'week_number','int')
        self.create_schema_entry(pSchema,'year','int')
        self.create_schema_entry(pSchema,'month','int')
        self.create_schema_entry(pSchema,'week_date','datetime')
        self.create_schema_entry(pSchema,'year_month','string')
        self.create_schema_entry(pSchema,'year_month_int','int')
        self.create_schema_entry(pSchema,'year_week_int','int')
        self.schemas_dict['weeks'] = {'storage_fields':pSchema}
    
    def create_plant_inv_schema(self):
        '''
        {'updated_by': None,
        'finish_week': '2016_06',
        'actual': 0,
        'up_timestamp': '2017-02-13T04:27:30.487390+00:00',
        'name': 'Succulent',
        'dw_sync_status': 'updated',
        'item_name': 'Succulent',
        'id': '2016_06:recipe_costing-150:all',
        'plant': 'Plant-5573190633914368',
        'timestamp': '2017-02-13T04:27:30.487380+00:00',
        'item_type': 'Plants',
        'added_by': 'jason@colororchids.com',
        'item_id': 'recipe_costing-150',
        'color': 'all',
        'is_all': True}
        '''
        pSchema = {}
        self.create_schema_entry(pSchema,'actual','int')
        self.create_schema_entry(pSchema,'finish_week','string')
        self.create_schema_entry(pSchema,'finish_week_dt','datetime')
        self.create_schema_entry(pSchema,'name','string')
        self.create_schema_entry(pSchema,'id','string')
        self.create_schema_entry(pSchema,'item_id','string')
        self.create_schema_entry(pSchema,'item_name','string')
        self.create_schema_entry(pSchema,'color','string')
        self.create_schema_entry(pSchema,'is_all','boolean')
        self.create_schema_entry(pSchema,'item_type','string')
        self.schemas_dict['plant_inventory'] = {'storage_fields':pSchema}

    
    '''
    This assumes you are getting a document from firestore
    '''
    def get_dict_value(self, doc):
        ref,snap = FireStoreBase.getDocuments(doc)
        if not snap.exists:
            return None
        d = snap.to_dict()
        d['id'] = ref.id
        d['collection'] = ref.parent.id
        d['parent_id'] = ref.parent.parent.id
        d['parent_collection'] = ref.parent.parent.parent.id
        d['path'] = ref.path
        d['parent_path'] = ref.parent.parent.path
        return d

    def convert_growweek_to_date(self, growWeek):
        dt = datetime.strptime(growWeek+'1', '%Y_%W%w')
        dtStr = dt.isoformat()
        return dt, dtStr

    def delete_destination(self, dsId,tblId, bqClt):
        '''
        Pass in the id of the dataset it (dsId) and the table id (tblId)
        Then use the bigquery client (bqClt) to delete the table
        '''
        table_ref = self.bqClt.dataset(dsId).table(tblId)
        self.bqClt.delete_table(table_ref)  # API request
        logger.debug('Table {}:{} deleted.'.format(dsId, tblId))

    def get_rename(self, column):
        if column in list(DataLoad.BIGQUERY_FIELDS.keys()):
            return DataLoad.BIGQUERY_FIELDS[column].get('name',None)
        return None

    def generate_schema(self, field,schema):
        schemaField = DataLoad.BIGQUERY_FIELDS.get(field,schema.get(field,None))
        desc = schemaField.get('description','')
        if self.needs_schema_dt(field,schema):
            fieldType = schemaField['field_type']
            if fieldType.lower() == 'datetime':
                return bigquery.SchemaField(field, bigquery.enums.SqlTypeNames.TIMESTAMP,description=desc)
            else:
                return bigquery.SchemaField(field, bigquery.enums.SqlTypeNames.DATE,description=desc)
        else:
            if schemaField['field_type'] == 'int':
                return bigquery.SchemaField(field, bigquery.enums.SqlTypeNames.INTEGER,description=desc)
            elif schemaField['field_type'] == 'float' or schemaField['field_type'] == 'currency':
                return bigquery.SchemaField(field, bigquery.enums.SqlTypeNames.FLOAT,description=desc)
            elif schemaField['field_type'] == 'boolean':
                return bigquery.SchemaField(field, bigquery.enums.SqlTypeNames.BOOLEAN,description=desc)
            else:
                return bigquery.SchemaField(field, bigquery.enums.SqlTypeNames.STRING,description=desc)

        return None

    def needs_schema_dt(self, field,schema):
        fld = DataLoad.BIGQUERY_FIELDS.get(field,None)
        if fld is None:
            fld = schema.get(field,None)
            if fld is None:
                return False
            if fld['field_type'] in ['data','datetime']:
                return True
            return False
        if fld.get('field_type','STRING') == 'DATETIME':
            return True
        return False

    def check_col(self, x, inSchema):
        bqFields = list(DataLoad.BIGQUERY_FIELDS.keys())
        schemaFields = list(inSchema.keys())
        if x in bqFields or x in schemaFields:
            if inSchema.get(x,{'field_type':'string'})['field_type'] != 'group':
                return True
        return False

    def get_record_type_schema(self, record_type, filter=None):
        stored_schema = self.schemas_dict.get(record_type,None)
        if stored_schema is not None:
            if filter is not None:
                return jmespath.search("storage_fields.* | "+filter,stored_schema)
            return jmespath.search("storage_fields",stored_schema)

        dst = DataStorageType.get_dataStorageType(record_type)
        if not dst.exists:
            logger.warning("Can't find schema for: "+record_type)
            return None

        schema = dst.get_schema(get_extends=True)
        if schema is None:
            return None

        self.schemas_dict[record_type] = schema

        if filter is not None:
            return jmespath.search("storage_fields.* | "+filter,schema)
        return jmespath.search("storage_fields",schema)

    def load_bq_data(self, records,record_type):
        try:
            return self._load_bq_data(records,record_type)
        except Exception as e:
            logger.error("Trouble processing records: {}".format(record_type))
            raise e

    def generate_df(self, records,record_type):
        logger.debug("Generating the dataFrame for: "+record_type)
        df = pd.DataFrame(records)
        record_schema = self.get_record_type_schema(record_type)
        cols = [x for x in list(df.columns) if self.check_col(x,record_schema)]
        df = df[cols]
        df.rename(columns = {x:self.get_rename(x) for x in cols if self.get_rename(x) is not None}, inplace=True )
        cols = list(df.columns)
        for col in list(df.columns):
            if self.needs_schema_dt(col,record_schema):
                df[col] = df[col].apply(lambda x: None if x is None or x == '' or x.lower() == 'none' or x.lower() == 'null' else x)
                df[col] = pd.to_datetime(df[col])
            else:
                df[col] = df[col].apply(lambda x: self.convert_data_field(x,col,record_schema))
        
        self.df_dict['record_type'] = df
        logger.debug("DataFrame loaded for: "+record_type)
        return df

    def _get_bq_schema(self, df,record_type):
        record_schema = self.get_record_type_schema(record_type)
        return [self.generate_schema(x,record_schema) for x in list(df.columns) if self.generate_schema(x,record_schema) is not None]

    def _submit_bq(self, df,record_type):
        logger.debug("Submitting job for: "+record_type)
        df.fillna(0,inplace=True)
        bq_schema = self._get_bq_schema(df,record_type)
        dsName, tblName = DataLoad.TABLE_NAMES[record_type].split('.')
        tblRef = self.bqClt.dataset(dsName).table(tblName)
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE",autodetect=True,schema=bq_schema)
        job = self.bqClt.load_table_from_dataframe(
            df, tblRef, job_config=job_config
        )  # Make an API request.
        return job.result()

    def _load_bq_data(self, records,record_type):
        split_func = self.check_for_split(record_type)
        if split_func is not None:
            new_records = split_func(records)
            records = new_records['records']
            added_records = new_records['add_records']
            for addedRec in added_records:
                self.load_bq_data(addedRec['records'],addedRec['record_type'])
        
        logger.info("-----> Begin Processing: "+record_type)
        self.processed_types[record_type] = records

        df = self.generate_df(records,record_type)

        result = self._submit_bq(df,record_type)
        logger.info("<----- Finished Processing: "+record_type)
        return result

    def check_for_split(self, record_type):
        if record_type == 'recipe_costing':
            return self.split_recipe_costing
        
        if record_type == 'cust_plant_item':
            return self.split_items

        if record_type == 'reserves':
            return self.reserve_split_vals

        return self.plain_split_vals

    def plain_split_vals(self,records):
        newRecs = []
        for old_rec in records:
            rec = {k:self.convert_to_val(v,str,raiseException=False) for k,v in old_rec.items()}
            newRecs.append(rec)
        return {'records':newRecs,'add_records':[]}

    def split_recipe_costing(self,records):
        newRecs = []
        for old_rec in records:
            rec = {k:v for k,v in old_rec.items()}
            del rec['image']
            newRecs.append(rec)
        return {'records':newRecs,'add_records':[]}

    def convert_to_val(self,inVal, outType, raiseException=True, defaultVal=0):
        try:
            return outType(inVal)
        except Exception as e:
            if raiseException:
                logger.error("Trying to convert ({}) to ({})".format(inVal,str(outType)))
                raise e
            return defaultVal

    def convert_data_field(self, field_value, field_name, schema, defaultVal=None):
        schemaField = DataLoad.BIGQUERY_FIELDS.get(field_name,schema.get(field_name,{'field_name':field_name,'field_type':'string'}))
        default_value = defaultVal
        if default_value is None:
            tmpDef = ''
            if schemaField['field_type'] in ['int','float','currency']:
                tmpDef = 0
            if schemaField['field_type'] == 'boolean':
                tmpDef = False
            
            tmpDef2 = schemaField.get('field_default',None)
            if tmpDef2 is None or tmpDef2 == '':
                default_value = tmpDef
            else:
                default_value = tmpDef2
        
        return self.convert_field(schemaField, field_value, default_value)

    def convert_field(self, fieldSchema, field_value,defaultVal=0):
        ft = fieldSchema['field_type']
        if ft == 'int':
            return self.convert_to_val(field_value,int,raiseException=False,defaultVal=defaultVal)

        if ft == 'float' or ft == 'currency':
            return self.convert_to_val(field_value,float,raiseException=False,defaultVal=defaultVal)
        
        if ft == 'boolean':
            return self.convert_bool(field_value)

        return self.convert_to_val(field_value,str,False,'')

    def convert_bool(self,inValue):
        if isinstance(inValue, bool):
            return inValue

        if (inValue is None or str(inValue).strip() == ""):
            return False

        if (inValue is not None and len(str(inValue)) > 0):
            if str(inValue).lower() == 'n/a': # saying that this field is not applicable
                return False

            if (str(inValue).lower() == "true" or str(inValue) == "1" or str(inValue).lower() == "y"  or str(inValue).lower() == "yes"):
                return True
            
            if (str(inValue).lower() == "false" or str(inValue) == "0" or str(inValue).lower() == "n"  or str(inValue).lower() == "no"):
                return False
            else:
                return False
        return False

    def split_items(self,records):
        fixed_recs = []
        plant_records = {'record_type': 'recipe_costing_plants', 'records':[]}
        rc_records = {'record_type': 'recipe_costing_items','records':[]}

        for old_rec in records:
            rec = {k:v for k,v in old_rec.items()}
            schema_fields = list(self.get_record_type_schema('cust_plant_item').values())
            if rec.get('plant_image',None) is not None:
                del rec['plant_image']
            for rcField in schema_fields:
                #print(rcField)
                field = rec.get(rcField['field_name'],None)
                #,"[?category == 'Recipe']"
                
                if field is not None:
                    if rcField['category'] == 'Recipe':
                        if rcField['field_name'] == 'Plants':
                            plRecs = self.process_item_plants(rec,field,rcField)
                            plant_records['records'] = plant_records['records'] + plRecs
                            del rec[rcField['field_name']]
                        else:
                            itRecs = self.process_item_recipe(rec,field,rcField)
                            if itRecs['success']:
                                rc_records['records'].append(itRecs['value'])
                            #else:
                            #    print(itRecs)
                            parts = field.split("|") if isinstance(field, str) else [field]
                            fieldValue = parts[0] if len(parts) == 1 else parts[1]
                            rec[rcField['field_name']] = self.convert_field(rcField, fieldValue)
                    else:
                        rec[rcField['field_name']] = self.convert_field(rcField, field)
            fixed_recs.append(rec)
        return {'records':fixed_recs,'add_records':[plant_records,rc_records]}

    def process_item_recipe(self, rec, field, schemaField):
        self.add_rc_items_schema()
        if field is None or field == '':
            return {'success': False, 'msg': schemaField['field_name']+': is Empty', 'value':None}

        parts = field.split("|") if isinstance(field, str) else [field]
        fieldValue = parts[0] if len(parts) == 1 else parts[1]
        rc_id = parts[0] if len(parts) > 1 else None

        rcEntry = None

        if rc_id is not None:
            searchEntry = "[?id == '"+rc_id+"'] | [0]"
            rcEntry = jmespath.search(searchEntry,self.processed_types['recipe_costing'])
        else:
            filterJp = schemaField['option_container'].split(":")[2]
            rcEntries = jmespath.search(filterJp,self.processed_types['recipe_costing'])
            if rcEntries is not None and len(rcEntries) > 0:
                for rcE in rcEntries:
                    if fieldValue == rcE['name']:
                        rcEntry = rcE
                if rcEntry is None:
                    rcEntry = rcEntries[0]
        
        if rcEntry is not None:
            rcRec = jmespath.search("{recipe_costing_id: id, name: name, recipe_costing_path: path, item_type: item_type, unit_cost: price_each}",rcEntry)
            rcRec['item_id'] = rec['id']
            rcRec['item_path'] = rec['path']
            rcRec['unit_cost'] = self.convert_to_val(rcRec['unit_cost'],float,raiseException=False)
            rcRec['cost'] = self.convert_to_val(rcRec['unit_cost'],float,raiseException=False)
            rcRec['item_value'] = str(fieldValue)
            rcRec['qty'] = 1
            if rcEntry['item_type'] in ['Ethyl Block','Heat Pack'] or rcEntry['price_type'] == 'count':
                rcRec['cost'] = rcRec['unit_cost'] * self.convert_to_val(rcRec['item_value'],float)
                rcRec['item_value'] = self.convert_to_val(rcRec['item_value'],str)
            return {'success': True, 'msg': 'All Good', 'value':rcRec}
        return {'success': False, 'msg': schemaField['field_name']+': is None', 'value':None}

    def process_item_plants(self, rec, field, fieldSchema):
        self.add_rc_plants_schema()
        plant_recs = []
        for plant in field:
            rc_id, plant_name = plant['plant'].split("|")
            searchEntry = "[?id == '"+rc_id+"'] | [0] | {recipe_costing_id: id, name: name, recipe_costing_path: path, item_type: item_type, unit_cost: price_each}"
            rcEntry = jmespath.search(searchEntry,self.processed_types['recipe_costing'])
            rcEntry['item_id'] = rec['id']
            rcEntry['item_path'] = rec['path']
            rcEntry['unit_cost'] = self.convert_to_val(rcEntry['unit_cost'],float,raiseException=False)
            rcEntry['qty'] = self.convert_to_val(plant['qty'],int)
            rcEntry['item_value'] = plant_name
            rcEntry['cost'] = rcEntry['unit_cost'] * rcEntry['qty']
            plant_recs.append(rcEntry)
        p2 = {}
        for pr in plant_recs:
            key = pr['recipe_costing_id'] + pr['item_id']
            pRec = p2.get(key,None)
            if pRec is None:
                p2[key] = pr
            else:
                pRec['qty'] = pRec['qty'] + pr['qty']
                p2[key] = pRec
        for p in list(p2.values()):
            p['cost'] = self.convert_to_val(p['qty'],int) * self.convert_to_val(p['unit_cost'],float)

        return list(p2.values())

    def get_customer_location_item(self,rec):
        rec['customer_id'] = rec['customer']['id']
        rec['customer_name'] = rec['customer']['name']
        del rec['customer']

        rec['location_id'] = rec['location']['id']
        rec['location_name'] = rec['location']['name']
        del rec['location']

        rec['item_id'] = rec['item']['id']
        rec['item_name'] = rec['item']['name']
        del rec['item']

    def get_plant_info(self,rec):
        plant_recs = []
        plants = rec.get('Plants',[])
        for plant in plants:
            plant_rec  = {}
            plant_rec['plant_id'] = plant['plant']['id']
            plant_rec['plant_name'] = plant['plant']['name']
            plant_rec['plant_path'] = plant['plant']['path']
            plant_rec['reserve_id'] = rec['id']
            plant_rec['qty'] = self.convert_to_val(plant['qty'],int,raiseException=False, defaultVal=1)
            plant_rec['total_reserved'] = plant_rec['qty'] * self.convert_to_val(rec['num_reserved'],int, raiseException=False)
            plant_recs.append(plant_rec)

        if rec.get('Plants',None) is not None:
            del rec['Plants']
        return plant_recs

    def get_vase_info(self,rec):
        vase = rec.get('Vase',None)
        if vase is not None and isinstance(vase,dict):
            vase_rec = {}
            vase_rec['vase_id'] = vase['id']
            vase_rec['vase_name'] = vase['name']
            vase_rec['vase_path'] = vase['path']
            vase_rec['reserve_id'] = rec['id']
            vase_rec['qty'] = 1
            vase_rec['total_reserved'] = self.convert_to_val(rec['num_reserved'],int, raiseException=False)
            del rec['Vase']
            return vase_rec
        return None

    def reserve_split_vals(self, records):
        if self.schemas_dict.get('reserves',None) is None:
            self.load_reserves_schemas()

        reserve_types = {'num_reserved':int, 'shipped': bool, 'qty': int }
        plant_records = {'record_type': 'reserves_plants', 'records':[]}
        vase_records = {'record_type': 'reserves_vase', 'records':[] }
        newRecs = []
        ret_reserves = {'records':newRecs,'add_records':[plant_records,vase_records]}
        for old_rec in records:
            new_rec = {k:v for k,v in old_rec.items()}
            self.get_customer_location_item(new_rec)
            plRecs = self.get_plant_info(new_rec)
            plant_records['records'] = plant_records['records'] + plRecs
            vaseRec = self.get_vase_info(new_rec)
            if vaseRec is not None:
                vase_records['records'].append(vaseRec)
            rec = {k:self.convert_to_val(v,reserve_types.get(k,str),raiseException=False) for k,v in new_rec.items()}

            if rec.get('reserve_date',None) is None or rec.get('reserve_date','').strip() == '':
                _, dtStr = self.convert_growweek_to_date(rec['finish_week'])
                rec['reserve_date'] = dtStr
            newRecs.append(rec)
        
        return ret_reserves

    def create_schema_entry(self, inSchema, fieldName, fieldType):
        inSchema[fieldName] = {'field_name': fieldName, 'field_type': fieldType}

    def load_weeks(self):
        logger.info("==== BEGIN load_weeks() ====")
        weekCollection = self.clt.fsClient.collection('application_data/Color_Orchids/Sales_Inventory/Converted/GrowWeek')
        weeks = [self.get_dict_value(d) for d in weekCollection.list_documents()]
        newWeeks = []
        for week in weeks:
            if week is not None:
                week['week_date'] = self.monday_of_calenderweek(week['year'],week['week_number'])
                week['month'] = week['week_date'].month
                week['year_month'] = str(week['year'])+"_"+str(week['month']).zfill(2)
                week['year_month_int'] = int(week['year_month'].replace("_",""))
                week['year_week_int'] = int(week['id'].replace("_",""))
                newWeeks.append(week)
        self.load_bq_data(newWeeks,'weeks')


    def monday_of_calenderweek(self,year,week):
        first = date(year, 1, 1)
        base = 1 if first.isocalendar()[1] == 1 else 8
        return first + timedelta(days=base - first.isocalendar()[2] + 7 * (week - 1))

    def load_customers(self):
        logger.info("==== BEGIN load_customers() ====")
        customersCollection = self.clt.fsClient.collection('application_data/Color_Orchids/Customer_Tracking/StorageBlob/customer')
        customers = [self.get_dict_value(d) for d in customersCollection.list_documents()]
        self.load_bq_data(customers,'customer')

    def load_cust_locations(self):
        logger.info("==== BEGIN load_cust_locations() ====")
        locationsCollection = self.clt.fsClient.collection_group('locations')
        locations = [self.get_dict_value(d) for d in locationsCollection.stream()]
        self.load_bq_data(locations,'location')

    def load_recipe_costing(self):
        logger.info("==== BEGIN load_recipe_costing() ====")
        recipe_costingCollection = self.clt.fsClient.collection('application_data/Color_Orchids/Customer_Tracking/StorageBlob/recipe_costing')
        recipe_costing = [self.get_dict_value(d) for d in recipe_costingCollection.list_documents()]
        self.load_bq_data(recipe_costing,'recipe_costing')
    
    def load_cust_items(self):
        logger.info("==== BEGIN load_cust_items() ====")
        itemsCollection = self.clt.fsClient.collection_group('items')
        items = [self.get_dict_value(x) for x in itemsCollection.stream()]
        self.load_bq_data(items,'cust_plant_item')

    def load_cust_reserves(self):
        logger.info("==== BEGIN load_cust_reserves() ====")
        reservesCollection = self.clt.fsClient.collection_group('Reserves')
        reserves = [self.get_dict_value(x) for x in reservesCollection.stream()]
        self.load_bq_data(reserves,'reserves')

    def load_plant_supply(self):
        '''
        Example Path: /application_data/Color_Orchids/Sales_Inventory/Converted/GrowWeek/2020_41/Supply/Plants
        self.create_schema_entry(rs,'supplier_name','string')
        self.create_schema_entry(rs,'supplier_id','string')
        self.create_schema_entry(rs,'cost','float')
        self.create_schema_entry(rs,'forecast','int')
        self.create_schema_entry(rs,'plant_id','string')
        self.create_schema_entry(rs,'plant_name','string')
        self.create_schema_entry(rs,'supply_id','string')
        '''
        logger.info("==== BEGIN load_plant_supply() ====")
        weekCollection = self.clt.fsClient.collection('application_data/Color_Orchids/Sales_Inventory/Converted/GrowWeek')
        gwDocs = [doc for doc in weekCollection.list_documents()]
        supply_recs = []
        for gwDoc in gwDocs:
            supplyDoc = self.clt.fsClient.document(gwDoc.path+'/Supply/Plants')
            supplySnap = supplyDoc.get()
            if supplySnap.exists:
                data = supplySnap.get('supply')
                itemKeys = data.keys()
                for itemKey in itemKeys:
                    entries = data[itemKey]
                    for entry in entries:
                        supplyData = {}
                        supplyData['supplier_name'] = entry.get('supplier',{}).get('name','No_Name')
                        supplyData['supplier_id'] = entry.get('supplier',{}).get('id','No_Id')
                        supplyData['cost'] = entry.get('cost','0.0')
                        supplyData['forecast'] = entry.get('forecast','0')
                        supplyData['plant_name'] = entry.get('item_name','NoPlantName')
                        supplyData['plant_id'] = entry.get('item_id','NoPlantId')
                        supplyData['supply_id'] = entry.get('id','NoSupplyId')
                        supplyData['finish_week'] = gwDoc.id
                        if not entry.get('soft_delete',False):
                            supply_recs.append(supplyData)
        self.load_bq_data(supply_recs,'supply')

    def load_vase_inventory(self):
        logger.info("==== BEGIN load_vase_inventory() ====")
        growMonthCollection = self.clt.fsClient.collection('application_data/Color_Orchids/Sales_Inventory/Converted/GrowMonth')
        gmDocs = [doc for doc in growMonthCollection.list_documents()]
        vase_inventory_recs = []
        for gmDoc in gmDocs:
            itemCollectionPath = gmDoc.path+"/Items"
            itemCollection = self.clt.fsClient.collection(itemCollectionPath)
            itemDocs = [self.get_dict_value(x) for x in itemCollection.list_documents()]
            for itemDoc in itemDocs:
                rec = {k:v for k,v in itemDoc.items()}
                rec['item_id'] = rec.get('item',{'id':''})['id']
                rec['grow_month_dt'] = datetime.strptime(rec['grow_month'],"%Y_%m").isoformat()
                if rec.get('item',None) is not None:
                    del rec['item']
                rec['clean_item_name'] = rec['item_name']
                del rec['item_name']
                vase_inventory_recs.append(rec)
        self.load_bq_data(vase_inventory_recs,'vase_inventory')
    
    def load_plant_inventory(self):
        logger.info("==== BEGIN load_plant_inventory() ====")
        gwCollection = self.clt.fsClient.collection('application_data/Color_Orchids/Sales_Inventory/Converted/GrowWeek')
        plant_rec_inv = []
        for d in gwCollection.list_documents():
            self._process_plant_inventory_growweek(d,plant_rec_inv)
        self.load_bq_data(plant_rec_inv,'plant_inventory')
    
    def _process_plant_inventory_growweek(self,growWeekDoc, plant_rec_inv):
        try:
            if len(growWeekDoc.id) == 7:
                pInvPath = growWeekDoc.path+'/Items/Plants'
                plant_inv = self.get_dict_value(self.clt.fsClient.document(pInvPath))
                if plant_inv is not None:
                    items = plant_inv.get('items',{})
                    itemsPlts = list(items.keys())
                    for plt in itemsPlts:
                        plantInv = items[plt]
                        rec = {k:v for k,v in plantInv.items()}
                        rec['item_id'] = rec.get('item',{'id',''})['id']
                        rec['item_name'] = rec.get('item',{'name',''})['name']
                        if 'groupings' in list(rec.keys()):
                            del rec['groupings']

                        del rec['item']
                        colors = ['all'] if rec.get('color_groupings',None) is None else list(rec['color_groupings'].keys())
                        if not 'all' in colors:
                            colors.append('all')

                        for color in colors:
                            cRec = {k:v for k,v in rec.items()}
                            del cRec['color_groupings']
                            del cRec['want_qty']
                            cRec['color'] = color
                            actual_number = rec.get('color_groupings',{color:rec.get('actual',0)})
                            if color == 'all':
                                cRec['actual'] = rec['actual']
                                cRec['is_all'] = True
                            else:
                                cRec['is_all'] = False
                                cRec['actual'] = actual_number[color]
                            
                            cRec['actual'] = self.convert_to_val(cRec['actual'],int)
                            cRec['id'] = cRec['finish_week']+":"+cRec['item_id']+":"+cRec['color']
                            _, dtStr = self.convert_growweek_to_date(cRec['finish_week'])
                            cRec['finish_week_dt'] = dtStr
                            plant_rec_inv.append(cRec)
        except Exception as e:
            logger.error("Problem processing: "+growWeekDoc.id)
            raise e
