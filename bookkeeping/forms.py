from datetime import date
from statistics import mode
from django import forms

from bookkeeping import models


class EntryForm(forms.ModelForm):
    amount = forms.DecimalField(max_digits=8, decimal_places=2, label="Betrag")
    shop = forms.CharField(max_length=100, label="Shop")
    booking_date = forms.DateField(
        widget=forms.widgets.DateInput(format="%Y-%m-%d"),
        label="Buchungsdatum",
        initial=date.today().strftime("%Y-%m-%d"),
    )
    type = forms.ChoiceField(
        choices=models.BookEntry.EntryType.choices,
        widget=forms.RadioSelect,
        label="Typ",
        initial=models.BookEntry.EntryType.EXPENSE,
    )
    receipt = forms.FileField(label="Beleg", required=False)
    comment = forms.Textarea()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        return super().save(commit)

    class Meta:
        model = models.BookEntry
        fields = ["amount", "shop", "booking_date", "type", "comment"]


class SearchForm(forms.Form):
    term = forms.CharField(max_length=100, label="Suchbegriff", required=False)
    from_date = booking_date = forms.DateField(
        widget=forms.widgets.DateInput(format="%Y-%m-%d"), label="Von", required=False
    )
    to_date = booking_date = forms.DateField(
        widget=forms.widgets.DateInput(format="%Y-%m-%d"), label="Bis", required=False
    )
