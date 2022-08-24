import datetime
from collections.abc import Sequence
from email.message import EmailMessage
from typing import NamedTuple

from bookkeeping.models import BookEntry


class Attachment(NamedTuple):
    content: bytes
    content_text: str
    file_name: str


class SenderAddress(NamedTuple):
    realname: str
    address: str


class ParsedMail(NamedTuple):
    mail_obj: EmailMessage
    invoice_amount: float
    booking_date: datetime.date
    sender_name: str
    subject: str
    entry_type: BookEntry.EntryType
    attachments: list[Attachment]
    parsing_errors: Sequence[Exception]
