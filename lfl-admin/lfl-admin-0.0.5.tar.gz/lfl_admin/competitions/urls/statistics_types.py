from django.urls import path

from lfl_admin.competitions.views import statistics_types

urlpatterns = [

    path('Statistics_types/Fetch/', statistics_types.Statistics_types_Fetch),
    path('Statistics_types/Add', statistics_types.Statistics_types_Add),
    path('Statistics_types/Update', statistics_types.Statistics_types_Update),
    path('Statistics_types/Remove', statistics_types.Statistics_types_Remove),
    path('Statistics_types/Lookup/', statistics_types.Statistics_types_Lookup),
    path('Statistics_types/Info/', statistics_types.Statistics_types_Info),
    path('Statistics_types/Copy', statistics_types.Statistics_types_Copy),

]
