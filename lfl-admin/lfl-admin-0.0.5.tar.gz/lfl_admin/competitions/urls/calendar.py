from django.urls import path

from lfl_admin.competitions.views import calendar

urlpatterns = [

    path('Calendar/Fetch/', calendar.Calendar_Fetch),
    path('Calendar/Add', calendar.Calendar_Add),
    path('Calendar/Update', calendar.Calendar_Update),
    path('Calendar/Remove', calendar.Calendar_Remove),
    path('Calendar/Lookup/', calendar.Calendar_Lookup),
    path('Calendar/Info/', calendar.Calendar_Info),
    path('Calendar/Copy', calendar.Calendar_Copy),

]
