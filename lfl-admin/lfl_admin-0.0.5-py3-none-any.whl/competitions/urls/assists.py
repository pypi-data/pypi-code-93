from django.urls import path

from lfl_admin.competitions.views import assists

urlpatterns = [

    path('Assists/Fetch/', assists.Assists_Fetch),
    path('Assists/Add', assists.Assists_Add),
    path('Assists/Update', assists.Assists_Update),
    path('Assists/Remove', assists.Assists_Remove),
    path('Assists/Lookup/', assists.Assists_Lookup),
    path('Assists/Info/', assists.Assists_Info),
    path('Assists/Copy', assists.Assists_Copy),

]
