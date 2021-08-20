from google.cloud import storage
import pandas as pd
import logging
import os
import json
import xlrd
from datetime import datetime
import jmespath
from xlsxwriter.utility import xl_col_to_name
from .. client_utils import FirestoreClient
from .. utils import Email
from .. pub_sub import publish_message
from .. import DataNumberLookup, StorageBlob, DataStorageType, InventoryActiveItems, ItemWeek

class DownloadItemData(object):

    output_fields = ['id', 'customer_name', 'location_name', 'customer_id', 'location_id',
                     'Cust_Item_Num', 'Item_Num', 'Product_Name', 'CO_Item_Num', 'customer_item_number',
                     'Pack_Size', 'Tray', 'Double_Spike_Percent',
                     'customer_item_description', 'customer_case_number',
                     'Ti', 'Hi', 'Case_Width', 'Cases_Per_Pallet',
                     'Case_UPC', 'Case_Weight_lbs', 'Case_Height', 'Ethyl_Block', 'Box',
                     'CO_Case_Num', 'Special_Instructions_Recipe', 'Date_Code', 'Pot_Size_ML',
                     'Branches', 'POP', 'Pick', 'UPC_Location', 'Vase_Style',
                     'Sleeve', 'Top_Dressing', 'Heat_Pack',
                     'Date_Code_Type', 'Grade', 'Assortment', 'Tag_Type', 'Staging', 'Case_Length',
                     'Insert', 'List_Price_FOB_CO', 'List_Price',
                     'Commission_Pricing', 'profit_margin', 'retail_price', 'recipe_cost',
                     'retail_on_upc', 'Consumer_UPC']

    TMP_FOLDER = "/tmp/"
    SHEET_NAME = 'Customer_Items'
    STORAGE_TYPE = 'cust_plant_item'
    CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    def __init__(self, spreadSheetName, customer_id=None,
                 location_id=None,
                 emailAddress="system@analyticssupply.com",
                 bucket_name=None,
                 use_tmp=True):

        DownloadItemData.STORAGE_TYPE = 'cust_plant_item'
        DownloadItemData.SHEET_NAME = 'Customer_Items'

        self.email = emailAddress
        self._client = FirestoreClient.getInstance()
        self.use_tmp_folder = use_tmp
        self.file_name = self.create_file_name(spreadSheetName)
        if bucket_name is None:
            bucket_name = os.environ.get(
                "DATA_DOWNLOAD_BUCKET", "prod_analytics_supply_download_data")
            if bucket_name.find("download") < 0:
                raise Exception("Invalid bucket name being used")

        self.bucket_name = bucket_name
        self.custId = customer_id
        self.locId = location_id
        self.init_items = None
        self.items = []
        self.itemStorageType = None
        self.fields = None
        self.dropdowns = None
        self.plants = None
        self.df = None
        self.file_url = None

    def create_file_name(self, file_suffix):
        prefix = str(datetime.now()).replace("-", "").replace(":",
                                                              "").replace(" ", "").replace(".", "")+"_"
        if not file_suffix.endswith(".xlsx"):
            parts = file_suffix.split(".")
            file_suffix = parts[0] + ".xlsx"

        tmp_file = prefix+"_"+file_suffix
        if self.use_tmp_folder:
            tmp_file = DownloadItemData.TMP_FOLDER+tmp_file
        return tmp_file

    def upload_to_storage(self):
        logging.info("Beggining load to storage")
        sClient = self._client.storeClient
        bucket = sClient.bucket(self.bucket_name)
        email_folder = self.email.replace(
            "@", "__at__").replace(".", "__dot__")
        storageFile = self.file_name.replace(DownloadItemData.TMP_FOLDER, "")
        blob = bucket.blob(email_folder+"/"+storageFile)
        with open(self.file_name, "rb") as my_file:
            blob.upload_from_file(my_file, DownloadItemData.CONTENT_TYPE)
        blob.make_public()
        logging.info("Load complete, url created")
        self.file_url = blob.public_url

    def email_file(self, file_url=None):
        '''

        '''
        logging.info("Setting up to send email")
        e = Email()
        e.sender = "system@analyticssupply.com"
        e.subject = "Your file download"
        e.receivers.append(self.email)
        e.receivers.append('system@analyticssupply.com')
        storageFile = self.file_name.replace(DownloadItemData.TMP_FOLDER, "")
        url = self.file_url
        if file_url is not None:
            url = file_url

        if url is None:
            raise Exception(
                "The file hasn't been uploaded yet... do that first")

        e.html = '<p>Click the link to download the items you selected.</p><span><a href="' + \
            url+'">'+storageFile+'</a></span>'
        e.html = e.html + \
            "<p> Thank you, <br> System Administrator (system@analyticssupply.com)"
        resp = e.send()
        logging.info(resp)
        logging.info("Email sent... Done.")
        return resp

    def set_df(self, inDf):
        self.df = inDf

    def _run_load(self):
        logging.info("Beginning item load")
        self.init_items = self.load_items()
        logging.info("Load complete... now filtering")
        self._filter_items()
        self.itemStorageType = DataStorageType.get_dataStorageType(
            DownloadItemData.STORAGE_TYPE)
        self.fields = self.itemStorageType.get_storage_fields()
        self.dropdowns = self.get_dropdowns()
        self.plants = self.get_plants()
        logging.info("Loaded all system info..  complete")
        logging.info("loading up the pandas dataframe")
        self.df = self.load_df()
        logging.info("Dataframe Loaded... now ready to create file")

    def write_spreadsheet(self, fileName=None):
        if fileName is None:
            fileName = self.file_name

        logging.info("Writing output to file: "+fileName)
        writer = pd.ExcelWriter(fileName, engine='xlsxwriter')
        logging.info("Writing pandas output to excel")
        self.df.to_excel(
            writer, sheet_name=DownloadItemData.SHEET_NAME, index=False)
        workbook = writer.book
        worksheet = writer.sheets[DownloadItemData.SHEET_NAME]
        lookup = workbook.add_worksheet('lookup')

        dCol = 0
        refDict = {}
        logging.info("Setting up dropdowns")
        for key in self.dropdowns.keys():
            dropdown = self.dropdowns[key]
            aCol = xl_col_to_name(dCol)
            vals = [x['name'] for x in dropdown]
            ref = '=lookup!$'+aCol+'$2:$'+aCol+'$'+str(len(vals)+1)
            dRow = 1
            lookup.write(0, dCol, key)
            for val in vals:
                lookup.write(dRow, dCol, val)
                dRow += 1
            dCol += 1
            refDict[key] = ref

        for fldName in self.dropdowns.keys():
            if fldName in list(self.df.columns):
                self._add_validation(worksheet, fldName, refDict)

        length_list = [len(x) for x in self.df.columns]
        for i, width in enumerate(length_list):
            worksheet.set_column(i, i, width+5)

        logging.info("Writing finished spreadsheet")
        writer.save()

    def _add_validation(self, wrkSht, fldName, refDict):
        col = self.df.columns.get_loc(fldName)
        validate = {'validate': 'list', 'source': refDict[fldName]}
        wrkSht.data_validation(0, col, 1048575, col, validate)

    def load_df(self):
        df = pd.DataFrame(self.items)
        for plt in self.plants:
            df[plt] = df.Plants.apply(lambda x: self._load_plants(plt, x))

        cols = self.output_fields + self.plants
        df = df[cols]
        for fld in cols:
            df[fld] = df[fld].apply(self._clean_up_fields)
        return df

    def _clean_up_fields(self, fldVal):
        if isinstance(fldVal, str) and fldVal is not None:
            if len(fldVal.split("|")) == 1:
                return fldVal
            else:
                return fldVal.split("|")[1]
        return fldVal

    def _load_plants(self, plant_name, plant_arr):
        qty = 0
        if plant_arr is not None:
            if isinstance(plant_arr, list):
                for plt_ent in plant_arr:
                    if isinstance(plt_ent, dict):
                        name = plt_ent.get('plant', '--none--')
                        if len(name.split("|")) > 1:
                            name = name.split("|")[1]
                        tempQty = plt_ent.get('qty', 0)
                    else:
                        name = plt_ent if len(plt_ent.split(
                            "|")) == 1 else plt_ent.split("|")[1]
                        tempQty = 1

                    if name == plant_name:
                        qty = tempQty
        return qty

    def load_items(self):
        '''
        Override this method for Master
        '''
        logging.info("Grabbing all items")
        items = StorageBlob.getSB_of_Type('items')
        logging.info("Now getting customer and location info")
        return [self.get_item_information(x) for x in items]

    def get_item_information(self, inItem):
        loc = StorageBlob.getInstanceByPath(
            inItem.reference.parent.parent.path)
        cust = StorageBlob.getInstanceByPath(loc.reference.parent.parent.path)
        item = inItem.get_dict()
        item['customer_name'] = cust.customer_name
        item['customer_id'] = cust.id
        item['location_name'] = loc.location_name
        item['location_id'] = loc.id
        return item

    def _filter_items(self):
        if self.custId is not None:
            if self.locId is not None:
                self.items = [
                    x for x in self.init_items if x['location_id'] == self.locId]
            else:
                self.items = [
                    x for x in self.init_items if x['customer_id'] == self.custId]
        else:
            self.items = self.init_items

    def get_plants(self):
        plts = InventoryActiveItems.get_all_dict('Plants')
        plts = [plts[x]['name'] for x in plts.keys()]
        return plts

    def get_dropdowns(self):
        return DownloadItemData.GetDropdowns(self.fields)

    @classmethod
    def GetDropdowns(cls, inFields):
        dropdowns = {}
        optEntries = StorageBlob.getSB_of_Type('options')
        options = {'options': [x.get_dict() for x in optEntries]}

        for key in inFields.keys():
            field = inFields[key]
            if field.is_option_filled and field.field_name != 'Plants':
                if field.option_container.startswith("options"):
                    parts = field.option_container.split(".")
                    vals = jmespath.search(
                        parts[0]+".{id: id, name: option_value}", options)
                    vals = [{'name': x['name'], 'id':x['id']} for x in vals]
                else:
                    opts = StorageBlob.retrieve_option_data(
                        field.field_name, field.option_container)
                    vals = [{'name': x['label'], 'id':x['option_id']}
                            for x in opts]
                dropdowns[key] = vals
        return dropdowns


class DownloadItemDataMstr(DownloadItemData):

    exc_output_fields = ['customer_name', 'location_name', 'customer_id', 'location_id',
                         'Cust_Item_Num', 'customer_item_number',
                         'customer_item_description', 'customer_case_number',
                         'Consumer_UPC', 'retail_on_upc', 'retail_price']

    def __init__(self, spreadSheetName,
                 emailAddress="system@analyticssupply.com",
                 bucket_name=None,
                 use_tmp=True):
        DownloadItemData.STORAGE_TYPE = 'plant_item'
        DownloadItemData.SHEET_NAME = 'Master_Items'
        self.custId = None
        self.output_fields = [
            x for x in self.output_fields if x not in self.exc_output_fields]
        self.email = emailAddress
        self._client = FirestoreClient.getInstance()
        self.use_tmp_folder = use_tmp
        self.file_name = self.create_file_name(spreadSheetName)
        if bucket_name is None:
            bucket_name = os.environ.get(
                "DATA_DOWNLOAD_BUCKET", "prod_analytics_supply_download_data")
            if bucket_name.find("download") < 0:
                raise Exception("Invalid bucket name being used")

        self.bucket_name = bucket_name
        self.init_items = None
        self.items = []
        self.itemStorageType = None
        self.fields = None
        self.dropdowns = None
        self.plants = None
        self.df = None
        self.file_url = None

    def load_items(self):
        '''
        Override this method for Master
        '''
        logging.info("Grabbing all items")
        items = StorageBlob.getSB_of_Type('master_items')
        logging.info("Now getting customer and location info")
        return [x.get_dict() for x in items]


class StoreBlob(object):

    def __init__(self, blob_uri, filename):
        self.blob_uri = blob_uri
        self.client = FirestoreClient.getInstance()
        self.blob = self._load_blob()
        self.upload_file = DownloadItemData.TMP_FOLDER+filename
        self.sheet_names = self.save_file()
        self.fileType = 'unknown'
        if 'Master_Items' in self.sheet_names:
            self.fileType = 'master'

        if 'Customer_Items' in self.sheet_names:
            self.fileType = 'customer'

    def _load_blob(self):
        return storage.Blob.from_string(self.blob_uri, self.client.storeClient)

    def save_file(self):
        with open(self.upload_file, "wb") as file_obj:
            self.blob.download_to_file(file_obj)

        xls = xlrd.open_workbook(self.upload_file, on_demand=True)
        return xls.sheet_names()

    def get_fileType(self):
        return self.fileType


class ProcessItemUpload(object):

    SHEET_NAME = 'Customer_Items'
    STORAGE_TYPE = 'cust_plant_item'
    ID_FIELD = 'Cust_Item_Num'

    def __init__(self, email, upload_filename):
        ProcessItemUpload.SHEET_NAME = 'Customer_Items'
        ProcessItemUpload.STORAGE_TYPE = 'cust_plant_item'
        ProcessItemUpload.ID_FIELD = 'Cust_Item_Num'

        self.email = email
        self.client = FirestoreClient.getInstance()
        self.upload_file = upload_filename
        self.df = None
        self.dropdowns = None
        self.fields = None
        self.plant_lookup = None

    def process_file(self):
        self._pre_process()
        self._process_updates()

    def _process_updates(self):
        self.df = pd.read_excel(self.upload_file, ProcessItemUpload.SHEET_NAME)
        plts = InventoryActiveItems.get_all_dict('Plants')
        self.plant_lookup = {plts[x]['name']: plts[x] for x in plts.keys()}
        self.df['Plants'] = self.df.apply(self._create_plants, axis=1)
        for fieldName in self.dropdowns.keys():
            if fieldName in list(self.df.columns):
                self.df[fieldName] = self.df[fieldName].apply(
                    lambda x: self._update_recipes(x, fieldName))
        self.df['id'] = self.df[ProcessItemUpload.ID_FIELD]

        update_fields = [x for x in list(self.fields.keys()) if x not in [
            'plant_image', 'Recipe', 'recipe_cost', 'profit_margin', 'Simplewick']]
        update_fields = [
            x for x in update_fields if x in list(self.df.columns)]

        update_fields.append('id')
        self.df = self.df[update_fields]
        for fld in update_fields:
            self.df[fld] = self.df[fld].apply(self._clear_nans)
        updateDict = self.df.to_dict('records')
        for ent in updateDict:
            self._publish_updates(ent)

    def _publish_updates(self, entry):
        publish_message('updateItem', json.dumps(entry), {
                        'id': entry.get('id', '0'), 'email': self.email})

    def _clear_nans(self, value):
        if isinstance(value, list):
            return value
        if pd.isna(value) or pd.isnull(value):
            return ''
        return value

    def _create_plants(self, row):
        pltArray = []
        for plant in self.plant_lookup.keys():
            entry = self.plant_lookup[plant]
            qty = row[plant]
            if qty is not None and qty > 0:
                pltArray.append({'plant': entry['id']+"|"+plant, 'qty': qty})

        return pltArray

    def _update_recipes(self, value, colName):
        dropdown = self.dropdowns.get(colName, None)
        if dropdown is None:
            return value

        if len(dropdown) == 0 or dropdown[0]['id'].startswith('options'):
            return value
        newval = value
        for entry in dropdown:
            if entry['name'] == value:
                return entry['id']+"|"+entry['name']
        return newval

    def _pre_process(self):
        itemStorageType = DataStorageType.get_dataStorageType(
            ProcessItemUpload.STORAGE_TYPE)
        self.fields = itemStorageType.get_storage_fields()
        self.dropdowns = DownloadItemData.GetDropdowns(self.fields)


class ProcessItemUploadMstr(ProcessItemUpload):

    def __init__(self, email, upload_filename):
        ProcessItemUpload.SHEET_NAME = 'Master_Items'
        ProcessItemUpload.STORAGE_TYPE = 'plant_item'
        ProcessItemUpload.ID_FIELD = 'Item_Num'

        self.email = email
        self.client = FirestoreClient.getInstance()
        self.upload_file = upload_filename
        self.df = None
        self.dropdowns = None
        self.fields = None
        self.plant_lookup = None


class ProcessItemUpdate(object):

    def __init__(self, updated_dict, item_id, email):
        self.updated_entry = updated_dict
        self.item_id = item_id
        self.email = email

    def update_sb(self):
        updatePath = DataNumberLookup.get_path_for_dnl(self.item_id)
        logging.info("Updating... "+updatePath)
        StorageBlob.update_blob_parent_fromPath(self.updated_entry, updatePath)


def process_uploaded_file(blob_uri, filename, email):
    sBlob = StoreBlob(blob_uri, filename)
    processor = None
    if sBlob.get_fileType() == 'master':
        print("Processing Master Item Upload")
        processor = ProcessItemUploadMstr(email, sBlob.upload_file)
    else:
        if sBlob.get_fileType() == 'customer':
            print("Processing Customer Item Upload")
            processor = ProcessItemUpload(email, sBlob.upload_file)
        else:
            raise Exception(
                "Unknown uploaded file... valid sheet name not found")

    processor.process_file()


class DownloadPlantSupply(object):

    FILTER = "[*].{id: id, week_number: week_number, supplier_id: supplier.id, supplier_name: supplier.name, forecast: forecast, cost: cost, confirmation_num: confirmation_num, plant_name: item_name}"

    def __init__(self, spreadSheetName, start_wk, end_wk, bck_nm=None, email="system@analyticssupply.com", use_tmp=True):
        self.PLANT_PATH = 'application_data/Color_Orchids/Sales_Inventory/Converted/InventoryActiveItems/Plants'
        self.SUPPLIER_PATH = 'application_data/Color_Orchids/Customer_Tracking/StorageBlob/Supplier'
        self.GRWWK_PATH = 'application_data/Color_Orchids/Sales_Inventory/Converted/GrowWeek'
        self.start_week = start_wk
        self.end_week = end_wk
        self.email = email
        self.use_tmp_folder = use_tmp
        self._client = FirestoreClient.getInstance()

        self.file_name = self.create_file_name(spreadSheetName)
        if bck_nm is None:
            bck_nm = os.environ.get(
                "DATA_DOWNLOAD_BUCKET", "prod_analytics_supply_download_data")
            if bck_nm.find("download") < 0:
               raise Exception("Invalid bucket name being used")
        
        self.activePlants = None
        self.clean_names = None
        self.supplier_list = None
        self.supplies = None
        self.slDf = None
        self.suppDf = None

    def run_load(self):
        self.activePlants = self._load_active_plants()
        self.clean_names = jmespath.search('[*].clean_name', self.activePlants)
        self.supplier_list = self._load_suppliers()
        self.supplies = self._load_plant_supplies()
        self.slDf = pd.DataFrame(self.supplier_list)
        self.suppDf = pd.DataFrame(self.supplies)

    def add_clean_name(self, entry):
        entry['clean_name'] = ItemWeek.CleanItemName(entry['name'])
        return entry

    def _load_active_plants(self):
        activePlants = self._client.fsClient.document(self.PLANT_PATH)
        items = activePlants.get().get('items')
        activePltIds = jmespath.search('*.{id: id, name: name}', items)
        return [self.add_clean_name(x) for x in activePltIds]

    def _load_suppliers(self):
        suppColl = self._client.fsClient.collection(self.SUPPLIER_PATH)
        docRefs = [x for x in suppColl.list_documents()]
        return jmespath.search("[*].{id: id,name:name}", [x.get().to_dict() for x in docRefs])

    def create_file_name(self, file_suffix):
        prefix = str(datetime.now()).replace("-", "").replace(":",
                                                              "").replace(" ", "").replace(".", "")+"_"
        if not file_suffix.endswith(".xlsx"):
            parts = file_suffix.split(".")
            file_suffix = parts[0] + ".xlsx"

        tmp_file = prefix+"_"+file_suffix
        if self.use_tmp_folder:
            tmp_file = DownloadItemData.TMP_FOLDER+tmp_file
        return tmp_file

    def _filter_supply(self, supplyDoc):
        supply_entry = supplyDoc.get('supply')
        keys = [x for x in list(supply_entry.keys()) if x in self.clean_names]
        supplies = []
        supps = [supply_entry[x] for x in keys]
        for supp in supps:
            for s in supp:
                s['week_number'] = supplyDoc.reference.parent.parent.id
                supplies.append(s)
        return supplies

    def _load_plant_supplies(self):
        startWk = int(self.start_week.replace("_", ""))
        endWk = int(self.end_week.replace("_", ""))

        coll = self._client.fsClient.collection(self.GRWWK_PATH)
        docs = coll.list_documents()
        docRefs = [x for x in docs]
        supp_list = []
        clt = FirestoreClient.getInstance()
        for x in docRefs:
            week_id = x.id
            parts = week_id.split("_")
            year = int(parts[0])
            week = int(parts[1])
            yrWk = int(parts[0]+parts[1])
            if yrWk > startWk and yrWk < endWk:
                suppDocRef = self._client.fsClient.document(x.path+"/Supply/Plants")
                supps = self._filter_supply(self._clean_names,suppDocRef.get())
                mtchs = jmespath.search(DownloadPlantSupply.FILTER,supps)
                supp_list = supp_list + mtchs
        return supp_list
