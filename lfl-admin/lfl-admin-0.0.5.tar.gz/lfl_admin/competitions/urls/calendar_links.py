from django.urls import path

from lfl_admin.competitions.views import calendar_links

urlpatterns = [

    path('Calendar_links/Fetch/', calendar_links.Calendar_links_Fetch),
    path('Calendar_links/Add', calendar_links.Calendar_links_Add),
    path('Calendar_links/Update', calendar_links.Calendar_links_Update),
    path('Calendar_links/Remove', calendar_links.Calendar_links_Remove),
    path('Calendar_links/Lookup/', calendar_links.Calendar_links_Lookup),
    path('Calendar_links/Info/', calendar_links.Calendar_links_Info),
    path('Calendar_links/Copy', calendar_links.Calendar_links_Copy),

]
