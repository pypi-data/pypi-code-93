from django.urls import path

from lfl_admin.competitions.views import technical_defeat

urlpatterns = [

    path( 'Technical_defeat/Fetch/' , technical_defeat.Technical_defeat_Fetch ) ,
    path( 'Technical_defeat/Add' , technical_defeat.Technical_defeat_Add ) ,
    path( 'Technical_defeat/Update' , technical_defeat.Technical_defeat_Update ) ,
    path( 'Technical_defeat/Remove' , technical_defeat.Technical_defeat_Remove ) ,
    path( 'Technical_defeat/Lookup/' , technical_defeat.Technical_defeat_Lookup ) ,
    path( 'Technical_defeat/Info/' , technical_defeat.Technical_defeat_Info ) ,
    path( 'Technical_defeat/Copy' , technical_defeat.Technical_defeat_Copy ) ,

]
