# URL Shortener — Backend Service

A containerized URL shortener backend built with **FastAPI, PostgreSQL, Redis, and Docker**. The service allows users to create short URLs, manage existing links, and redirect users through generated short codes.

The project focuses on backend engineering concepts such as REST API development, database management, caching, rate limiting, pagination, and containerized application deployment.

## Features

- **URL Shortening:** Generate unique short codes using Base62 encoding.
- **Custom Aliases:** Allow users to provide custom short codes.
- **URL Redirection:** Redirect users to the original URL using the generated short code.
- **CRUD Operations:** Create, retrieve, update, and delete shortened URLs.
- **Redis Caching:** Cache frequently accessed URLs to reduce database queries.
- **Cache Invalidation:** Remove outdated cache entries when a URL is updated or deleted.
- **Rate Limiting:** Limit URL creation requests to 5 requests per IP address within a 60-second window.
- **Pagination:** Support limit and offset-based pagination when retrieving stored links.
- **Database Migrations:** Manage database schema changes using Alembic.
- **Containerization:** Run the application, PostgreSQL, and Redis using Docker Compose.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API framework |
| SQLAlchemy | ORM and database interaction |
| PostgreSQL | Persistent database |
| Redis | Caching and rate limiting |
| Alembic | Database migrations |
| Docker | Application containerization |
| Docker Compose | Multi-container orchestration |
| Pydantic | Request validation and settings |

## Architecture

The application uses a containerized architecture consisting of three main services.

```text
                 Client
                   |
                   v
             FastAPI App
                   |
          +--------+--------+
          |                 |
          v                 v
       Redis            PostgreSQL
     (Cache &          (Persistent
   Rate Limiting)        Storage)
```

**Request flow:**

1. The client sends an HTTP request to the FastAPI application.
2. For URL creation, Redis checks and enforces the rate limit.
3. The application generates a short code and stores the URL in PostgreSQL.
4. For redirection, the application first checks Redis for a cached URL.
5. On a cache miss, it retrieves the original URL from PostgreSQL and caches it in Redis.
6. The client receives an HTTP redirect to the original URL.

## Project Structure

```text
url-shortener/
│
├── main.py
├── models.py
├── schemas.py
├── database.py
├── config.py
├── cache.py
├── rate_limiter.py
│
├── routers/
│
├── tests/
│
├── alembic/
│   └── versions/
│
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Docker
- Docker Compose
- Git

### 1. Clone the repository

```bash
git clone https://github.com/AdwaitPalsule/URL_SHORTENER.git

cd URL_SHORTENER
```

### 2. Build and start the services

```bash
docker compose up --build -d
```

This starts three services:

- **App:** FastAPI backend running on port 8000.
- **Database:** PostgreSQL 16.
- **Cache:** Redis 7.

Docker Compose manages the services and their internal network communication.

### 3. Run database migrations

After the containers are healthy, execute:

```bash
docker compose exec app /app/.venv/bin/alembic upgrade head
```

This applies the database migrations and creates the required tables.

### 4. Access the API

The application will be available at:

```text
http://localhost:8000
```

Interactive Swagger documentation:

```text
http://localhost:8000/docs
```

You can use Swagger UI to explore and test the API endpoints.

### 5. Stop the services

```bash
docker compose down
```

To stop the services and remove the associated named volumes as well:

```bash
docker compose down -v
```

**Warning:** The second command removes the PostgreSQL data volume.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Root endpoint |
| POST | `/shorten` | Create a shortened URL |
| GET | `/links` | Retrieve shortened URLs with pagination |
| GET | `/links/{code}` | Retrieve URL metadata |
| PUT | `/links/{code}` | Update the original URL |
| DELETE | `/links/{code}` | Delete a shortened URL |
| GET | `/{code}` | Redirect to the original URL |

### Example: Create a Short URL

**Request**

```http
POST /shorten
Content-Type: application/json
```

```json
{
  "url": "https://www.example.com",
  "custom_alias": "example"
}
```

**Example response**

```json
{
  "short_code": "example",
  "original_url": "https://www.example.com/"
}
```

The exact response fields depend on the API response schema.

### Example: URL Redirection

```http
GET /example
```

The application looks up the short code and redirects the client to the original URL.

### Example: Pagination

```http
GET /links?limit=10&offset=0
```

- `limit`: Maximum number of records to retrieve (default 10, maximum 100).
- `offset`: Number of records to skip (default 0).

## Redis Implementation

Redis is used for two primary purposes.

### 1. URL Caching

The application implements a cache-aside pattern.

- Check Redis for the requested short code.
- If found, return the cached original URL.
- If not found, query PostgreSQL.
- Store the retrieved URL in Redis with a TTL of 300 seconds.
- Invalidate the cache when a URL is updated or deleted.

### 2. Rate Limiting

The `/shorten` endpoint uses Redis to track requests by client IP address.

- Each request increments a Redis counter.
- The counter expires after 60 seconds.
- Requests exceeding 5 within the window receive HTTP `429 Too Many Requests`.

## Database Management

PostgreSQL stores shortened URL records.

The database is managed through SQLAlchemy ORM models, while Alembic handles schema migrations.

The URL records include:

- `id`
- `original_url`
- `short_code`
- `created_at`
- `expires_at`

The `expires_at` field is nullable and reserved for expiration functionality.

## Future Improvements

- Implement URL expiration and automatic expiry handling.
- Expand automated test coverage using Pytest.
- Add click analytics and background processing.
- Introduce authentication and user-specific URL management.
- Add monitoring, logging, and performance testing.
- Deploy the application to a cloud platform.

## Learning Outcomes

Through this project, I explored and implemented:

- REST API design using FastAPI.
- Relational database integration using SQLAlchemy.
- Database migrations with Alembic.
- Redis caching and cache invalidation.
- Redis-based rate limiting.
- Pagination and CRUD operations.
- Docker images, containers, and multi-service orchestration.
- Container networking, environment configuration, and persistent volumes.

## Author

**Adwait Palsule**

GitHub: [AdwaitPalsule](https://github.com/AdwaitPalsule)

LeetCode: [Adwait Palsule](https://leetcode.com/u/AdwaitPalsule/)
