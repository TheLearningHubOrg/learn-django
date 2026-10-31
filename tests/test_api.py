import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from catalog.models import Book

pytestmark = pytest.mark.django_db

BOOKS_URL = "/api/v1/books/"


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def alice():
    return get_user_model().objects.create_user(username="alice")


@pytest.fixture
def bob():
    return get_user_model().objects.create_user(username="bob")


def test_health_reports_ok(api_client):
    response = api_client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_anonymous_users_can_list_books(api_client, alice):
    Book.objects.create(title="Dune", author="Frank Herbert", isbn="9780441013593", owner=alice)
    response = api_client.get(BOOKS_URL)
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["results"][0]["owner"] == "alice"


def test_anonymous_users_cannot_create(api_client):
    response = api_client.post(BOOKS_URL, {"title": "X", "author": "Y", "isbn": "9780441013593"})
    assert response.status_code == 403
    assert Book.objects.count() == 0


def test_authenticated_create_sets_owner_and_cleans_isbn(api_client, alice):
    api_client.force_authenticate(user=alice)
    payload = {"title": "Dune", "author": "Frank Herbert", "isbn": "978-0441013593"}
    response = api_client.post(BOOKS_URL, payload, format="json")
    assert response.status_code == 201
    book = Book.objects.get()
    assert book.owner == alice
    assert book.isbn == "9780441013593"


def test_invalid_isbn_is_rejected(api_client, alice):
    api_client.force_authenticate(user=alice)
    response = api_client.post(BOOKS_URL, {"title": "T", "author": "A", "isbn": "123"}, format="json")
    assert response.status_code == 400
    assert "isbn" in response.json()


def test_duplicate_isbn_is_rejected_even_with_hyphens(api_client, alice):
    Book.objects.create(title="Dune", author="Frank Herbert", isbn="9780441013593", owner=alice)
    api_client.force_authenticate(user=alice)
    payload = {"title": "Dune (again)", "author": "Frank Herbert", "isbn": "978-0-441-01359-3"}
    response = api_client.post(BOOKS_URL, payload, format="json")
    assert response.status_code == 400
    assert "isbn" in response.json()
    assert Book.objects.count() == 1


def test_only_owner_can_update(api_client, alice, bob):
    book = Book.objects.create(title="Dune", author="Frank Herbert", isbn="9780441013593", owner=alice)
    api_client.force_authenticate(user=bob)
    response = api_client.patch(f"{BOOKS_URL}{book.pk}/", {"title": "Hijacked"}, format="json")
    assert response.status_code == 403

    api_client.force_authenticate(user=alice)
    response = api_client.patch(f"{BOOKS_URL}{book.pk}/", {"title": "Dune Messiah"}, format="json")
    assert response.status_code == 200
    book.refresh_from_db()
    assert book.title == "Dune Messiah"


def test_author_filter(api_client, alice):
    Book.objects.create(title="Dune", author="Frank Herbert", isbn="9780441013593", owner=alice)
    Book.objects.create(title="Emma", author="Jane Austen", isbn="9780141439587", owner=alice)
    response = api_client.get(BOOKS_URL, {"author": "austen"})
    titles = [b["title"] for b in response.json()["results"]]
    assert titles == ["Emma"]
