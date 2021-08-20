from django.urls import path

from lfl_admin.user_ext.views import users_regions

urlpatterns = [

    path('Users_regions/Fetch/', users_regions.Users_regions_Fetch),
    path('Users_regions/Add', users_regions.Users_regions_Add),
    path('Users_regions/Update', users_regions.Users_regions_Update),
    path('Users_regions/Remove', users_regions.Users_regions_Remove),
    path('Users_regions/Lookup/', users_regions.Users_regions_Lookup),
    path('Users_regions/Info/', users_regions.Users_regions_Info),
    path('Users_regions/Copy', users_regions.Users_regions_Copy),

]
