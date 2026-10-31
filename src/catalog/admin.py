from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn", "owner", "created_at")
    search_fields = ("title", "author", "isbn")
    list_select_related = ("owner",)
