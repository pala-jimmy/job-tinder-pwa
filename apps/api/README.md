# Job Tinder API

FastAPI backend for Job Tinder PWA.

## Setup

1. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```

2. **Activate virtual environment:**
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

## Running the Server

### Development mode (with hot reload):
```bash
uvicorn main:app --reload
```

Or using Python module:
```bash
python -m uvicorn main:app --reload
```

The API will be available at:
- **API:** http://127.0.0.1:8000
- **Interactive Docs:** http://127.0.0.1:8000/docs
- **Alternative Docs:** http://127.0.0.1:8000/redoc

### Production mode:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Database Migrations

### Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback migration:
```bash
alembic downgrade -1
```

### View migration history:
```bash
alembic history
```

## API Endpoints

### Health Check
```bash
GET /health
```

Returns API status and version information.

### Root
```bash
GET /
```

Returns API information with links to documentation.

## Configuration

Configuration is managed through environment variables in `.env`:

- `DATABASE_URL` - Database connection string (default: SQLite)
- `API_HOST` - API host (default: 0.0.0.0)
- `API_PORT` - API port (default: 8000)
- `DEBUG` - Debug mode (default: True)
- `ALLOWED_ORIGINS` - CORS origins (comma-separated)
- `SECRET_KEY` - Secret key for auth
- `MAGIC_LINK_EXPIRY` - Magic link expiration in seconds

## Database

Currently using SQLite for development (`dev.db`).

For production, update `DATABASE_URL` in `.env` to use PostgreSQL:
```
DATABASE_URL=postgresql://user:password@localhost:5432/jobtinder
```

## Models

- **Seeker** - Job seekers with profiles and questionnaire data
- **Offerer** - Recruiters/employers
- **Swipe** - Offerer actions on candidates (like/dislike/pass)
- **Shortlist** - Saved candidates

## Testing

Run tests with pytest:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Project Structure

```
apps/api/
├── alembic/              # Database migrations
│   └── versions/         # Migration files
├── models/               # SQLModel database models
│   ├── seeker.py
│   ├── offerer.py
│   ├── swipe.py
│   └── shortlist.py
├── config.py             # Configuration management
├── database.py           # Database setup and session management
├── main.py               # FastAPI application entrypoint
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (not in git)
```

## Development

The API uses:
- **FastAPI** - Modern Python web framework
- **SQLModel** - Type-safe ORM built on SQLAlchemy and Pydantic
- **Alembic** - Database migration tool
- **Pydantic Settings** - Configuration management
- **Uvicorn** - ASGI server

See `/docs/api.md` for detailed API documentation.
