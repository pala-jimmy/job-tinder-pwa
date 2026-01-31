# API Documentation

FastAPI backend for Job Tinder PWA.

## Overview

- **Framework:** FastAPI
- **Database:** PostgreSQL + SQLModel
- **Auth:** Passwordless (magic link / OTP)
- **Deployment:** TBD (Render, Railway, or Fly.io likely)

---

## Core Entities

### Seeker

Represents a job seeker using the platform.

```python
{
  "id": "uuid",
  "email": "string",
  "created_at": "datetime",
  "profile": {
    "name": "string",
    "bio": "string",
    "work_preferences": {
      "location": "string",
      "remote": "boolean",
      "desired_role": "string"
    }
  },
  "questionnaire_progress": {
    "completed": "boolean",
    "current_step": "integer",
    "answers": {}
  },
  "stats_card": {
    "attributes": [
      {"name": "technical_skills", "score": 8.5},
      {"name": "communication", "score": 7.2}
    ],
    "computed_at": "datetime"
  }
}
```

### Offerer

Represents a recruiter/employer using the platform.

```python
{
  "id": "uuid",
  "email": "string",
  "company": "string",
  "role_filter": "string | null",
  "created_at": "datetime"
}
```

### Swipe

Tracks offerer actions on candidate cards.

```python
{
  "id": "uuid",
  "offerer_id": "uuid",
  "seeker_id": "uuid",
  "action": "like | dislike | pass",
  "swiped_at": "datetime"
}
```

### Shortlist

Candidates saved by offerers.

```python
{
  "id": "uuid",
  "offerer_id": "uuid",
  "seeker_id": "uuid",
  "added_at": "datetime",
  "notes": "string | null"
}
```

---

## API Endpoints (Planned)

### Authentication

```
POST /auth/request-magic-link
  Body: { "email": "string" }
  Response: { "message": "Check your email" }

GET /auth/verify?token=xyz
  Response: Set session cookie, redirect to dashboard
```

### Seeker Endpoints

```
POST /seekers/register
  Body: { "email": "string" }
  Response: Seeker object

GET /seekers/me
  Auth: Required
  Response: Current seeker profile

PATCH /seekers/me/profile
  Auth: Required
  Body: { "name": "string", "bio": "string", ... }
  Response: Updated profile

POST /seekers/me/questionnaire/answer
  Auth: Required
  Body: { "question_id": "string", "answer": any }
  Response: { "saved": true, "progress": "integer" }

POST /seekers/me/compute-stats
  Auth: Required
  Response: { "stats_card": {...} }
```

### Offerer Endpoints

```
POST /offerers/register
  Body: { "email": "string", "company": "string" }
  Response: Offerer object

GET /offerers/me
  Auth: Required
  Response: Current offerer profile

GET /offerers/me/candidates
  Auth: Required
  Query: ?role_filter=optional
  Response: [ { "id": "uuid", "stats_card": {...}, "bio": "string" } ]

POST /offerers/me/swipe
  Auth: Required
  Body: { "seeker_id": "uuid", "action": "like | dislike | pass" }
  Response: { "recorded": true }

GET /offerers/me/shortlist
  Auth: Required
  Response: [ { "seeker": {...}, "added_at": "datetime" } ]

POST /offerers/me/shortlist
  Auth: Required
  Body: { "seeker_id": "uuid", "notes": "string" }
  Response: Shortlist entry
```

### Admin Endpoints

```
GET /admin/scoring-rules
  Auth: Admin required
  Response: { "rules": [...] }

POST /admin/scoring-rules
  Auth: Admin required
  Body: { "rules": [...] }
  Response: { "updated": true }

GET /admin/questions
  Auth: Admin required
  Response: [ { "id": "string", "text": "string", ... } ]
```

---

## Scoring Engine

### Rules Location

- **Definition:** `/apps/api/scoring/rules.json`
- **Loader:** `/apps/api/scoring/engine.py`

### Calculation Flow

1. Seeker completes questionnaire
2. `POST /seekers/me/compute-stats` triggered
3. Server loads scoring rules from JSON
4. For each attribute:
   - Fetch relevant question answers
   - Apply calculation (average, weighted, custom)
   - Normalize to 0-10 scale
5. Store computed stats_card in DB
6. Return stats to client

### Example Rule

```json
{
  "attribute": "problem_solving",
  "name": "Problem Solving",
  "questions": ["q5", "q12", "q18"],
  "calculation": {
    "type": "weighted_average",
    "weights": {
      "q5": 0.4,
      "q12": 0.4,
      "q18": 0.2
    }
  },
  "normalize": true,
  "display_order": 2
}
```

---

## Database Schema (SQLModel)

### seekers

```sql
id UUID PRIMARY KEY
email VARCHAR UNIQUE NOT NULL
created_at TIMESTAMP
profile JSONB
questionnaire_progress JSONB
stats_card JSONB
```

### offerers

```sql
id UUID PRIMARY KEY
email VARCHAR UNIQUE NOT NULL
company VARCHAR NOT NULL
role_filter VARCHAR
created_at TIMESTAMP
```

### swipes

```sql
id UUID PRIMARY KEY
offerer_id UUID REFERENCES offerers(id)
seeker_id UUID REFERENCES seekers(id)
action VARCHAR CHECK (action IN ('like', 'dislike', 'pass'))
swiped_at TIMESTAMP
```

### shortlists

```sql
id UUID PRIMARY KEY
offerer_id UUID REFERENCES offerers(id)
seeker_id UUID REFERENCES seekers(id)
added_at TIMESTAMP
notes TEXT
UNIQUE(offerer_id, seeker_id)
```

---

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/jobtinder

# Auth
SECRET_KEY=your-secret-key-here
MAGIC_LINK_EXPIRY=3600  # seconds

# Email (for magic links)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-api-key
FROM_EMAIL=noreply@jobtinder.app

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## Development Setup (Planned)

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Testing Strategy

- Unit tests for scoring engine
- Integration tests for auth flow
- E2E tests for critical paths (seeker onboarding, offerer swipe)
