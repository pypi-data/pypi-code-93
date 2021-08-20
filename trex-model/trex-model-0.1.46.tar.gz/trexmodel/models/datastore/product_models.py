'''
Created on 23 Jul 2021

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel, FullTextSearchable
from trexmodel.models.datastore.user_models import User
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet, MerchantUser
from trexlib.utils.string_util import is_empty, is_not_empty
import logging, json
from trexmodel import conf, program_conf
from trexlib.utils.string_util import random_string
from datetime import datetime, timedelta
from trexmodel.models.datastore.customer_models import Customer
import trexmodel.conf as model_conf
from trexmodel.models.datastore.model_decorators import model_transactional

logger = logging.getLogger('model')


class ProductCategory(BaseNModel,DictModel):
    '''
    merchant_acct as ancestor
    '''
    category_code           = ndb.StringProperty(required=True)
    category_label          = ndb.StringProperty(required=True)
    parent_category_code    = ndb.StringProperty(required=False)
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    has_child               = ndb.BooleanProperty(required=False, default=False)
    created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    modified_by             = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    
    
    dict_properties = ['category_code', 'category_label', 'parent_category_code', 'has_child']
    
    @staticmethod
    def create(category_code, category_label, merchant_acct, created_by=None, parent_category_code=None):
        created_by_key = None
        if created_by:
            created_by_key = created_by.create_ndb_key()
        created_category = ProductCategory(
                                            parent                  = merchant_acct.create_ndb_key(),
                                            category_code           = category_code,
                                            category_label          = category_label,
                                            parent_category_code    = parent_category_code,
                                            created_by              = created_by_key,
                                            )
        
        created_category.put()
        
        if is_not_empty(parent_category_code):
            parent_category = ProductCategory.get_by_categoy_code(parent_category_code, merchant_acct)
            if parent_category:
                parent_category.has_child = True
                parent_category.put()
        
        return created_category
        
    @staticmethod
    def update(category, category_code, category_label, modified_by=None):
        modified_by_key = None
        if modified_by:
            modified_by_key = modified_by.create_ndb_key()
        
        category.category_code      = category_code
        category.category_label     = category_label
        category.modified_by        = modified_by_key
        category.put()
    
    @staticmethod
    @model_transactional(desc='delete_by_parent_category_code')
    def delete_with_child(product_category, merchant_acct):
        ProductCategory.delete_by_parent_category_code(product_category.category_code, merchant_acct)
        product_category.delete()
        
    @staticmethod
    def get_structure_by_merchant_acct(merchant_acct):
        product_category_list = ProductCategory.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        
        product_category_dict_list = []
        
        for pc in product_category_list:
            product_category_dict_list.append(pc)
        
        return product_category_dict_list
    
    @staticmethod
    def get_by_categoy_code(category_code, merchant_acct):
        return ProductCategory.query(ndb.AND(ProductCategory.category_code==category_code), ancestor=merchant_acct.create_ndb_key()).get()
    
    @staticmethod
    def list_by_parent_category_code(merchant_acct, parent_category_code):
        product_category_list = ProductCategory.query(ndb.AND(ProductCategory.parent_category_code==parent_category_code),
                                                        ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        return product_category_list
    
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        product_category_list = ProductCategory.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        return product_category_list
        
    @staticmethod
    def delete_by_parent_category_code(parent_category_code, merchant_acct):
        found_category_code_list = ProductCategory.list_by_parent_category_code(merchant_acct, parent_category_code)
        
        logger.debug('found_category_code_list=%s', found_category_code_list)
        
        if found_category_code_list:
            for c in found_category_code_list:
                if c.has_child:
                    ProductCategory.delete_by_parent_category_code(c.category_code, merchant_acct)
                else:
                    c.delete()
    
    
class Product(BaseNModel, DictModel, FullTextSearchable):
    '''
    merchant_acct as ancestor
    '''
    product_sku                 = ndb.StringProperty(required=True)
    product_name                = ndb.StringProperty(required=True)
    product_desc                = ndb.StringProperty(required=False)
    category_code               = ndb.StringProperty(required=False)  
    
    barcode                     = ndb.StringProperty(required=False)   
    
    price                       = ndb.FloatProperty(required=False, default=.0)
    
    #for shipping purpose
    weight                      = ndb.FloatProperty(required=False, default=.0)
    length                      = ndb.FloatProperty(required=False, default=.0)
    width                       = ndb.FloatProperty(required=False, default=.0)
    height                      = ndb.FloatProperty(required=False, default=.0)
    
    created_datetime            = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime           = ndb.DateTimeProperty(required=True, auto_now=True)
    created_by                  = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    modified_by                 = ndb.KeyProperty(name="modified_by", kind=MerchantUser)  
    
    fulltextsearch_field_name   = 'product_name'
    
    dict_properties = ['product_sku', 'product_name', 'category_code', 'price', 'product_desc', 'barcode']
    
    @staticmethod
    def search_merchant_product(merchant_acct, product_name=None, product_sku=None, category_code=None,
                                 offset=0, start_cursor=None, limit=model_conf.MAX_FETCH_RECORD):
        
        search_text_list    = None
        query               = None
        
        if is_not_empty(product_name):
            search_text_list = product_name.split(' ')
            
        if merchant_acct:
            query = Product.query(ancestor=merchant_acct.create_ndb_key())
        else:
            query = Product.query()
            
        
        if is_not_empty(product_sku):
            query = query.filter(Product.product_sku==product_sku)
            
        elif is_not_empty(category_code):
            query = query.filter(Product.category_code==category_code)
        
        total_count                         = Product.full_text_count(search_text_list, query, conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH)
        
        (search_results, next_cursor)       = Product.full_text_search(search_text_list, query, offset=offset, 
                                                                   start_cursor=start_cursor, return_with_cursor=True, 
                                                                   limit=limit)
        
        return (search_results, total_count, next_cursor)
    
    @staticmethod
    def create(product_sku, product_name, category_code, merchant_acct, product_desc=None, price=.0, barcode=None, created_by=None):
        created_by_key = None
        if created_by:
            created_by_key = created_by.create_ndb_key()
        created_product = Product(
                                            parent              = merchant_acct.create_ndb_key(),
                                            product_sku         = product_sku,
                                            product_name        = product_name,
                                            barcode             = barcode,
                                            product_desc        = product_desc,
                                            category_code       = category_code, 
                                            created_by          = created_by_key,
                                            price               = price,
                                            )
        
        created_product.put()
        
        if price > 0:
            ProductPriceHistory(
                                parent      = created_product.create_ndb_key(),
                                price       = price,
                                created_by  = created_by_key,
                                ).put()
        
        return created_product
        
    @staticmethod
    def update(product, product_sku, product_name, category_code, price=.0, barcode=None, product_desc=None, updated_by=None):
        modified_by_key = None
        
        if updated_by:
            modified_by_key = updated_by.create_ndb_key()
        
        product.product_sku         = product_sku
        product.product_name        = product_name
        product.barcode             = barcode
        product.price               = price
        product.product_desc        = product_desc
        product.category_code       = category_code
        product.modified_by         = modified_by_key
        product.put() 
        
        if price>0 and product.price !=price:
            ProductPriceHistory(
                                parent      = product.create_ndb_key(),
                                price       = price,
                                created_by  = modified_by_key,
                                ).put()
        
    
class ProductPriceHistory(BaseNModel, DictModel):
    product                 = ndb.KeyProperty(name="product", kind=Product)
    price                   = ndb.FloatProperty(required=False, default=.0)
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    
        
class ProductFile(BaseNModel, DictModel):
    '''
    Product as ancestor
    '''
    product_file_label              = ndb.StringProperty(required=False)
    product_file_type               = ndb.StringProperty(required=True)
    product_file_public_url         = ndb.StringProperty(required=True)
    product_file_storage_filename   = ndb.StringProperty(required=True)
    
    dict_properties = ['product_file_public_url', 'product_file_storage_filename', 'product_file_type']
    
    @staticmethod
    def list_by_product(product):
        return ProductFile.query(ancestor=product.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def upload_file(uploading_file, product, merchant_acct, bucket, product_file_type=None):
        file_prefix                         = random_string(8)
        product_file_storage_filename       = 'merchant/'+merchant_acct.key_in_str+'/product/'+file_prefix+'-'+uploading_file.filename
        blob                                = bucket.blob(product_file_storage_filename)
        
        logger.debug('product_file_storage_filename=%s', product_file_storage_filename)
        
        blob.upload_from_string(
                uploading_file.read(),
                content_type=uploading_file.content_type
            )
        
        uploaded_url        = blob.public_url
        
        logger.debug('uploaded_url=%s', uploaded_url)
        logger.debug('product_file_type=%s', product_file_type)
        
        product_file = ProductFile(
                            parent = product.create_ndb_key(),
                            product_file_public_url             = uploaded_url,
                            product_file_storage_filename       = product_file_storage_filename,
                            product_file_type                   = product_file_type,
                            )
        
        product_file.put()
        
        return product_file
    
    @staticmethod
    def remove_file(product_file, bucket):
        
        old_logo_blob = bucket.get_blob(product_file.product_file_storage_filename) 
        if old_logo_blob:
            old_logo_blob.delete()
            product_file.delete()
        
    
