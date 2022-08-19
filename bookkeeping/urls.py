from django.urls import path
from django.views.generic.base import RedirectView

from bookkeeping import views

urlpatterns = [
    path("", RedirectView.as_view(url="entries/")),
    path("entries/", views.BookView.as_view(), name="entry-list"),
    path("entries/add/", views.BookEntryCreateView.as_view(), name="entry-add"),
    path("entries/add-businesstrip/", views.BusinessTripCreateView.as_view(), name="businesstrip-add"),
    path("entries/<int:pk>/", views.GenericEntryUpdateView.as_view(), name="entry-update"),
    path("entries/<int:pk>/delete/", views.BookEntryDeleteView.as_view(), name="entry-delete"),
    path("entries/<int:pk>/split/", views.EntrySplitView.as_view(), name="entry-split"),
    path("receipts/<int:pk>/delete/", views.ReceiptDeleteView.as_view(), name="receipt-delete"),
    path("summary/year/<int:year>/", views.SummaryView.as_view(), name="summary-yearly"),
    path("auth/media/", views.authenticate_media_query, name="auth-media"),
]
