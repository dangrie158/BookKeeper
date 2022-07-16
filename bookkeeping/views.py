from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class BookView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
