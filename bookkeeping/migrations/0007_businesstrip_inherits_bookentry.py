# Generated by Django 4.1 on 2022-08-28 11:05

import django.db.models.deletion
from django.db import migrations, models


def migrate_old_trips(apps, schema_editor):
    BusinessTrip = apps.get_model("bookkeeping", "BusinessTrip")
    for old_object in BusinessTrip.objects.all():
        old_object.bookentry_ptr = old_object.book_entry
        old_object.save()


def unmigrate_old_trips(apps, schema_editor):
    BusinessTrip = apps.get_model("bookkeeping", "BusinessTrip")
    for old_object in BusinessTrip.objects.all():
        old_object.book_entry = old_object.bookentry_ptr
        old_object.save()


class Migration(migrations.Migration):
    dependencies = [
        ("bookkeeping", "0006_alter_user_email"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="businesstrip",
            name="id",
        ),
        migrations.AddField(
            model_name="businesstrip",
            name="bookentry_ptr",
            field=models.OneToOneField(
                auto_created=True,
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                null=True,
                serialize=False,
                to="bookkeeping.bookentry",
            ),
            preserve_default=False,
        ),
        migrations.RunPython(migrate_old_trips, reverse_code=unmigrate_old_trips),
        migrations.RemoveField(
            model_name="businesstrip",
            name="book_entry",
        ),
        migrations.AlterField(
            model_name="businesstrip",
            name="bookentry_ptr",
            field=models.OneToOneField(
                auto_created=True,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="bookkeeping.bookentry",
            ),
        ),
    ]
