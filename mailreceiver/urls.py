from django.urls import path
from django.views.generic.base import RedirectView

from mailreceiver import views

urlpatterns = [
    path("entry_added", views.entry_added),
    path("parsing_failed", views.parsing_failed),
]
