from tabnanny import verbose
from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class BookEntry(models.Model):
    class EntryType(models.TextChoices):
        INCOME = ("IN", "Einnahme")
        EXPENSE = ("EX", "Ausgabe")

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Betrag")
    shop = models.CharField(max_length=100, verbose_name="Shop")
    booking_date = models.DateField(verbose_name="Buchungsdatum")
    type = models.CharField(choices=EntryType.choices, max_length=2, verbose_name="Typ")
    comment = models.TextField(verbose_name="Kommentar")

    class Meta:
        verbose_name = "Eintrag"
        verbose_name_plural = "Einträge"
        ordering = ("booking_date",)
        indexes = (models.Index(fields=("booking_date",)),)


def _user_receipt_path(instance: "Receipt", filename: str) -> str:
    # file will be uploaded to MEDIA_ROOT/user_<id>/<year>/<filename>
    book_entry = instance.entry
    return f"receipts/user_{book_entry.user.id}/{book_entry.booking_date.year}/{filename}"


class Receipt(models.Model):
    entry = models.ForeignKey(BookEntry, on_delete=models.CASCADE)
    file = models.FileField(upload_to=_user_receipt_path, verbose_name="Belegdatei")

    class Meta:
        verbose_name = "Beleg"
        verbose_name_plural = "Belege"
