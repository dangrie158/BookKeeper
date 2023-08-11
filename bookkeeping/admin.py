from django.contrib import admin
from django.contrib.auth import models as auth_models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from polymorphic.admin import (
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
    PolymorphicParentModelAdmin,
)

from bookkeeping.models import BookEntry, BusinessTrip, Receipt, TripFlatRate, User

admin.site.unregister(auth_models.Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


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
