import email.message
import email.parser
import email.policy
import email.utils
import itertools
import re
from datetime import datetime
from io import BytesIO
from typing import cast

import dkim
import PyPDF2
from PyPDF2.errors import PdfReadError

from bookkeeping.models import BookEntry, User
from mailreceiver.models import Attachment, ParsedMail, SenderAddress

policy = email.policy.EmailPolicy(utf8=True)
parser = email.parser.BytesParser(policy=policy)


class DataExtractionError(Exception):
    pass


def get_from_addr(mail_obj: email.message.Message) -> SenderAddress:
    return SenderAddress(*email.utils.parseaddr(mail_obj["From"]))


def extract_invoice_amount_candidates(text_content: str) -> list[float]:
    currency_affix = r"\s*(?:€|EUR)\s*"
    # forced decimal is a number that stands on its own (has a whitespace before and after)
    # and MUST contain a decimal separator and 2 decimals
    forced_decimal = r"\d+[.,]\d{2}\D"
    amount_regex = "|".join(
        [
            rf"""(?:{currency_affix}({forced_decimal}))""",
            rf"""(?:({forced_decimal}){currency_affix})""",
            rf"""\s+({forced_decimal})\s+""",
        ]
    )

    all_amount_candidates_in_document = []
    for match in re.finditer(amount_regex, text_content, re.MULTILINE):
        for group in match.groups():
            if group:
                amount_str = group.replace(",", ".")
                amount = abs(float(amount_str))
                all_amount_candidates_in_document.append(amount)

    return all_amount_candidates_in_document


def extract_text(data: bytes | str, content_type: str) -> str:
    match content_type:
        case "application/pdf":
            assert isinstance(data, bytes)
            try:
                pdf_stream = BytesIO(data)
                pdf_reader = PyPDF2.PdfReader(pdf_stream)
            except PdfReadError:
                return ""
            return " ".join(page.extract_text() for page in pdf_reader.pages)
        case "text/plain":
            assert isinstance(data, str)
            return data
        case _:
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            return data


def extract_email_senders(email_body: str) -> list[SenderAddress]:
    sender_regex = r"""(?:Von|From): (?P<realname>.*)<(?P<address>[\w@_-]+)\..*>"""

    all_found_addresses = []
    for match in re.finditer(sender_regex, email_body, re.MULTILINE):
        name_str = match.group("realname").strip()
        address_str = match.group("address").strip()
        address = SenderAddress(name_str, address_str)
        all_found_addresses.append(address)

    return all_found_addresses


def extract_attachments(mail_obj: email.message.Message) -> list[Attachment]:
    attachments: list[Attachment] = []
    for part in mail_obj.walk():
        part = cast(email.message.MIMEPart, part)

        is_attachment = part.get_content_maintype() == "application" and part.get_content_disposition() in (
            "inline",
            "attachment",
        )

        if not is_attachment:
            continue

        filename = part.get_filename()
        if filename is None:
            filename = f"Belegdatei_{len(attachments):02d}"

        attachment_content = part.get_content()
        attachment_text = extract_text(attachment_content, part.get_content_type())
        attachment = Attachment(attachment_content, attachment_text, filename)
        attachments.append(attachment)

    return attachments


def get_subject_without_prefixes(mail_obj: email.message.Message) -> str:
    all_prefixes = ("Fwd:", "Fw:", "Aw:", "Re:")
    subject = mail_obj.get("Subject", "")
    for prefix in all_prefixes:
        subject = subject.replace(prefix, "").strip()

    return subject


def get_booking_type(mail_body: str) -> BookEntry.EntryType:
    income_tokens = ("Auszahlungsbetrag", "Auszahlung", "Gutschrift")
    for token in income_tokens:
        if token in mail_body:
            return BookEntry.EntryType.INCOME
    return BookEntry.EntryType.EXPENSE


def extract_information(contents: bytes, user: User) -> ParsedMail:
    parsing_errors = []

    mail_obj = cast(email.message.MIMEPart, parser.parsebytes(contents))

    subject = get_subject_without_prefixes(mail_obj)
    body = mail_obj.get_body(preferencelist=("plain", "related", "html"))
    body = cast(email.message.MIMEPart, body)
    if body is None:
        parsing_errors.append(DataExtractionError("Kein guter Mail Text Kandidat gefunden."))
        body_text = ""
    else:
        body_text = extract_text(body.get_content(), body.get_content_type())

    attachments = extract_attachments(mail_obj)

    # append the mail itself as a last attachment
    mail_attachment = Attachment(mail_obj.as_bytes(), body_text, f"{subject}.eml")
    attachments.append(mail_attachment)

    # find all strings that are potential amounts and select the largest
    amount_candidates: list[float] = list(
        itertools.chain(*[extract_invoice_amount_candidates(attachment.content_text) for attachment in attachments])
    )
    # filter out improbably high amounts
    amount_candidates = [amount for amount in amount_candidates if amount <= 3_000.00]
    invoice_amount = max((*amount_candidates, 0))
    if invoice_amount == 0:
        parsing_errors.append(DataExtractionError(f"Konnte keine plausiblen Rechnungbetrag finden."))

    # add all senders from the headers
    potential_senders = []
    for sender_header in mail_obj.get_all("From"):
        potential_senders += extract_email_senders(f"From: {sender_header}")
    potential_senders += extract_email_senders(body_text)
    potential_senders = [sender for sender in potential_senders if not user.email in sender.address]

    if len(potential_senders) == 0:
        parsing_errors.append(DataExtractionError("Konnte Name des Senders nicht bestimmen."))
        sender_name = "<unbekannt>"
    else:
        # take the last potential sender, that is the first that wrote an email in the chain
        sender = potential_senders[-1]
        sender_name = sender.realname if sender.realname else sender.address

    mail_timestamp = email.utils.parsedate_to_datetime(mail_obj["Date"])
    if mail_timestamp is None:
        mail_timestamp = datetime.now()
    booking_date = mail_timestamp.date()

    subject = get_subject_without_prefixes(mail_obj)

    entry_type = get_booking_type(body_text)

    return ParsedMail(
        cast(email.message.EmailMessage, mail_obj),
        invoice_amount,
        booking_date,
        sender_name,
        subject,
        entry_type,
        attachments,
        parsing_errors,
    )
