import csv
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from bookkeeping.models import BookEntry, User


class Command(BaseCommand):
    help = "Import old Entries in csv form"

    def add_arguments(self, parser):
        parser.add_argument("file", type=Path, help="name of the file to import")
        parser.add_argument("--username", type=str, help="The username to add the bookings to", required=True)
        parser.add_argument(
            "--type",
            type=str,
            choices=[t[0] for t in BookEntry.EntryType.choices],
            help="The username to add the bookings to",
            required=True,
        )

    def handle(self, *args, **options):
        type = options["type"]
        try:
            user = User.objects.get(username=options["username"])
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"""User {options["user"]} does not exist"""))

        num_entries = 0
        sum = 0
        with open(options["file"], newline="") as csvfile:
            data_reader = csv.DictReader(csvfile)
            for row in data_reader:
                amount_str = row["Betrag"]
                if amount_str.endswith(" €"):
                    amount_str = amount_str[:-2]
                if amount_str.endswith("€"):
                    amount_str = amount_str[:-1]

                amount_str = amount_str.replace(".", "")
                amount_str = amount_str.replace(",", ".")
                amount = float(amount_str)

                booking_date = datetime.strptime(row["Datum"], "%d.%m.%Y").date()
                BookEntry.objects.create(
                    user=user,
                    amount=amount,
                    shop=row["Shop"],
                    type=type,
                    booking_date=booking_date,
                    comment=row.get("Kommentar", ""),
                )
                num_entries += 1
                sum += amount

        self.stdout.write(
            self.style.SUCCESS(f"Successfully imported {num_entries} Entries with a total of {sum:4.2f} €")
        )
