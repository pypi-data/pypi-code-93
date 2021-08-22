#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "this module is for Amazon Web Services"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "3.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2017"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import the required modules
#import boto
import boto3 # python3 version

import os # for local pathname check and making directories



### AWS S3 name
S3='s3'

### AWS S3 storage class mode
SC_REDUCED='REDUCED_REDUNDANCY'
SC_IA='STANDARD_IA'
SC_STD='STANDARD'



### AWS S3 functions

def set_logger(name='boto3',level=0):
	"""set the aws s3 log system
	(level=0 means disabled)
	(level=10 means debugging)
	(level=50 means critical)
	"""
	boto3.set_stream_logger(name,level=level)
	
	
def get_buckets_list():
	"""Retrieve the list of all existing S3 buckets"""
	s3 = boto3.client('s3')
	reply = s3.list_buckets()
	buckets_list=[ bucket["Name"] for bucket in reply['Buckets'] ]
	return buckets_list
	
	
	
### AWS S3 Objects

class Summary_Object:
	"""This is the representation of S3 distant file metadata."""
	def __init__(self,object):
		"""object must be an S3 bucket object"""
		self.object=object
	
	def get_metadata(self):
		"""return metadata of distant s3 object file (if not a delete marker)"""
		if not self.get_deleted():
			data = self.object.head()
			metadata = data["Metadata"]
		else:
			metadata = {}
		return metadata
		
	def get_path(self):
		"""returns the file path location on the distant bucket"""
		return self.object.key

	def get_latest(self):
		"""if its the last version of this file object return True otherwise False"""
		return self.object.is_latest

	def get_version(self):
		"""return the version of this file object"""
		return self.object.version_id

	def get_time(self):
		"""return the date and time of the last file object modification creation"""
		return self.object.last_modified # return exempl: <class 'datetime.datetime'> 2017-12-03 01:33:03+00:00

	def get_size(self):
		"""give the size in bytes of the object file"""
		size=self.object.size
		if size : return size
		else : return 0

	def get_deleted(self):
		"""if the file object been set deleted returns True otherwise False"""
		### As far as I can tell,
		### the only clean way of identifying delete markers in boto3 
		### is to use the list_object_versions paginator, handling the DeleteMarkers and Versions attributes oneself.
		return self.object.size==None and self.object.e_tag==None and self.object.storage_class==None# alls equal None if there is a delete-marker on the object

	def get_hash(self):
		"""give the condensat of the object file"""
		### If an object is created by either the Multipart Upload or Part Copy operation, the ETag is not an MD5 digest. 
		hash=self.object.e_tag
		if hash : return hash.strip('"')
		else : return ''



class Object(Summary_Object):
	"""This is the representation of an existing S3 distant file."""
	def __init__(self,object):
		"""object must be an S3 bucket object"""
		Summary_Object.__init__(self,object)

	def get_metadata(self):
		"""return metadata of the distant s3 object file (if not a delete marker)"""
		if not self.object.delete_marker :
			metadata = self.object.metadata
			#missing_metadata = self.object.missing_meta
		else :
			metadata = {}
		return metadata
	
	def get_latest(self):
		"""if its the last version of this file object return True otherwise False"""
		### always returns True because the Object class is only instantiated for the latest version files.
		return True
	
	def get_size(self):
		"""give the size in bytes of the object file"""
		size=self.object.content_length
		if size : return size
		else : return 0

	def get_deleted(self):
		"""if the file object been set deleted returns True otherwise False"""
		### always returns False because the Object class is only instantiated for not deleted files.
		return False# self.object.delete_marker
		
		

### AWS S3 Bucket

class Bucket:
	"""for the use of Amazons3  Buckets"""
	def __init__(self,bucket_name,chunk_size=104857600,download_attempts=3,max_queue=10,storage_class=SC_IA):#chunk_size=104857600 # = 100MB
		"""bucket name must be an exiting S3 bucket name"""
		#s3 = boto3.client('s3')
		s3 = boto3.resource(S3)
		#s3 = boto.connect_s3()
		
		self.bucket = s3.Bucket(bucket_name)
		
		### If use_threads is False, no threads will be used in performing transfers , all logic will be ran in the main thread.
		### Note that in setting use_threads to False, the value for max_concurrency is ignored as the main thread will only ever be used
		### Ensure that multipart uploads only happen if the size of a transfer is not larger than S3's size limit for nonmultipart uploads, which is 5GB.
		### param max_io_queue : The maximum amount of read parts that can be queued in memory to be written for a download. The size of each of these read parts is at most the size of ``io_chunksize``.
		### param io_chunksize : The max size of each chunk in the io queue. Currently, this is size used when ``read`` is called on the	downloaded stream as well.
		#print(help(boto3.s3.transfer.TransferConfig))
		self.conf = boto3.s3.transfer.TransferConfig(max_concurrency=1,multipart_threshold=chunk_size,multipart_chunksize=chunk_size,num_download_attempts=download_attempts,max_io_queue=max_queue,io_chunksize=chunk_size)
		self.storage_class=storage_class
		
		
	def get_name(self):
		"""gives the current S3 bucket name"""
		return self.bucket.name
	
	
	def get_all_objects(self):
		"""returns all the contents of the bucket as summary objects list"""
		### bucket.object_versions.all() is an iterator, each object is downloaded on each iteration, not all at same time
		#self.bucket.objects.all()
		return [ Summary_Object(o) for o in self.bucket.object_versions.all() ] # <class 'boto3.resources.factory.s3.ObjectVersion'>
		#self.bucket.object_versions.filter(Prefix="delset",Delimiter="check",KeyMarker="delset/local") #VersionIdMarker
	
	
	def get_object(self,pathname):
		"""gives the specified pathname object of the bucket"""
		return Object(self.bucket.Object(pathname)) # <class 'boto3.resources.factory.s3.Object'>
		
		
	def set_metadata(self,source_key,metadata,callback=None):
		"""set metadata of the distant s3 object file"""
		obj=self.bucket.Object(source_key)
		obj.metadata.update(metadata)
		source={'Bucket':self.bucket.name,'Key':source_key}
		
		### need to use copy method instead, because copy_object,copy_from fail if file size>5368709120
		obj.copy_from(CopySource=source,Metadata=obj.metadata,MetadataDirective='REPLACE')
		
		#extra={'StorageClass':self.storage_class,'Metadata':obj.metadata,"MetadataDirective":'REPLACE' }
		#self.bucket.copy(source,source_key,ExtraArgs=extra,Callback=callback,SourceClient=None,Config=self.conf)
		
		
	def copy_file(self,source_key,source_version,new_key,callback=None):
		"""copy an extiting S3 bucket file to another bucket location"""
		source={'Bucket':self.bucket.name,'Key':source_key,'VersionId':source_version}
		extra={'StorageClass':self.storage_class,}
		self.bucket.copy(source,new_key,ExtraArgs=extra,Callback=callback,SourceClient=None,Config=self.conf)
		
		
	def upload_file(self,localpath,name,type=None,encoding=None,callback=None):
		"""upload a local file into the distant S3 bucket"""
		extra={}
		extra['StorageClass']=self.storage_class
		#extra['Metadata']={"MD5":hash,"mtime":mt}}
		if type : extra['ContentType']=type
		if encoding : extra['ContentEncoding']=encoding
		### problem with self.bucket.put_object and ContentMD5 argument
		self.bucket.upload_file(localpath,name,ExtraArgs=extra,Callback=callback,Config=self.conf)

		
	def download_file(self,item,local_path,overwrite=False,callback=None):
		"""download a distant S3 bucket file on local location"""
		if os.path.lexists(local_path) and overwrite==False :
			raise FileExistsError(local_path)
		else :
			directory=os.path.dirname(local_path)
			os.makedirs(directory,exist_ok=True)
			self.bucket.download_file(item,local_path,Callback=callback,Config=self.conf)# replace local file if already exist 
			
			
	def download_file_version(self,item,version,local_path,overwrite=False,callback=None):
		"""download a specific version of distant S3 bucket file on local location"""
		if os.path.lexists(local_path) and overwrite==False :
			raise FileExistsError(local_path)
		else :
			directory=os.path.dirname(local_path)
			os.makedirs(directory,exist_ok=True)
			extra={"VersionId": version}
			self.bucket.download_file(item,local_path,ExtraArgs=extra,Callback=callback,Config=self.conf)# replace local file if already exist 


	def delete_file(self,item,version=None):
		"""delete a file on the distant S3 bucket"""
		if version :
			### definitely remove the item
			response = self.bucket.delete_objects( Delete={'Objects':[{'Key':item,'VersionId':version}],'Quiet':True} )
		else :
			### set a delete mark
			response = self.bucket.delete_objects( Delete={'Objects':[{'Key':item}],'Quiet':True} )
			
		if "Errors" in response :
			print(response["Errors"])
			raise response["Errors"]
		
