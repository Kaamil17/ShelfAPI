# Verkko Inventory API

MADE BY HUMANS IN EARTH :))

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
curl http://localhost:8002/
# {"message": "Healthy"}
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


### Why SQLAlchemy


### Why Redis for Rate Limiting


### Schema & Indexes


### Error Handling


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