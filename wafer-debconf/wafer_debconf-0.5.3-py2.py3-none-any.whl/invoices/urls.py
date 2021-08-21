from django.conf.urls import url

from invoices.views import (
    InvoiceCancel, InvoiceCombine, InvoiceDisplay, stripe_webhook)

app_name = 'invoices'
urlpatterns = [
    url(r'^combine/$', InvoiceCombine.as_view(), name='combine'),
    url(r'^stripe-webhook/$', stripe_webhook),
    url(r'^(?P<reference_number>[^/]+)/$', InvoiceDisplay.as_view(),
        name='display'),
    url(r'^(?P<reference_number>[^/]+)/cancel/$', InvoiceCancel.as_view(),
        name='cancel'),
]
