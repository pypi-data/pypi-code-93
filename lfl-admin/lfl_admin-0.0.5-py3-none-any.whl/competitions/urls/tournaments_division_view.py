from django.urls import path

from lfl_admin.competitions.views import tournaments_division_view

urlpatterns = [

    path( 'Tournaments_division_view/Fetch/' , tournaments_division_view.Tournaments_division_view_Fetch ) ,
    path( 'Tournaments_division_view/Add' , tournaments_division_view.Tournaments_division_view_Add ) ,
    path( 'Tournaments_division_view/Update' , tournaments_division_view.Tournaments_division_view_Update ) ,
    path( 'Tournaments_division_view/Remove' , tournaments_division_view.Tournaments_division_view_Remove ) ,
    path( 'Tournaments_division_view/Lookup/' , tournaments_division_view.Tournaments_division_view_Lookup ) ,
    path( 'Tournaments_division_view/Info/' , tournaments_division_view.Tournaments_division_view_Info ) ,
    path( 'Tournaments_division_view/Copy' , tournaments_division_view.Tournaments_division_view_Copy ) ,

]
