from contextlib import suppress
from pathlib import Path
from urllib.parse import urlparse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views.generic.dates import YearArchiveView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.http.request import HttpRequest
from django.http.response import HttpResponse

from bookkeeping import models
from bookkeeping import forms


def upload_receipt_file(file: UploadedFile, entry: models.BookEntry) -> models.Receipt:
    file_name = file.name or "receipt"

    upload_path = Path(settings.MEDIA_ROOT).joinpath(models._receipt_path_for_entry(entry, file_name))
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    with open(upload_path, "wb") as saved_file:
        for chunk in file.chunks():
            saved_file.write(chunk)

    relative_path = str(upload_path.relative_to(settings.MEDIA_ROOT))
    receipt_entry = models.Receipt(file=relative_path, entry=entry)
    receipt_entry.save()
    return receipt_entry


class NoConfirmDeleteView(DeleteView):
    """This view skips the confirmation and just deletes the selected entry"""

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class BookView(LoginRequiredMixin, ListView):
    model = models.BookEntry
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        search_params = forms.SearchForm(self.request.GET)
        search_params.is_valid()

        search_terms = Q()
        if search_params.cleaned_data["from_date"] is not None:
            search_terms &= Q(booking_date__gte=search_params.cleaned_data["from_date"])

        if search_params.cleaned_data["to_date"] is not None:
            search_terms &= Q(booking_date__lte=search_params.cleaned_data["to_date"])

        if term := search_params.cleaned_data["term"]:
            search_terms &= Q(shop__icontains=term) | Q(shop__icontains=term)

        return queryset.filter(search_terms, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"search_form": forms.SearchForm(self.request.GET)})
        return context


class BookEntryCreateView(LoginRequiredMixin, CreateView):
    model = models.BookEntry
    form_class = forms.EntryForm
    success_url = reverse_lazy("entry-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        if self.request.FILES:
            kwargs.update({"files": self.request.FILES})
        return kwargs

    def form_valid(self, form: forms.EntryForm):
        response = super().form_valid(form)

        # save the receipt file to disk
        receipt_file = self.request.FILES.get("receipt")
        if receipt_file is not None:
            assert self.object is not None
            upload_receipt_file(receipt_file, self.object)

        messages.success(self.request, "Eintrag hinzugefügt")
        return response

    def form_invalid(self, form):
        return super().form_invalid(form)


class BookEntryUpdateView(LoginRequiredMixin, UpdateView):
    model = models.BookEntry
    form_class = forms.EntryForm
    success_url = reverse_lazy("entry-list")

    def get_success_url(self) -> str:
        if "upload" in self.request.POST:
            assert self.object is not None
            return reverse_lazy("entry-update", args=(self.object.id,))

        if "split" in self.request.POST:
            assert self.object is not None
            return reverse_lazy("entry-split", args=(self.object.id,))

        messages.success(self.request, "Eintrag aktualisiert")
        return reverse_lazy("entry-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def form_valid(self, form: forms.EntryForm):
        response = super().form_valid(form)

        # save the receipt file to disk
        receipt_file = self.request.FILES.get("receipt")
        if receipt_file is not None:
            assert self.object is not None
            upload_receipt_file(receipt_file, self.object)

        return response


class BookEntryDeleteView(LoginRequiredMixin, NoConfirmDeleteView):
    model = models.BookEntry
    success_url = reverse_lazy("entry-list")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Eintrag gelöscht")
        return response


class ReceiptDeleteView(LoginRequiredMixin, NoConfirmDeleteView):
    model = models.Receipt

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self) -> str:
        return reverse("entry-update", args=(self.object.entry.id,))

    def get_queryset(self):
        return super().get_queryset().filter(entry__user=self.request.user)


class EntrySplitView(LoginRequiredMixin, UpdateView):
    template_name = "bookkeeping/bookentry_split.html"
    form_class = forms.SplitEntryForm
    success_url = reverse_lazy("entry-list")

    def get_queryset(self):
        return models.BookEntry.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        num_years = 5
        with suppress(ValueError):
            num_years = int(self.request.GET.get("num_years", 5))

        kwargs.update({"user": self.request.user, "num_years": num_years})
        return kwargs


class SummaryView(LoginRequiredMixin, YearArchiveView):
    date_field = "booking_date"
    make_object_list = True
    allow_future = True

    def get_queryset(self):
        return models.BookEntry.objects.filter(user=self.request.user).order_by("booking_date")


def authenticate_media_query(request: HttpRequest):
    """
    Check if the user is allowed to access the requested files
    """
    request_uri = request.headers.get("X-Original-URI", "")
    request_parts = urlparse(request_uri)
    request_path = Path(request_parts.path)
    allowed_media_path_for_user = Path(settings.MEDIA_URL) / f"receipts/user_{request.user.id}"
    if request_path.is_relative_to(allowed_media_path_for_user):
        return HttpResponse(status=200)
    return HttpResponse(status=403)
