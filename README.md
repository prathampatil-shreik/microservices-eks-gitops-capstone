# MicroTask — Microservices Task Management Platform

A three-service microservices application built for Kubernetes (EKS) with Helm, GitOps and Observability.

## Services

| Service | Technology | Port |
|---------|-----------|------|
| Frontend | React + Vite + Nginx | 3000 |
| API | Python FastAPI | 8000 |
| Worker | Python background poller | — |
| Database | MySQL 8.0 | 3306 |

## Quick Start

```bash
cd application

# 1. Copy environment file
cp .env.example .env

# 2. Start everything
docker compose up --build

# 3. Open browser
# http://localhost:3000  — Frontend
# http://localhost:8000/docs  — API docs (Swagger)
```

## Architecture

```
Browser → Frontend (Nginx:80) → API (FastAPI:8000) → MySQL
                                                        ↑
                                              Worker (polls MySQL)
```

- The **frontend** serves the React SPA and proxies `/api/*` to the API via Nginx.
- The **API** handles all CRUD operations and exposes REST endpoints.
- The **worker** polls MySQL every 5 seconds for `PENDING` tasks, processes them, and updates their status.
- A one-shot **migrate** container runs Alembic migrations before the worker starts.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health + DB status |
| GET | /health/live | Kubernetes liveness probe |
| GET | /health/ready | Kubernetes readiness probe |
| GET | /api/v1/tasks | List tasks (filter, search, paginate) |
| POST | /api/v1/tasks | Create task |
| GET | /api/v1/tasks/{id} | Get task + history |
| PUT | /api/v1/tasks/{id} | Update task |
| DELETE | /api/v1/tasks/{id} | Delete task |
| GET | /api/v1/tasks/{id}/history | Task history |
| GET | /api/v1/stats | Dashboard statistics |
| GET | /metrics | Prometheus metrics |

## Running Tests

```bash
cd application

# Install test dependencies
pip install -r tests/requirements-test.txt

# Run all tests
pytest tests/ -v

# Run only API tests
pytest tests/test_tasks.py -v

# Run only health tests
pytest tests/test_health.py -v
```

## Docker Commands

```bash
# Build all images
docker compose build

# Start all services
docker compose up -d

# View logs
docker compose logs -f api
docker compose logs -f worker

# Run migrations manually
docker compose run --rm migrate

# Stop everything
docker compose down

# Stop and remove volumes (wipes MySQL data)
docker compose down -v
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| MYSQL_HOST | mysql | MySQL hostname |
| MYSQL_PORT | 3306 | MySQL port |
| MYSQL_DATABASE | microtask_db | Database name |
| MYSQL_USER | microtask_user | DB username |
| MYSQL_PASSWORD | microtask_pass | DB password |
| FAILURE_RATE | 0.1 | Worker failure rate (0.0–1.0) |
| POLL_INTERVAL_SECONDS | 5 | Worker poll interval |
| MAX_RETRIES | 3 | Max task retry attempts |

## Demonstrating Failures

Set `FAILURE_RATE=0.5` in `.env` to make 50% of tasks fail. The worker will retry up to `MAX_RETRIES` times before marking a task as `FAILED`. You can observe this in the frontend task list.

## Building Individual Images

```bash
# API
docker build -t microtask-api ./api

# Worker
docker build -t microtask-worker ./worker

# Frontend
docker build -t microtask-frontend ./frontend
```
