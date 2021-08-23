from os import makedirs
import requests

from django.conf import settings
from django.db.models import F

from saleboxdjango.models import ProductCategory, \
    Product, ProductVariant


class SaleboxPullPOSImages:
    def __init__(self):
        self.update_productcategories()
        self.update_products()
        self.update_productvariants()

    def get_folder(self, dir):
        target_dir = f'{settings.MEDIA_ROOT}/salebox/{dir}'
        try:
            makedirs(target_dir)
        except:
            pass

        return target_dir

    def sync_image(self, id, urlpath, dir):
        target_dir = self.get_folder(dir)

        # fetch image
        try:
            url = f'{settings.SALEBOX["API"]["URL"]}/{urlpath}'
            suffix = urlpath.split('.')[-1]
            filename = f'{id}.{urlpath.split("/")[-1][0:6]}.{suffix}'
            target = f'{target_dir}/{filename}'

            r = requests.get(url)
            if r.status_code == 200:
                open(target, 'wb').write(r.content)
                return filename, True
        except:
            print('ERROR')

        return None, False

    def update_products(self):
        products = Product \
                    .objects \
                    .exclude(image__isnull=True) \
                    .exclude(local_image_version__exact=F('image'))

        for p in products:
            path, success = self.sync_image(p.id, p.image[1:], 'posp')
            if success:
                p.local_image_version = p.image
                p.local_image = path
                p.save()

    def update_productcategories(self):
        categories = ProductCategory \
                        .objects \
                        .exclude(image__isnull=True) \
                        .exclude(local_image_version__exact=F('image'))

        for c in categories:
            path, success = self.sync_image(c.id, c.image[1:], 'pospc')
            if success:
                c.local_image_version = c.image
                c.local_image = path
                c.save()

    def update_productvariants(self):
        variants = ProductVariant \
                    .objects \
                    .exclude(image__isnull=True) \
                    .exclude(local_image_version__exact=F('image'))

        for v in variants:
            path, success = self.sync_image(v.id, v.image[1:], 'pospv')
            if success:
                v.local_image_version = v.image
                v.local_image = path
                v.save()