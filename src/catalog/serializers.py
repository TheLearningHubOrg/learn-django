import re

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Book

# Nine digits plus a digit or "X" check character (ISBN-10), or thirteen digits (ISBN-13).
ISBN_PATTERN = re.compile(r"\d{9}[\dX]|\d{13}", re.ASCII)


class ISBNField(serializers.CharField):
    """Strips hyphens and spaces before validators run, so length and uniqueness see the stored form."""

    def to_internal_value(self, data):
        return super().to_internal_value(data).replace("-", "").replace(" ", "").upper()


class BookSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    isbn = ISBNField(
        max_length=13,
        validators=[UniqueValidator(queryset=Book.objects.all(), message="A book with this ISBN already exists.")],
    )

    class Meta:
        model = Book
        fields = ["id", "title", "author", "isbn", "published", "owner", "created_at"]
        read_only_fields = ["id", "owner", "created_at"]

    def validate_isbn(self, value: str) -> str:
        if not ISBN_PATTERN.fullmatch(value):
            raise serializers.ValidationError("ISBN must have 10 or 13 digits.")
        return value
