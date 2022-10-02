from datetime import date
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property
from polymorphic.models import PolymorphicModel


class User(AbstractUser):
    # default email ob AbstractUser is non-unique and blankable
    email = models.EmailField(unique=True, blank=False)

    class Meta:
        verbose_name = "Benutzer"
        verbose_name_plural = "Benutzer"

    @cached_property
    def display_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name

        return self.username


class BookEntry(PolymorphicModel):
    class EntryType(models.TextChoices):
        EXPENSE = ("EX", "Ausgabe")
        INCOME = ("IN", "Einnahme")

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=False, verbose_name="Betrag")
    currency = models.CharField(max_length=3, default="€", blank=False, null=False, verbose_name="Währung")
    shop = models.CharField(max_length=100, verbose_name="Shop")
    booking_date = models.DateField(verbose_name="Buchungsdatum")
    type = models.CharField(choices=EntryType.choices, max_length=2, blank=False, null=False, verbose_name="Typ")
    comment = models.TextField(blank=True, null=False, verbose_name="Kommentar")

    @property
    def is_booked_in_future(self):
        return self.booking_date > date.today()

    @property
    def booking_month(self):
        return date(year=self.booking_date.year, month=self.booking_date.month, day=1)

    @property
    def is_businesstrip(self):
        return False

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
    def is_image(self):
        return self.file.name.endswith(("png", "jpeg", "jpg"))

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


class TripFlatRate(models.Model):
    rate = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Preis pro Km")
    valid_since = models.DateField(default=timezone.now, verbose_name="gültig Ab")

    class Meta:
        verbose_name = "Kilometerpauschale"
        verbose_name_plural = "Kilometerpauschalen"
        ordering = ("-valid_since",)

    def __str__(self):
        return f"""Pauschale seit dem {self.valid_since.strftime("%d.%m.%Y")}: {self.rate}"""


class BusinessTrip(BookEntry):
    distance = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Gefahrene Km",
        validators=(MinValueValidator(Decimal("0.01")),),
    )

    class Meta:
        verbose_name = "Geschäftsreise"
        verbose_name_plural = "Geschäftsreisen"

    def __str__(self):
        return f"""Geschäftsreise am {self.booking_date.strftime("%d.%m.%Y")} über {self.distance:3.2f}km"""

    def save(self, *args, **kwargs):
        self.amount = self.flatrate.rate * self.distance
        self.type = BookEntry.EntryType.EXPENSE
        super().save(*args, **kwargs)

    @property
    def is_businesstrip(self):
        return True

    @cached_property
    def flatrate(self):
        # the active rate is the newest rate that was valid then the trip was booked
        return TripFlatRate.objects.filter(valid_since__lte=self.booking_date).order_by("-valid_since").first()
