from django.urls import path

from lfl_admin.constructions.views import fields

urlpatterns = [

    path('Fields/Fetch/', fields.Fields_Fetch),
    path('Fields/Add', fields.Fields_Add),
    path('Fields/Update', fields.Fields_Update),
    path('Fields/Remove', fields.Fields_Remove),
    path('Fields/Lookup/', fields.Fields_Lookup),
    path('Fields/Info/', fields.Fields_Info),
    path('Fields/Copy', fields.Fields_Copy),

]
