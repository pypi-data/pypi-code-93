from django.urls import path

from lfl_admin.user_ext.views import administrators_view

urlpatterns = [

    path('Administrators_view/Fetch/', administrators_view.Administrators_view_Fetch),
    path('Administrators_view/Add', administrators_view.Administrators_view_Add),
    path('Administrators_view/Update', administrators_view.Administrators_view_Update),
    path('Administrators_view/Remove', administrators_view.Administrators_view_Remove),
    path('Administrators_view/Lookup/', administrators_view.Administrators_view_Lookup),
    path('Administrators_view/Info/', administrators_view.Administrators_view_Info),
    path('Administrators_view/Copy', administrators_view.Administrators_view_Copy),

]
