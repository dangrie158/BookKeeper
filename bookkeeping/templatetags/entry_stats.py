from itertools import zip_longest
from typing import Iterable, NamedTuple
from django import template

from bookkeeping.models import BookEntry


def entry_sum(entries: Iterable[BookEntry], entry_type: str | None = None):
    print("Mark" * 40)
    print(entries)
    if entry_type is not None:
        entries = filter(lambda e: e.type == entry_type, entries)

    entry_amounts = map(lambda e: -e.amount if e.type == "EX" else e.amount, entries)
    return sum(entry_amounts)


class EntryPair(NamedTuple):
    in_entry: BookEntry
    ex_entry: BookEntry


def zip_entries(group: Iterable[BookEntry]):
    in_entries = filter(lambda e: e.type == "IN", group)
    ex_entries = filter(lambda e: e.type == "EX", group)

    for entry_pair in zip_longest(in_entries, ex_entries):
        yield EntryPair(*entry_pair)


register = template.Library()
register.filter("entry_sum", entry_sum)
register.filter("zip_entries", zip_entries)
