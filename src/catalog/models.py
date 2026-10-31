from django.conf import settings
from django.db import models


class Book(models.Model):
    """A book in the catalog, owned by the user who created it."""

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=120)
    isbn = models.CharField(max_length=13, unique=True)
    published = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="books",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["author"])]

    def __str__(self) -> str:
        return f"{self.title} ({self.author})"
