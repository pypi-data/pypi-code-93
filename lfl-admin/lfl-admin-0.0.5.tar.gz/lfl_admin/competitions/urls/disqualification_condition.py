from django.urls import path

from lfl_admin.competitions.views import disqualification_condition

urlpatterns = [

    path('Disqualification_condition/Fetch/', disqualification_condition.Disqualification_condition_Fetch),
    path('Disqualification_condition/Add', disqualification_condition.Disqualification_condition_Add),
    path('Disqualification_condition/Update', disqualification_condition.Disqualification_condition_Update),
    path('Disqualification_condition/Remove', disqualification_condition.Disqualification_condition_Remove),
    path('Disqualification_condition/Lookup/', disqualification_condition.Disqualification_condition_Lookup),
    path('Disqualification_condition/Info/', disqualification_condition.Disqualification_condition_Info),
    path('Disqualification_condition/Copy', disqualification_condition.Disqualification_condition_Copy),

]
