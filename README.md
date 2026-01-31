# Job Tinder PWA (MVP)

Two-sided PWA:
- Seekers fill profile + questionnaire → computed stats card
- Offerers swipe candidates + shortlist

## Structure
- apps/api: FastAPI + SQLite (dev) / PostgreSQL (prod) + SQLModel
- apps/web: Next.js PWA (mobile-first)
- packages/shared: shared types + scoring rules

## Backend API

### Setup
```bash
cd apps/api
python -m venv .venv
.\.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Database Migration
```bash
# Apply migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

### Seed Data
```bash
# Populate with test questionnaire and role configs
python seed.py
```

### Authentication
The API uses JWT bearer tokens for authentication:

**Register**: `POST /auth/register`
```json
{
  "email": "user@example.com",
  "password": "password123",
  "role": "seeker"  // or "offerer"
}
```

**Login**: `POST /auth/login`
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Get Current User**: `GET /auth/me`
- Requires: `Authorization: Bearer <token>` header

### Running
```bash
uvicorn main:app --reload --port 8000
# Or: python main.py
```

### Testing
```bash
python test_auth.py  # Test auth endpoints
```

## Dev (planned)
- API: ✅ Running on uvicorn (http://localhost:8000)
- Web: next dev

## Progress

### EPIC 0 — Repo + Project Hygiene ✅
- Documentation (prompts, decision-log, API spec)
- GitHub issue templates

### EPIC 1 — Backend Foundation ✅
- FastAPI skeleton with health endpoint
- SQLModel database foundation
- Alembic migrations

### EPIC 2 — Core Domain Models ✅
- User, SeekerProfile, Questionnaire system
- OffererRoleConfig, SwipeDecision, Shortlist
- Seed script with 16 questions across 6 attributes
- 3 role configurations with different weights

### EPIC 3 — Authentication ✅
- T3.1: JWT auth with email/password
  - POST /auth/register
  - POST /auth/login  
  - GET /auth/me
  - Bearer token protection
