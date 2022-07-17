from django.urls import path

from bookkeeping import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", views.BookView.as_view(), name="entry-list"),
    path("entry/add/", views.BookEntryCreateView.as_view(), name="entry-add"),
    path("entry/<int:pk>/", views.BookEntryUpdateView.as_view(), name="entry-update"),
    path("entry/<int:pk>/delete/", views.BookEntryDeleteView.as_view(), name="entry-delete"),
]
