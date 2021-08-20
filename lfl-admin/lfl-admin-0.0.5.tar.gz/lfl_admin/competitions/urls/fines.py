from django.urls import path

from lfl_admin.competitions.views import fines

urlpatterns = [

    path('Fines/Fetch/', fines.Fines_Fetch),
    path('Fines/Add', fines.Fines_Add),
    path('Fines/Update', fines.Fines_Update),
    path('Fines/Remove', fines.Fines_Remove),
    path('Fines/Lookup/', fines.Fines_Lookup),
    path('Fines/Info/', fines.Fines_Info),
    path('Fines/Copy', fines.Fines_Copy),

]
