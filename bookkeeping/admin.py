from django.contrib import admin
from django.contrib.auth import models as auth_models
from django.contrib.auth.admin import UserAdmin

from bookkeeping.models import BookEntry, BusinessTrip, Receipt, TripFlatRate, User

admin.site.unregister(auth_models.Group)


class ReceiptInline(admin.TabularInline):
    model = Receipt


class BusinessTripAdmin(admin.TabularInline):
    model = BusinessTrip


class BookEntryAdmin(admin.ModelAdmin):
    inlines = [
        BusinessTripAdmin,
        ReceiptInline,
    ]


class TripFlatRateAdmin(admin.ModelAdmin):
    fields = ("rate", "valid_since")


admin.site.register(User, UserAdmin)
admin.site.register(BookEntry, BookEntryAdmin)
admin.site.register(TripFlatRate, TripFlatRateAdmin)
