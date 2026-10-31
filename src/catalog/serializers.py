from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Book


class ISBNField(serializers.CharField):
    """Strips hyphens before validators run, so length and uniqueness see the stored form."""

    def to_internal_value(self, data):
        return super().to_internal_value(data).replace("-", "")


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
        # ISBN-10 may end in "X"; every other character must be a digit.
        if len(value) not in (10, 13) or not value[:-1].isdigit():
            raise serializers.ValidationError("ISBN must have 10 or 13 digits.")
        return value
