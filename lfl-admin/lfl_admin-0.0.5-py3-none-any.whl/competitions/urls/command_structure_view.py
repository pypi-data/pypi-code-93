from django.urls import path

from lfl_admin.competitions.views import command_structure_view

urlpatterns = [

    path('Command_structure_view/Fetch/', command_structure_view.Command_structure_view_Fetch),
    path('Command_structure_view/Add', command_structure_view.Command_structure_view_Add),
    path('Command_structure_view/Update', command_structure_view.Command_structure_view_Update),
    path('Command_structure_view/Remove', command_structure_view.Command_structure_view_Remove),
    path('Command_structure_view/Lookup/', command_structure_view.Command_structure_view_Lookup),
    path('Command_structure_view/Info/', command_structure_view.Command_structure_view_Info),
    path('Command_structure_view/Copy', command_structure_view.Command_structure_view_Copy),
    path('Command_structure_view/Paste', command_structure_view.Command_structure_view_Paste),

]
