# Decision Log

This document tracks key architectural and scope decisions for Job Tinder PWA.

## 2026-01-31 — Initial Scope Definition

**Decision:** Adopt MoSCoW prioritization for MVP clarity

**Context:** Need clear boundaries for MVP to avoid scope creep

**MoSCoW Breakdown:**

### Must (MVP)

**PWA Requirements:**
- Mobile-first, responsive design
- "Install optional" (can work as web app)

**Seeker Flow:**
- Onboarding + auth (email magic link or passwordless OTP)
- Profile builder
  - Basic info + work preferences
  - Questionnaire engine (multi-step, autosave)
- Scoring + stats card
  - Compute normalized stats from answers (6–10 attributes)

**Offerer Flow:**
- Dashboard with "Need for Speed-style" card UI
  - Big stats, compact bio
  - Swipe/like/dislike interaction
- Shortlist view (saved candidates)

**Admin:**
- Seed data: questions + scoring rules in code/JSON

**Privacy:**
- Offerers see candidate cards (stats), not full personal contact until shortlisted

### Should (Next Phase)

- Offerer role templates (different scoring weights per role)
- Export shortlist (CSV)
- Simple analytics events (completion rate, swipe rate)

### Could (Later)

- Psychological test libraries / validated instruments
- Team accounts + multiple offerers per org
- Matching recommendations, chat, scheduling
- CV parsing, LinkedIn import

### Won't (Explicitly Out of Scope)

- Payments/subscriptions
- Complex ATS integrations
- Full-blown psychometric certification/compliance workflows
- Public marketplace job board

---

## 2026-01-31 — Tech Stack Selection

**Decision:** FastAPI + Next.js + SQLModel

**Why:**
- FastAPI: Fast, modern, type-safe Python API framework
- Next.js: React framework with PWA support, excellent mobile performance
- SQLModel: Type-safe ORM with Pydantic integration
- Postgres: Robust relational DB for structured candidate data

**Alternatives considered:**
- Django: Too heavyweight for MVP
- Express: Preferred Python for backend consistency
- Prisma + Node: Team has stronger Python experience

---

## 2026-01-31 — Scoring Engine Design

**Decision:** JSON-driven scoring rules, computed server-side

**Why:**
- Flexibility: Change scoring without code deploys
- Security: Rules not exposed to client
- Consistency: Server ensures uniform calculation
- Future-proof: Easy to add role-specific weights

**Structure:**
```json
{
  "attributes": [
    {
      "id": "technical_skills",
      "name": "Technical Skills",
      "questions": ["q1", "q2", "q3"],
      "calculation": "weighted_average",
      "normalize": true,
      "display_order": 1
    }
  ]
}
```

**Alternatives considered:**
- Client-side computation: Rejected due to security concerns
- Hardcoded rules: Rejected due to inflexibility

---

## 2026-01-31 — Authentication Strategy

**Decision:** Passwordless (magic link or OTP) for MVP

**Why:**
- Better UX on mobile
- Reduces friction in onboarding
- One less thing to secure (no password storage)
- Sufficient for MVP privacy requirements

**Implementation notes:**
- Use email-based magic link as primary
- Consider SMS OTP as alternative
- Session management via HTTP-only cookies

---

## 2026-01-31 — Monorepo Structure

**Decision:** Simple monorepo with apps/ and packages/ folders

**Why:**
- Shared types between API and web
- Single repo for easier coordination
- No need for complex tooling (no Nx/Turborepo initially)

**Structure:**
```
/apps/api      — FastAPI backend
/apps/web      — Next.js frontend
/packages/shared — Shared types, scoring rules
/docs          — Documentation
```

---

## Template for Future Decisions

**Decision:** [Title]

**Date:** YYYY-MM-DD

**Context:** [Why this decision needed to be made]

**Decision:** [What was decided]

**Why:** [Reasoning and tradeoffs]

**Alternatives considered:** [What else was evaluated]

**Consequences:** [Impact on project]
