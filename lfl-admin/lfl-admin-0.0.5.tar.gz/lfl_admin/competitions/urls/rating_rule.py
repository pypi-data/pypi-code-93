from django.urls import path

from lfl_admin.competitions.views import rating_rule

urlpatterns = [

    path( 'Rating_rule/Fetch/' , rating_rule.Rating_rule_Fetch ) ,
    path( 'Rating_rule/Add' , rating_rule.Rating_rule_Add ) ,
    path( 'Rating_rule/Update' , rating_rule.Rating_rule_Update ) ,
    path( 'Rating_rule/Remove' , rating_rule.Rating_rule_Remove ) ,
    path( 'Rating_rule/Lookup/' , rating_rule.Rating_rule_Lookup ) ,
    path( 'Rating_rule/Info/' , rating_rule.Rating_rule_Info ) ,
    path( 'Rating_rule/Copy' , rating_rule.Rating_rule_Copy ) ,

]
