from datetime import date

from django import forms
from django.forms import ValidationError

from bookkeeping import models


class EntryForm(forms.ModelForm):
    amount = forms.DecimalField(max_digits=8, decimal_places=2, label="Betrag")
    shop = forms.CharField(max_length=100, label="Shop")
    booking_date = forms.DateField(
        widget=forms.widgets.DateInput(format="%Y-%m-%d"),
        label="Buchungsdatum",
        initial=lambda: date.today().strftime("%Y-%m-%d"),
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


class SplitEntryForm(forms.ModelForm):
    def __init__(self, user, *args, num_years=5, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.num_years = num_years
        per_year = round(self.instance.amount / num_years, 2)
        difference = self.instance.amount - (per_year * num_years)
        for year in range(1, num_years + 1):
            initial_value = per_year
            if year == 1:
                initial_value += difference
            self.fields[f"year_{year}"] = forms.DecimalField(
                max_digits=8,
                decimal_places=2,
                label=f"Jahr {year}",
                initial=initial_value,
            )

    def clean(self):
        super().clean()
        total_sum = sum(self.cleaned_data.values())
        difference = abs(total_sum - self.instance.amount)
        currency = self.instance.currency
        if difference > 0:
            raise ValidationError(
                f"""Ungültige Summe: {total_sum}{currency}.
                Ursprünglicher Betrag sind {self.instance.amount}{currency}
                (Differenz {difference}{currency})"""
            )

        return self.cleaned_data

    def save(self, commit=True):
        if commit:
            self.instance.amount = self.cleaned_data.pop("year_1")
            self.instance.comment = (self.instance.comment + f"\n Abgeschrieben über {self.num_years}Jahre").strip()
            self.instance.save()
            for year, year_amount in enumerate(self.cleaned_data.values(), start=2):
                new_booking_date = date(
                    year=self.instance.booking_date.year + (year - 1),
                    month=1,
                    day=1,
                )
                new_instance = models.BookEntry(
                    user=self.user,
                    amount=year_amount,
                    currency=self.instance.currency,
                    shop=self.instance.shop + f" (Abschreibung Jahr {year})",
                    booking_date=new_booking_date,
                    type=self.instance.type,
                    comment=f"Abschreibung für Eintragung am {self.instance.booking_date.strftime('%d.%m.%Y')}",
                )
                new_instance.save()
        return super().save(commit)

    class Meta:
        model = models.BookEntry
        fields: list[str] = []


class SearchForm(forms.Form):
    term = forms.CharField(max_length=100, label="Suchbegriff", required=False)
    from_date = booking_date = forms.DateField(
        widget=forms.widgets.DateInput(format="%Y-%m-%d"), label="Von", required=False
    )
    to_date = booking_date = forms.DateField(
        widget=forms.widgets.DateInput(format="%Y-%m-%d"), label="Bis", required=False
    )
