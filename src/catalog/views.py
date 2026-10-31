from django.db import connection
from django.http import JsonResponse
from rest_framework import permissions, viewsets

from .models import Book
from .permissions import IsOwnerOrReadOnly
from .serializers import BookSerializer


def health(request):
    """Liveness plus a cheap database round trip."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return JsonResponse({"status": "ok"})


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Book.objects.select_related("owner")
        author = self.request.query_params.get("author")
        if author:
            queryset = queryset.filter(author__icontains=author)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
