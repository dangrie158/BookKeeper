import asyncio
from io import BytesIO

import dkim
from aiosmtpd.controller import UnthreadedController
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from bookkeeping.models import BookEntry, Receipt, User
from mailreceiver.mail_parsing import extract_information, get_from_addr
from mailreceiver.mail_responses import (
    send_entry_added_response,
    send_parse_failed_response,
)


class Command(BaseCommand):
    help = "Start the Mail Receiver"

    def add_arguments(self, parser):
        parser.add_argument("-H", "--host", default="127.0.0.1", type=str, help="host to listen for SMTP traffic")
        parser.add_argument("-p", "--port", default=25, type=int, help="port to listen on")

    def handle(self, *args, **options):
        host = options["host"]
        port = options["port"]

        loop = asyncio.get_event_loop()
        controller = UnthreadedController(self, host, port, loop=loop)
        controller.begin()

        self.stdout.write("Starting Event Loop", self.style.SUCCESS)
        loop.run_forever()

    def verify_message(self, envelope):
        try:
            if not dkim.verify(envelope.content):
                raise dkim.ValidationError("Ungültige DKIM Signatur.")
        except dkim.DKIMException as e:
            if settings.DEBUG:
                self.stderr.write(f"DKIM Verification failed for mail from {envelope.mail_from}.", self.style.WARNING)
                self.stderr.write(f"Continuing because DEBUG=True.", self.style.WARNING)
            else:
                raise e

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        try:
            await User.objects.aget(email=envelope.mail_from)
            envelope.rcpt_tos.append(address)
        except User.DoesNotExist:
            self.stdout.write(f"unknown user: {envelope.mail_from}. rejecting mail", self.style.NOTICE)
            return "551 Unknown Mailbox"

        return "250 OK"

    async def handle_DATA(self, server, session, envelope):
        user = await User.objects.aget(email=envelope.mail_from)
        self.stdout.write(f"Parsing mail from {envelope.mail_from}", self.style.HTTP_INFO)
        try:
            self.verify_message(envelope)
            extracted_info = extract_information(envelope.content, user)
        except dkim.ValidationError as e:
            self.stdout.write(f"{e}", self.style.ERROR)
            return "538 Need valid DKIK Signature"
        except Exception as e:
            self.stdout.write(f"{e}", self.style.ERROR)
            return "538 Error while checking DKIM Signature"

        # make sure the from user matches the envelope, since we can only verify the From header
        # using DKIM but use the envelope to find the user up until now
        try:
            from_addr = get_from_addr(extracted_info.mail_obj)
            from_user = await User.objects.aget(email=from_addr.address)
        except User.DoesNotExist:
            from_user = None
        if from_user != user:
            return "535 header From did not match sender address"

        if len(extracted_info.parsing_errors) > 0:
            self.stdout.write(f"encountered errors while parsing mail from {user.username}:", self.style.WARNING)
            for error in extracted_info.parsing_errors:
                self.stdout.write(f"\t{error}", self.style.WARNING)
            self.stdout.write("sending negative response", self.style.WARNING)
            await send_parse_failed_response(user, extracted_info)
        else:
            self.stdout.write(f"completed parsing mail from {user.username}", self.style.SUCCESS)
            self.stdout.write(
                f"creating new entry with {len(extracted_info.attachments)} attachments", self.style.SUCCESS
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

            self.stdout.write("sending confirmation", self.style.SUCCESS)
            await send_entry_added_response(entry, extracted_info)

        return "250 Message accepted for delivery"
