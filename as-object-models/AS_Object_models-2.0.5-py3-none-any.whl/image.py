from .utils import FireStoreBase
from datetime import datetime
import logging
'''
Will need to use the BlobStore service to store the images
see: https://gist.github.com/merqurio/c0b62eb1e1769317907f
Thinking a form to upload the image and then we just store the image url here with the Image along with Meta Info

That could all be done through a separate form
'''
class Image(FireStoreBase):

    ext_fields = ['image_number','image_url','name','description','blobkey','storage_bucket','old_image_url']
    COLLECTION_NAME = 'application_data'

    def __init__(self, fsClient, **kwargs):
        self.image_number = kwargs.get('image_number','') #ndb.StringProperty(required=True)
        self.image_url = kwargs.get('image_url','') #ndb.StringProperty()
        self.name = kwargs.get('name','') #ndb.StringProperty()
        self.description = kwargs.get('description','') #ndb.StringProperty()
        self.blobkey = kwargs.get('blobkey','') #ndb.BlobKeyProperty()
        self.storage_bucket = kwargs.get('storage_bucket','')
        self.old_image_url = kwargs.get('old_image_url','')
        super(Image, self).__init__(fsClient, **kwargs)

    def base_path(self):
        return Image.__basePath(self._fsClient)

    @classmethod
    def basePath(cls):
        return Image.__basePath(Image.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return Image.COLLECTION_NAME+'/'+inClient.company+'/'+inClient.application+'/StorageBlob/Image'

    @classmethod
    def getInstance(cls,fsDocument):
        ref,snap = Image.getDocuments(fsDocument)
        docDict = snap.to_dict() if snap.exists else {}
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        return Image(Image.get_firestore_client(),**docDict)

    def getThumbnail(self):
        raise Exception('Method not implemented:  "getThumbnail(self):"')

    @classmethod
    def getImageInfo(cls, image):
        try:
            ref = Image.get_firestore_client().document(Image.basePath()+'/'+image['image_id'])
            img = Image.getInstance(ref)
            if img.exists:
                return img
        except Exception as e:
            logging.error(e)

        return None

    @classmethod
    def getAllImages(cls):
        col = Image.get_firestore_client().collection(Image.basePath())

        files = [dox for dox in col.list_documents()]
        resp = {}
        for imgRef in files:
            img = Image.getInstance(imgRef)
            resp[img.image_number] = {'filename': img.name,'web_path':img.image_url, 'instance': img}
        return resp

    @classmethod
    def createImage(cls, image_file):
        '''
        Need to convert this to use the new method for using Google Storage
        URL: https://googleapis.dev/python/storage/latest/client.html
        '''
        sClient = Image.get_storage_client()
        bucket = sClient.bucket(Image.get_backend_client().storage_bucket)
        prefix = str(datetime.now()).replace("-","").replace(":","").replace(" ","").replace(".","")+"_"
        tsFileName = prefix+image_file.filename
        blob = bucket.blob(tsFileName)

        blob.upload_from_file(image_file,content_type=image_file.mimetype)
        blob.make_public()
        image_url = blob.public_url

        data = {}
        data['image_url'] = image_url
        data['name'] = tsFileName
        data['storage_bucket'] = Image.get_client().storage_bucket
        data['description'] = 'Uploaded file from web application (post 2/14/20)'
        imageNumber = ImageNumber.get_next_image_number()
        data['image_number'] = imageNumber
        data['fs_docRef'] = Image.get_firestore_client().document(Image.basePath()+'/'+imageNumber)
        img = Image(Image.get_firestore_client(),**data)

        img.update_ndb()

        return img.get_dict()

class ImageNumber(object):

    @classmethod
    def get_next_image_number(cls):
        imgNumRef = Image.get_firestore_client().document(ImageNumber.basePath()+'/image')
        imgNum = imgNumRef.get()
        if not imgNum.exists:
            data = {}
            data['number'] = 99
            data['name'] = 'image'
            imgNumRef.set(data)

        number = imgNum.get('number')

        number = number + 1
        imgNumRef.update({'number':number,})
        return 'image-'+str(number)

    @classmethod
    def basePath(cls):
        return ImageNumber.__basePath(Image.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return 'data_number_sync/'+inClient.company+'/'+inClient.application