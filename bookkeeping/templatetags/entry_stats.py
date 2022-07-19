from typing import Optional
from django import template
from django.template.defaulttags import GroupedResult


def entry_sum(group: GroupedResult, entry_type: str | None = None):
    entries = group.list
    if entry_type is not None:
        entries = filter(lambda e: e.type == entry_type, entries)
    return sum([entry.amount for entry in entries])


register = template.Library()
register.filter("entry_sum", entry_sum)
