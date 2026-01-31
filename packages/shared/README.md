# Shared Packages

This directory contains shared code and configuration used by both the API and web app.

## Contents

- **`scoring-rules.json`** - Defines the attributes used for candidate scoring and how they're calculated
- Future: TypeScript types, shared validation schemas, etc.

## Scoring Rules

The scoring system uses these attributes to evaluate candidates:

1. **Technical Skills** - Programming, tools, technical problem-solving
2. **Communication** - Written and verbal communication abilities
3. **Leadership** - Team management, decision-making, vision
4. **Problem Solving** - Analytical thinking, creativity
5. **Adaptability** - Flexibility, learning agility, change management
6. **Teamwork** - Collaboration, interpersonal skills

Each attribute is scored 0-10 and can be weighted differently per role configuration.
