# Prompts Template

This document contains prompt templates for working with AI assistants on this project.

## Project Context Prompt

```
You are working on Job Tinder PWA - a two-sided recruitment platform:
- Seekers fill profile + questionnaire → computed stats card
- Offerers swipe candidates + shortlist

Tech Stack:
- apps/api: FastAPI + Postgres + SQLModel
- apps/web: Next.js PWA (mobile-first)
- packages/shared: shared types + scoring rules

Key Principles:
- Mobile-first responsive design
- JSON-driven scoring rules
- Privacy-focused (offerers see stats cards, not full contact until shortlist)
- Autosave questionnaire progress
```

## Feature Development Prompt

```
Context: Job Tinder PWA [Component: {api/web/shared}]

Task: {describe feature}

Requirements:
- Follow existing patterns in {relevant directory}
- Update shared types if needed
- Consider mobile UX
- Test with seeker/offerer perspective

Constraints:
- MVP scope (see decision-log.md)
- No payments, no ATS integrations
- JSON-driven configuration
```

## Bug Fix Prompt

```
Context: Job Tinder PWA

Issue: {describe bug}
Component: {api/web/shared}
Steps to reproduce: {list steps}
Expected: {expected behavior}
Actual: {actual behavior}

Environment:
- OS: {OS}
- Browser: {browser if web issue}
- Python version: {version if api issue}
```

## Code Review Prompt

```
Please review this code for:
1. Mobile responsiveness (web components)
2. Type safety (shared types usage)
3. Privacy considerations (data exposure)
4. Performance (especially questionnaire autosave)
5. Consistency with MVP scope

Code:
{paste code}
```

## Scoring Rules Design Prompt

```
Context: Job Tinder PWA scoring engine

Design a scoring rule for: {attribute name}

Requirements:
- JSON-serializable structure
- Normalization to 0-10 scale
- Clear mapping from questionnaire answers
- Consider role-specific weights (future)

Example format:
{
  "attribute": "technical_skills",
  "questions": ["q1", "q2"],
  "scoring": {
    "calculation": "average",
    "normalize": true,
    "weight": 1.0
  }
}
```
