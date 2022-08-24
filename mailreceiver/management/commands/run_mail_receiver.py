import asyncio
from io import BytesIO

import dkim
from aiosmtpd.controller import UnthreadedController
from django.core.files import File
from django.core.management.base import BaseCommand

from bookkeeping.models import BookEntry, Receipt, User, _receipt_path_for_entry
from mailreceiver.mail_parsing import extract_information
from mailreceiver.mail_responses import (
    send_entry_added_response,
    send_parse_failed_response,
)


class Command(BaseCommand):
    help = "Start the Mail Receiver"

    def add_arguments(self, parser):
        parser.add_argument("-H", "--host", default="127.0.0.1", type=str, help="host to listen for SMTP traffic")
        parser.add_argument("-P", "--port", default=25, type=int, help="port to listen on")

    def handle(self, *args, **options):
        host = options["host"]
        port = options["port"]

        loop = asyncio.get_event_loop()
        controller = UnthreadedController(self, host, port, loop=loop)
        controller.begin()

        self.stdout.write(self.style.SUCCESS("Starting Event Loop"))
        loop.run_forever()

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        try:
            await User.objects.aget(email=envelope.mail_from)
            envelope.rcpt_tos.append(address)
        except User.DoesNotExist:
            self.stdout.write(self.style.NOTICE(f"unknown user: {envelope.mail_from}. rejecting mail"))
            return "551 Unknown Mailbox"

        return "250 OK"

    async def handle_DATA(self, server, session, envelope):
        user = await User.objects.aget(email=envelope.mail_from)
        self.stdout.write(self.style.HTTP_INFO(f"Parsing mail from {envelope.mail_from}"))
        try:
            extracted_info = extract_information(envelope.content, user)
        except dkim.ValidationError as e:
            self.stdout.write(self.style.ERROR(e))
            return "538 Need valid DKIK Signature"
        except Exception as e:
            self.stdout.write(self.style.ERROR(e))

        if len(extracted_info.parsing_errors) > 0:
            self.stdout.write(self.style.WARNING(f"encountered errors while parsing mail from {user.username}:"))
            for error in extracted_info.parsing_errors:
                self.stdout.write(self.style.WARNING(f"\t{error}"))
            self.stdout.write(self.style.WARNING("sending negative response"))
            await send_parse_failed_response(user, extracted_info)
        else:
            self.stdout.write(self.style.SUCCESS(f"completed parsing mail from {user.username}"))
            self.stdout.write(
                self.style.SUCCESS(f"creating new entry with {len(extracted_info.attachments)} attachments")
            )
            entry = await BookEntry.objects.acreate(
                user=user,
                amount=extracted_info.invoice_amount,
                shop=extracted_info.sender_name,
                booking_date=extracted_info.booking_date,
                type=extracted_info.entry_type,
                comment=extracted_info.subject,
            )
            for attachment in extracted_info.attachments:
                attachment_file = File(BytesIO(attachment.content), attachment.file_name)
                await Receipt.objects.acreate(file=attachment_file, entry=entry)

            self.stdout.write(self.style.SUCCESS("sending confirmation"))
            await send_entry_added_response(entry, extracted_info)

        return "250 Message accepted for delivery"
