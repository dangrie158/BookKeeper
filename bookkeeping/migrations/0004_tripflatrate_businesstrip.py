# Generated by Django 4.0.6 on 2022-08-19 18:18

from datetime import date
from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models
from django.utils import timezone


def add_initial_flatrate(apps, shema_editor):
    TripFlatRate = apps.get_model("bookkeeping", "TripFlatRate")
    TripFlatRate.objects.create(valid_since=date(year=2020, month=1, day=1), rate=0.30)


class Migration(migrations.Migration):

    dependencies = [
        ("bookkeeping", "0003_alter_bookentry_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="TripFlatRate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rate", models.DecimalField(decimal_places=2, max_digits=4, verbose_name="Preis pro Km")),
                ("valid_since", models.DateField(default=timezone.now, verbose_name="gültig Ab")),
            ],
            options={
                "verbose_name": "Kilometerpauschale",
                "verbose_name_plural": "Kilometerpauschalen",
                "ordering": ("-valid_since",),
            },
        ),
        migrations.CreateModel(
            name="BusinessTrip",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "distance",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=8,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                        verbose_name="Gefahrene Km",
                    ),
                ),
                (
                    "book_entry",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="bookkeeping.bookentry"),
                ),
            ],
            options={
                "verbose_name": "Geschäftsreise",
                "verbose_name_plural": "Geschäftsreisen",
            },
        ),
        migrations.RunPython(add_initial_flatrate, reverse_code=migrations.RunPython.noop),
    ]
