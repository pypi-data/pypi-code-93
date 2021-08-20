from django.urls import path

from lfl_admin.competitions.views import division_stages

urlpatterns = [

    path( 'Division_stages/Fetch/' , division_stages.Division_stages_Fetch ) ,
    path( 'Division_stages/Add' , division_stages.Division_stages_Add ) ,
    path( 'Division_stages/Update' , division_stages.Division_stages_Update ) ,
    path( 'Division_stages/Remove' , division_stages.Division_stages_Remove ) ,
    path( 'Division_stages/Lookup/' , division_stages.Division_stages_Lookup ) ,
    path( 'Division_stages/Info/' , division_stages.Division_stages_Info ) ,
    path( 'Division_stages/Copy' , division_stages.Division_stages_Copy ) ,

]
