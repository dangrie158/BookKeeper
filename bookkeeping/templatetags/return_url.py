import urllib.parse

from django import template
from django.http.request import HttpRequest


def to_return_url(url: str, request: HttpRequest):
    returnUrl = request.get_full_path()
    return f"{url}?returnUrl={urllib.parse.quote_plus(returnUrl)}"


def with_return_url(url: str, request: HttpRequest):
    returnUrl = request.GET.get("returnUrl", "")
    return f"{url}?returnUrl={urllib.parse.quote_plus(returnUrl)}"


register = template.Library()
register.filter("to_return_url", to_return_url)
register.filter("with_return_url", with_return_url)
