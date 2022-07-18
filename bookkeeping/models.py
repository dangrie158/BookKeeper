from datetime import date
from pathlib import Path
from tabnanny import verbose
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.conf import settings

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class BookEntry(models.Model):
    class EntryType(models.TextChoices):
        EXPENSE = ("EX", "Ausgabe")
        INCOME = ("IN", "Einnahme")

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Betrag")
    currency = models.CharField(max_length=3, default="€", verbose_name="Währung")
    shop = models.CharField(max_length=100, verbose_name="Shop")
    booking_date = models.DateField(verbose_name="Buchungsdatum")
    type = models.CharField(choices=EntryType.choices, max_length=2, verbose_name="Typ")
    comment = models.TextField(blank=True, verbose_name="Kommentar")

    @property
    def is_booked_in_future(self):
        return self.booking_date > date.today()

    @property
    def booking_month(self):
        return date(year=self.booking_date.year, month=self.booking_date.month, day=1)

    def __str__(self):
        return f"{self.get_type_display()} über {self.amount}{self.currency} von {self.user}"

    class Meta:
        verbose_name = "Eintrag"
        verbose_name_plural = "Einträge"
        ordering = ("-booking_date",)
        indexes = (models.Index(fields=("booking_date",)),)


def _receipt_path_for_entry(entry: BookEntry, filename: str) -> str:
    # file will be uploaded to MEDIA_ROOT/user_<id>/<year>/<filename>
    original_filename_candidate = Path(f"receipts/user_{entry.user.id}/{entry.booking_date.year}/{entry.id}/{filename}")
    unique_filename = original_filename_candidate
    suffix = 0
    while (Path(settings.MEDIA_ROOT) / unique_filename).exists():
        suffix += 1
        unique_filename = original_filename_candidate.with_name(f"{original_filename_candidate.stem}_{suffix:02d}")
    return str(unique_filename)


def _receipt_path_for_receipt(receipt: "Receipt", filename: str):
    return _receipt_path_for_entry(receipt.entry, filename)


class Receipt(models.Model):
    file = models.FileField(
        upload_to=_receipt_path_for_receipt,
        null=True,
        verbose_name="Belegdatei",
    )
    entry = models.ForeignKey(BookEntry, on_delete=models.CASCADE)

    @property
    def is_pdf(self):
        return self.file.name.endswith("pdf")

    @property
    def file_name(self):
        return Path(self.file.name).name

    def __str__(self):
        return f"Beleg für {self.entry}"

    class Meta:
        verbose_name = "Beleg"
        verbose_name_plural = "Belege"


@receiver(pre_delete, sender=Receipt)
def remove_files(sender, instance, using, **kwargs):
    instance.file.delete()
