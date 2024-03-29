# Generated by Django 4.1 on 2022-08-28 11:45

import django.db.models.deletion
from django.db import migrations, models


def set_ctype_for_polymorphic(apps, schema_editor):
    BookEntry = apps.get_model("bookkeeping", "BookEntry")
    BusinessTrip = apps.get_model("bookkeeping", "BusinessTrip")
    ContentType = apps.get_model("contenttypes", "ContentType")

    book_entry_ct = ContentType.objects.get_for_model(BookEntry)
    business_trip_ct = ContentType.objects.get_for_model(BusinessTrip)
    BookEntry.objects.filter(polymorphic_ctype__isnull=True, businesstrip__isnull=True).update(
        polymorphic_ctype=book_entry_ct
    )
    BookEntry.objects.filter(polymorphic_ctype__isnull=True, businesstrip__isnull=False).update(
        polymorphic_ctype=business_trip_ct
    )


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("bookkeeping", "0007_businesstrip_inherits_bookentry"),
    ]

    operations = [
        migrations.AddField(
            model_name="bookentry",
            name="polymorphic_ctype",
            field=models.ForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="polymorphic_%(app_label)s.%(class)s_set+",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.RunPython(set_ctype_for_polymorphic, reverse_code=migrations.RunPython.noop),
    ]
