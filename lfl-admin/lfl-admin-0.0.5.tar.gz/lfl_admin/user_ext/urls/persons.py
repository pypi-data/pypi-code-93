from django.urls import path

from lfl_admin.user_ext.views import persons

urlpatterns = [

    path('Persons/Fetch/', persons.Persons_Fetch),
    path('Persons/Add', persons.Persons_Add),
    path('Persons/Update', persons.Persons_Update),
    path('Persons/Remove', persons.Persons_Remove),
    path('Persons/Lookup/', persons.Persons_Lookup),
    path('Persons/Info/', persons.Persons_Info),
    path('Persons/Copy', persons.Persons_Copy),

]
