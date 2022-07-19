from django.urls import path

from bookkeeping import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="entries/")),
    path("entries/", views.BookView.as_view(), name="entry-list"),
    path("entries/add/", views.BookEntryCreateView.as_view(), name="entry-add"),
    path("entries/<int:pk>/", views.BookEntryUpdateView.as_view(), name="entry-update"),
    path("entries/<int:pk>/delete/", views.BookEntryDeleteView.as_view(), name="entry-delete"),
    path("entries/<int:pk>/split/", views.EntrySplitView.as_view(), name="entry-split"),
    path("receipts/<int:pk>/delete/", views.ReceiptDeleteView.as_view(), name="receipt-delete"),
]
