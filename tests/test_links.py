
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app
from models import Link
from rate_limiter import rate_limit
import main

# Dedicated test database
TEST_DATABASE_URL = (
    "postgresql+psycopg2://postgres:pass@localhost:5432/shortener_test"
)

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Bypass real rate limiting during tests.
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[rate_limit] = lambda: None


def setup_module():
    Base.metadata.create_all(bind=test_engine)


def teardown_module():
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


client = TestClient(app)


# 1. Root endpoint
def test_read_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello world"}


# 2. Create a short URL
def test_create_short_url():
    response = client.post(
        "/shorten",
        json={"url": "https://example.com"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["original_url"] == "https://example.com/"
    assert data["short_code"]


# 3. Create a URL with a custom alias
def test_create_custom_alias():
    response = client.post(
        "/shorten",
        json={
            "url": "https://example.org",
            "custom_alias": "my-example",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["short_code"] == "my-example"
    assert data["original_url"] == "https://example.org/"


# 4. Reject a duplicate custom alias
def test_duplicate_custom_alias():
    alias = "duplicate-test"

    first = client.post(
        "/shorten",
        json={
            "url": "https://example.com",
            "custom_alias": alias,
        },
    )

    second = client.post(
        "/shorten",
        json={
            "url": "https://example.org",
            "custom_alias": alias,
        },
    )

    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["detail"] == "This custom alias is already taken"


# 5. Retrieve an existing link
def test_get_existing_link():
    created = client.post(
        "/shorten",
        json={
            "url": "https://example.com",
            "custom_alias": "get-test",
        },
    )

    assert created.status_code == 200

    response = client.get("/links/get-test")

    assert response.status_code == 200
    assert response.json()["short_code"] == "get-test"


# 6. Return 404 for an unknown link
def test_get_missing_link():
    response = client.get("/links/does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "URL not found"


# 7. Redirect a short URL
def test_redirect_short_url():
    created = client.post(
        "/shorten",
        json={
            "url": "https://example.com",
            "custom_alias": "redirect-test",
        },
    )

    assert created.status_code == 200

    # Prevent the test from following the external redirect.
    response = client.get(
        "/redirect-test",
        follow_redirects=False,
    )

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/"


# 8. Return 404 when redirecting an unknown code
def test_redirect_missing_code():
    response = client.get(
        "/unknown-code",
        follow_redirects=False,
    )

    assert response.status_code == 404


# 9. Update an existing link
def test_update_link(monkeypatch):
    created = client.post(
        "/shorten",
        json={
            "url": "https://example.com",
            "custom_alias": "update-test",
        },
    )

    assert created.status_code == 200

    monkeypatch.setattr(main.r, "delete", lambda key: 1)

    response = client.put(
        "/links/update-test",
        json={"url": "https://example.org"},
    )

    assert response.status_code == 200
    assert response.json()["original_url"] == "https://example.org/"


# 10. Return 404 when updating an unknown link
def test_update_missing_link():
    response = client.put(
        "/links/missing-update",
        json={"url": "https://example.com"},
    )

    assert response.status_code == 404


# 11. Delete an existing link
def test_delete_link(monkeypatch):
    created = client.post(
        "/shorten",
        json={
            "url": "https://example.com",
            "custom_alias": "delete-test",
        },
    )

    assert created.status_code == 200

    monkeypatch.setattr(main.r, "delete", lambda key: 1)

    response = client.delete("/links/delete-test")

    assert response.status_code == 200
    assert response.json() == {"message": "URL deleted successfully"}

    # Confirm it was actually deleted from PostgreSQL.
    check = client.get("/links/delete-test")
    assert check.status_code == 404


# 12. Return 404 when deleting an unknown link
def test_delete_missing_link():
    response = client.delete("/links/missing-delete")

    assert response.status_code == 404


# 13. List links
def test_list_links():
    client.post(
        "/shorten",
        json={
            "url": "https://example.com",
            "custom_alias": "list-test",
        },
    )

    response = client.get("/links")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        link["short_code"] == "list-test"
        for link in response.json()
    )


# 14. Pagination returns the requested number of links
def test_pagination_limit():
    for alias in ["page-test-1", "page-test-2", "page-test-3"]:
        response = client.post(
            "/shorten",
            json={
                "url": "https://example.com",
                "custom_alias": alias,
            },
        )
        assert response.status_code == 200

    response = client.get("/links?limit=2&offset=0")

    assert response.status_code == 200
    assert len(response.json()) == 2


# 15. Pagination returns different batches
def test_pagination_offset():
    response1 = client.get("/links?limit=2&offset=0")
    response2 = client.get("/links?limit=2&offset=2")

    assert response1.status_code == 200
    assert response2.status_code == 200

    codes1 = {link["short_code"] for link in response1.json()}
    codes2 = {link["short_code"] for link in response2.json()}

    assert codes1.isdisjoint(codes2)


# 16. Reject a zero limit
def test_pagination_zero_limit():
    response = client.get("/links?limit=0")

    assert response.status_code == 422


# 17. Reject a negative offset
def test_pagination_negative_offset():
    response = client.get("/links?offset=-1")

    assert response.status_code == 422


# 18. Reject an invalid URL
def test_invalid_url():
    response = client.post(
        "/shorten",
        json={"url": "not-a-valid-url"},
    )

    assert response.status_code == 422


# 19. Reject a missing URL
def test_missing_url():
    response = client.post("/shorten", json={})

    assert response.status_code == 422
