from django.contrib import admin
from django.contrib.auth import models as auth_models
from django.contrib.auth.admin import UserAdmin
from polymorphic.admin import (
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
    PolymorphicParentModelAdmin,
)

from bookkeeping.models import BookEntry, BusinessTrip, Receipt, TripFlatRate, User

admin.site.unregister(auth_models.Group)


class ReceiptInline(admin.TabularInline):
    model = Receipt


@admin.register(BusinessTrip)
class BusinessTripAdmin(PolymorphicChildModelAdmin):
    base_model = BusinessTrip


@admin.register(BookEntry)
class BookEntryAdmin(PolymorphicParentModelAdmin):
    base_model = BookEntry
    child_models = (BusinessTrip,)
    inlines = (ReceiptInline,)
    list_filter = (PolymorphicChildModelFilter,)


@admin.register(TripFlatRate)
class TripFlatRateAdmin(admin.ModelAdmin):
    fields = ("rate", "valid_since")
