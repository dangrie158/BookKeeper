import os
from pathlib import Path
from typing import cast
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings

from bookkeeping import models
from bookkeeping import forms


class BookView(LoginRequiredMixin, ListView):
    template_name = "book.html"
    model = models.BookEntry
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class BookEntryCreateView(LoginRequiredMixin, CreateView):
    model = models.BookEntry
    form_class = forms.EntryForm
    success_url = reverse_lazy("entry-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form: forms.EntryForm):
        response = super().form_valid(form)

        # save the receipt file to disk
        receipt_file = cast(UploadedFile, self.request.FILES["receipt"])
        file_name = receipt_file.name or "receipt"

        upload_path = Path(settings.MEDIA_ROOT).joinpath(models._user_receipt_path(form.instance, file_name))
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        with open(upload_path, "wb") as saved_file:
            for chunk in receipt_file.chunks():
                saved_file.write(chunk)

        return response


class BookEntryUpdateView(UpdateView):
    model = models.BookEntry
    fields = ["amount", "shop", "booking_date", "type", "comment"]


class BookEntryDeleteView(DeleteView):
    model = models.BookEntry
    success_url = reverse_lazy("entry-list")
