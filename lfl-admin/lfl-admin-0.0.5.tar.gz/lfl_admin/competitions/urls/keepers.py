from django.urls import path

from lfl_admin.competitions.views import keepers

urlpatterns = [

    path('Keepers/Fetch/', keepers.Keepers_Fetch),
    path('Keepers/Add', keepers.Keepers_Add),
    path('Keepers/Update', keepers.Keepers_Update),
    path('Keepers/Remove', keepers.Keepers_Remove),
    path('Keepers/Lookup/', keepers.Keepers_Lookup),
    path('Keepers/Info/', keepers.Keepers_Info),
    path('Keepers/Copy', keepers.Keepers_Copy),

]
