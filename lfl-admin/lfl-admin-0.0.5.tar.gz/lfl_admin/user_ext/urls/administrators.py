from django.urls import path

from lfl_admin.user_ext.views import administrators
from lfl_admin.user_ext.views.administrators import Administrators_ImagesUpload

urlpatterns = [

    path('Administrators/Fetch/', administrators.Administrators_Fetch),
    path('Administrators/Add', administrators.Administrators_Add),
    path('Administrators/Update', administrators.Administrators_Update),
    path('Administrators/Remove', administrators.Administrators_Remove),
    path('Administrators/Lookup/', administrators.Administrators_Lookup),
    path('Administrators/Info/', administrators.Administrators_Info),
    path('Administrators/Copy', administrators.Administrators_Copy),
    path('Administrators/UploadImage', Administrators_ImagesUpload),
]
