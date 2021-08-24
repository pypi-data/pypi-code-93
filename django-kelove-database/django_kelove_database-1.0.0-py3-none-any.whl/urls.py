"""
urls.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 2/2/21 11:25 AM
"""

from django.urls import path

from .apps import DjangoKeloveDatabaseConfig
from .views import ckfinder, ckfinder_api

app_name = DjangoKeloveDatabaseConfig.name

urlpatterns = [
    # ckfinder
    path('ckfinder/', ckfinder, name='ckfinder'),
    path('ckfinder-api/', ckfinder_api, name='ckfinder_api'),
]
