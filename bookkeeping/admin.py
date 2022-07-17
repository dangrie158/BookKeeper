from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from bookkeeping.models import User, BookEntry

admin.site.register(User, UserAdmin)
admin.site.register(BookEntry)
