from django.urls import path

from lfl_admin.competitions.views import goals_type

urlpatterns = [

    path('Goals_type/Fetch/', goals_type.Goals_type_Fetch),
    path('Goals_type/Add', goals_type.Goals_type_Add),
    path('Goals_type/Update', goals_type.Goals_type_Update),
    path('Goals_type/Remove', goals_type.Goals_type_Remove),
    path('Goals_type/Lookup/', goals_type.Goals_type_Lookup),
    path('Goals_type/Info/', goals_type.Goals_type_Info),
    path('Goals_type/Copy', goals_type.Goals_type_Copy),

]
