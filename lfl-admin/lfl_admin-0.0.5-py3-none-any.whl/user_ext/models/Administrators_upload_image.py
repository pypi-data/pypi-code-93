import logging

from django.db import transaction

from isc_common.http.DSResponse import JsonResponseWithException
from isc_common.models.upload_image import Common_UploadImage
from isc_common.models.users_images import Users_images
from lfl_admin.user_ext.models.administrators import Administrators

logger = logging.getLogger(__name__)


@JsonResponseWithException()
class DSResponse_Administrators_UploadImage(Common_UploadImage):
    def __init__(self, request):
        with transaction.atomic():
            file = request.FILES.get('upload_attatch')
            if file is not None:
                image, administartor_id = self.upload_image(request=request)
                user = Administrators.objects.get(id=administartor_id).user
                res, created = Users_images.objects.get_or_create(image=image, main_model=user)
                logger.debug(f'Created: {created}')
