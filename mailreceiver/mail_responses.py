from email.message import EmailMessage

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from bookkeeping.models import BookEntry, User
from mailreceiver.models import ParsedMail

DEFAULT_FROM_EMAIL = f"Book Keeper <mailreader@{settings.HOSTNAME}>"


def _create_message(
    subject: str,
    txt_content: str,
    html_content: str,
    user: User,
    in_reponse_to: EmailMessage | None,
) -> EmailMultiAlternatives:
    headers = {}
    if in_reponse_to is not None and "Message-ID" in in_reponse_to:
        headers["In-Response-To"] = in_reponse_to["Message-ID"]
        headers["References"] = in_reponse_to["Message-ID"]

    email = EmailMultiAlternatives(
        subject=subject,
        body=txt_content,
        from_email=DEFAULT_FROM_EMAIL,
        to=[user.email],
        headers=headers,
    )
    email.attach_alternative(html_content, "text/html")

    return email


@sync_to_async
def send_entry_added_response(entry: BookEntry, extracted_information: ParsedMail):
    context = {
        "entry": entry,
        "extracted_information": extracted_information,
        "BASE_URL": settings.BASE_URL,
        "MEDIA_URL": settings.MEDIA_URL,
        "user": entry.user,
    }

    html_content = render_to_string("mail_responses/entry_added.html", context)
    txt_content = render_to_string("mail_responses/entry_added.txt", context)
    subject = f"Eintrag über {entry.amount:4.2f}€ für {entry.shop} hinzugefügt"

    email = _create_message(subject, txt_content, html_content, entry.user, extracted_information.mail_obj)

    email.send(fail_silently=not settings.DEBUG)


@sync_to_async
def send_parse_failed_response(user: User, extracted_information: ParsedMail):
    context = {
        "extracted_information": extracted_information,
        "BASE_URL": settings.BASE_URL,
        "MEDIA_URL": settings.MEDIA_URL,
        "user": user,
    }

    html_content = render_to_string("mail_responses/parsing_failed.html", context)
    txt_content = render_to_string("mail_responses/parsing_failed.txt", context)
    subject = f"Eintrag konnte nicht hinzugefügt werden"

    email = _create_message(subject, txt_content, html_content, user, extracted_information.mail_obj)
    email.send(fail_silently=not settings.DEBUG)
