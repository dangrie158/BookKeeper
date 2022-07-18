from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from bookkeeping.models import User, BookEntry, Receipt


class ReceiptInline(admin.TabularInline):
    model = Receipt


class BookEntryAdmin(admin.ModelAdmin):
    inlines = [
        ReceiptInline,
    ]


admin.site.register(User, UserAdmin)
admin.site.register(BookEntry, BookEntryAdmin)
