import asyncio
import smtplib
from io import BytesIO
from pathlib import Path

import dkim
from aiosmtpd.controller import UnthreadedController
from django.core.files import File
from django.core.management.base import BaseCommand

from bookkeeping.models import BookEntry, Receipt, User, _receipt_path_for_entry
from mailreceiver.mail_parsing import extract_information, get_from_addr
from mailreceiver.mail_responses import (
    send_entry_added_response,
    send_parse_failed_response,
)


class Command(BaseCommand):
    help = "Send a message to the running receiver"

    def add_arguments(self, parser):
        parser.add_argument("-H", "--host", default="127.0.0.1", type=str, help="host to send the message to")
        parser.add_argument("-p", "--port", default=25, type=int, help="port to of the target server")
        parser.add_argument("-s", "--sender", type=str, help="sender address to use")
        parser.add_argument("-t", "--receiver", type=str, help="address to send the email to")
        parser.add_argument("-f", "--file", type=Path, help="path to an .eml file to use as content")

    def handle(self, *args, **options):
        host: str = options["host"]
        port: int = options["port"]
        sender: str = options["sender"]
        receiver: str = options["receiver"]
        message_file: Path = options["file"]

        if not message_file.exists():
            self.stderr.write(f"{message_file} does not exist", self.style.ERROR)
            return

        messaage_contents = message_file.read_bytes()
        with smtplib.SMTP(host, port) as smtp:
            smtp.sendmail(sender, receiver, messaage_contents)
