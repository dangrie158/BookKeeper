from django.urls import path

from bookkeeping import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/accounts/profile/")),
    path("accounts/", RedirectView.as_view(url="/accounts/profile/")),
    path("accounts/profile/", views.BookView.as_view()),
]
