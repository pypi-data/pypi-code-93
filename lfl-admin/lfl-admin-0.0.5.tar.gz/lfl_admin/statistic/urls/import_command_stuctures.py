from django.urls import path

from lfl_admin.statistic.views import import_command_stuctures

urlpatterns = [

    path('Import_command_stuctures/Fetch/', import_command_stuctures.Import_command_stuctures_Fetch),
    path('Import_command_stuctures/Add', import_command_stuctures.Import_command_stuctures_Add),
    path('Import_command_stuctures/Update', import_command_stuctures.Import_command_stuctures_Update),
    path('Import_command_stuctures/Remove', import_command_stuctures.Import_command_stuctures_Remove),
    path('Import_command_stuctures/Lookup/', import_command_stuctures.Import_command_stuctures_Lookup),
    path('Import_command_stuctures/Info/', import_command_stuctures.Import_command_stuctures_Info),
    path('Import_command_stuctures/Copy', import_command_stuctures.Import_command_stuctures_Copy),

]
