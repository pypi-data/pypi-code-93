from django.urls import path

from lfl_admin.competitions.views import disqualification_types

urlpatterns = [

    path('Disqualification_types/Fetch/', disqualification_types.Disqualification_types_Fetch),
    path('Disqualification_types/Add', disqualification_types.Disqualification_types_Add),
    path('Disqualification_types/Update', disqualification_types.Disqualification_types_Update),
    path('Disqualification_types/Remove', disqualification_types.Disqualification_types_Remove),
    path('Disqualification_types/Lookup/', disqualification_types.Disqualification_types_Lookup),
    path('Disqualification_types/Info/', disqualification_types.Disqualification_types_Info),
    path('Disqualification_types/Copy', disqualification_types.Disqualification_types_Copy),

]
