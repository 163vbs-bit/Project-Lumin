# Setup Guide

## Requirements

- Docker and Docker Compose.
- Optional local Python 3.12 for backend tests.
- Optional Node 22 for frontend development.

## Environment

Copy `.env.example` to `.env` for local overrides. Docker Compose already supplies working defaults.

## Common Commands

```bash
docker-compose up --build
docker-compose down
docker-compose exec backend pytest
docker-compose exec backend alembic revision --autogenerate -m "change"
docker-compose exec backend python -m app.db.seed
```

## Production Notes

- Replace `SECRET_KEY`.
- Use managed PostgreSQL or persistent encrypted storage.
- Serve frontend as static assets behind a reverse proxy.
- Restrict CORS origins.
- Add structured logging and metrics export before public deployment.
