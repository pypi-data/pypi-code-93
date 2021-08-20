from django.urls import path

from lfl_admin.statistic.views import import_command_stuctures_log

urlpatterns = [

    path('Import_command_stuctures_log/Fetch/', import_command_stuctures_log.Import_command_stuctures_log_Fetch),
    path('Import_command_stuctures_log/Add', import_command_stuctures_log.Import_command_stuctures_log_Add),
    path('Import_command_stuctures_log/Update', import_command_stuctures_log.Import_command_stuctures_log_Update),
    path('Import_command_stuctures_log/Remove', import_command_stuctures_log.Import_command_stuctures_log_Remove),
    path('Import_command_stuctures_log/Lookup/', import_command_stuctures_log.Import_command_stuctures_log_Lookup),
    path('Import_command_stuctures_log/Info/', import_command_stuctures_log.Import_command_stuctures_log_Info),
    path('Import_command_stuctures_log/Copy', import_command_stuctures_log.Import_command_stuctures_log_Copy),

]
