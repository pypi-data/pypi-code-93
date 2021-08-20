from django.urls import path

from lfl_admin.competitions.views import goals

urlpatterns = [

    path('Goals/Fetch/', goals.Goals_Fetch),
    path('Goals/Add', goals.Goals_Add),
    path('Goals/Update', goals.Goals_Update),
    path('Goals/Remove', goals.Goals_Remove),
    path('Goals/Lookup/', goals.Goals_Lookup),
    path('Goals/Info/', goals.Goals_Info),
    path('Goals/Copy', goals.Goals_Copy),

]
