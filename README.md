# Verkko Inventory API

MADE BY HUMANS ON EARTH :))

A FastAPI-based inventory management API backed by PostgreSQL, with Redis-powered rate limiting.

## Stack

- **Python 3.11** / FastAPI
- **PostgreSQL 16** — primary datastore
- **Redis 7** — rate limiting
- **SQLAlchemy 2 (async)** + asyncpg
- **Alembic** — database migrations

---

## Running with Docker (recommended)

### Prerequisites

- Docker + Docker Compose

### 1. Configure environment

All configuration is read from `backend.env` in the project root. A working example:

```env
DEBUG=True
LOG_LEVEL=INFO

DB_HOST=db
DB_PORT=5432
DB_NAME=verkko
DB_USER=verkko
DB_PASSWORD=verkko

POSTGRES_USER=verkko
POSTGRES_PASSWORD=verkko
POSTGRES_DB=verkko

REDIS_HOST=redis
REDIS_PORT=6379
```

### 2. Start all services

```bash
docker-compose up --build
```

This starts three containers: `verkko-api` (port 8002), `db` (PostgreSQL), and `redis`.

### 3. Run migrations

In a separate terminal, once the containers are up:

```bash
cd backend
alembic upgrade head
```

### 4. Verify

```bash
curl http://localhost:8002/health
# {"db": "ok", "redis": "ok"}
```

API docs available at: `http://localhost:8002/docs`

---

## Running Locally (without Docker)

### Prerequisites

- Python 3.11
- PostgreSQL running locally
- Redis running locally

### 1. Create and activate virtual environment

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows (Git Bash)
source .venv/bin/activate       # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Configure environment

Create a `.env` file in the project root (or edit `backend.env`) with your local DB and Redis credentials:

```env
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=verkko
DB_USER=verkko
DB_PASSWORD=verkko

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

### 4. Run migrations

```bash
cd backend
alembic upgrade head
```

### 5. Start the server

```bash
uvicorn backend.main:app --reload --port 8002
```

---

## API Endpoints

Base URL: `http://localhost:8002/api`

### `GET /health`

Checks if the API, database, and Redis are all reachable.

**Response:** `200 OK` (all healthy) or `503 Service Unavailable` (something is down)
```json
{"db": "ok", "redis": "ok"}
```

---

### `POST /api/inventory/update`

Bulk insert inventory items.

**Rate limit:** 10 requests/minute per IP

**Request body:**
```json
{
  "items": [
    {
      "productid": "ABC-123",
      "quantity": 50,
      "timestamp": "2024-01-01T10:00:00"
    }
  ]
}
```

**Response:** `201 Created` (no body)

---

### `GET /api/inventory/query`

Query inventory records for a product with optional date range and pagination.

**Rate limit:** 30 requests/minute per IP

**Query parameters:**

| Parameter        | Required | Default | Description                        |
|------------------|----------|---------|------------------------------------|
| `productid`      | Yes      | —       | Product ID to query                |
| `starttimestamp` | No       | —       | Filter records from this timestamp |
| `endtimestamp`   | No       | —       | Filter records up to this timestamp|
| `limit`          | No       | 50      | Page size (max 500)                |
| `offset`         | No       | 0       | Number of records to skip          |

**Example:**
```bash
curl "http://localhost:8002/api/inventory/query?productid=ABC-123&limit=100&offset=0"
```

**Response:** `200 OK`
```json
{
  "count": 2,
  "limit": 100,
  "offset": 0,
  "items": [
    {
      "id": 1,
      "productid": "ABC-123",
      "quantity": 50,
      "timestamp": "2024-01-01T10:00:00"
    }
  ]
}
```

---

## Project Structure

```
VerkkoApi/
├── backend/
│   ├── alembic/            # Migration files
│   ├── core/
│   │   └── config.py       # pydantic-settings config (reads backend.env)
│   ├── inventory/
│   │   ├── router.py       # Route handlers
│   │   ├── service.py      # Business logic
│   │   ├── repository.py   # Database access (SQLAlchemy only)
│   │   ├── models.py       # ORM models
│   │   ├── schemas.py      # Pydantic request/response schemas
│   │   ├── dependencies.py # get_db_session FastAPI dependency
│   │   ├── exceptions.py   # Custom error classes
│   │   └── exception_handlers.py
│   ├── main.py             # App factory, lifespan, middleware
│   └── requirements.txt
├── docker-compose.yml
├── backend.env
└── README.md
```

---

## Design Decisions

### Why FastAPI

Honestly, part of the motivation was simply a good opportunity to try a framework I'd been curious about, 
and given the nature of this task, it made sense.
Coming from Django, most of the concepts transferred quickly: migrations, project structure, request lifecycle.
The main adjustment was SQLAlchemy over Django ORM, which didn't take long to get comfortable with.

The async database communication was immediately noticeable. For an I/O bound service like this one, not blocking on every
database call feels like the right default rather than something you have to opt into.

The biggest surprise was Pydantic. From automatically pulling environment variables into typed settings, to validating 
incoming requests, to giving my IDE full type awareness throughout the codebase — it genuinely changed how the code feels to write.
And the free Swagger UI as a side effect of just defining schemas is something I won't be able to go back from.
In Django I was maintaining separate schema definitions just to get that documentation. Here it's just there.

Five hours in and already enjoying it — good sign yaay!! :).

### Why SQLAlchemy
Honestly, most of my ORM experience is with Django ORM, so SQLAlchemy was relatively new territory here.
But it was the right call for one fundamental reason: async support. Django ORM's async story is still catching up,
and for a service where every request waits on the database, non-blocking queries aren't a nice-to-have.

Beyond that, a few things stood out. The separation between the ORM layer and the core expression language gives you
more control when you need it — you're not fighting the abstraction when a query gets complex. 

The session and connection pool management is also very explicit, which I actually prefer over magic , you know exactly when a connection is opened, used, and returned to the pool.

It's more verbose than Django ORM, but that verbosity is mostly transparency. You always know what's happening. Early to say but great tool.


### Why Redis for Rate Limiting
When building for 1,000 users, I'm already thinking about 10,000. A service should handle traffic spikes gracefully rather
than fall over under load — rate limiting is what keeps it sane when things get busy.
Redis was the natural choice here and honestly I just love working with it. 

It's easy to configure, the API is dead simple, and everything happens in nanoseconds — when you're tracking request counts per user per second, that speed matters.
An in-memory counter that responds faster than your database can even blink at the connection is exactly what you want sitting in front of your API, so Redis all the way.
And also that i can share the state accross my infra.

### Schema & Indexes
I love database and i always loved to understand what happens under the hood.

PostgreSQL uses B-tree indexes so a million row table needs ~20 comparisons instead of a full scan.

The query pattern here is always "product X within this time range", so a composite index on (productid, timestamp) does the job;
productid first to jump straight to that product, timestamp second for the range scan. 
Column order matters here; flip them and the index becomes far less effective.

Trade-off is every insert also updates the tree, so writes get slightly slower.
For a service that queries far more than it writes, easy call.


### Error Handling
Working in a system with poor error handling is like navigating a desert without a compass.
It's not just about catching exceptions — it's about making sure every failure tells you exactly what went wrong and where.

I treat error handling as a communication tool. When something breaks, the response should be useful to the frontend developer consuming the API, not just meaningful to the server logs.
A clear error shape with a consistent structure means less back and forth between frontend and backend trying to diagnose what actually failed.

Every error in this service returns the same predictable format — a message, an optional field-level detail, and a request ID that can be traced through the logs. 

---


---
Based on what's already built, there are the honest gaps: 

Security gaps:

- HTTPS enforcement, it is plain http now.
- API key or JWT authentication, currently anyone can hit the endpoint.
- a better (token based) rete limiter so it cannot be bypassesd with a proxy
---

---
Logs and Alert system: 

- For production I would route logs directly to CloudWatch using Docker's AWS logs driver no need for mounted volumes,
  no log shipping agent, the container just writes and CloudWatch receives it.
 
- Then on top of that, CloudWatch subscription filter watching for error patterns connected to an SNS topic 
  so the moment something breaks in production, you get notified immediately rather than finding out from a user report.

---


---
APi versioning
- Versioning (/api/v1/) so breaking changes can be introduced without affecting existing clients
---

## Migrations

```bash
cd backend

# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "description"

# Roll back one migration
alembic downgrade -1
```