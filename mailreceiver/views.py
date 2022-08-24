from django.conf import settings
from django.template.response import TemplateResponse

from bookkeeping.models import BookEntry
from mailreceiver.mail_parsing import DataExtractionError
from mailreceiver.models import Attachment, ParsedMail


def entry_added(request):
    entry = BookEntry.objects.filter(user=request.user).last()
    template = (
        "mail_responses/entry_added.txt" if request.GET["format"] == "text" else "mail_responses/entry_added.html"
    )
    return TemplateResponse(
        request,
        template,
        {
            "entry": entry,
            "BASE_URL": settings.BASE_URL,
        },
    )


def parsing_failed(request):
    entry = BookEntry.objects.filter(user=request.user).last()
    template = (
        "mail_responses/parsing_failed.txt" if request.GET["format"] == "text" else "mail_responses/parsing_failed.html"
    )
    attachments = [Attachment(b"", "", receipt.file.name) for receipt in entry.receipt_set.all()]
    extracted_information = ParsedMail(
        entry.amount, entry.booking_date, entry.shop, entry.comment, entry.type, attachments
    )
    parsing_errors = [
        DataExtractionError("Fehler 1"),
        DataExtractionError("Fehler 2"),
        DataExtractionError("Fehler 3"),
    ]
    return TemplateResponse(
        request,
        template,
        {
            "extracted_information": extracted_information,
            "parsing_errors": parsing_errors,
            "BASE_URL": settings.BASE_URL,
        },
    )
