from tabnanny import verbose
from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


def _user_receipt_path(instance, filename: str) -> str:
    # file will be uploaded to MEDIA_ROOT/user_<id>/<year>/<filename>
    return f"receipts/user_{instance.user.id}/{instance.booking_date.year}/{filename}"


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
    receipt = models.FileField(upload_to=_user_receipt_path, null=True, verbose_name="Belegdatei")

    def __str__(self):
        return f"{self.get_type_display()} über {self.amount}{self.currency} von {self.user}"

    class Meta:
        verbose_name = "Eintrag"
        verbose_name_plural = "Einträge"
        ordering = ("booking_date",)
        indexes = (models.Index(fields=("booking_date",)),)
