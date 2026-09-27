# Portfolio Refactor Notes

This repository is a post-graduation cleanup of the team project source.

The refactor is intentionally transparent: it improves maintainability and better reflects the final UML, but it does not claim those changes were all part of the original submitted implementation.

## Changes made for the portfolio edition

- Removed `.env`, local SQLite database files, virtual environments, `__pycache__`, IDE metadata, and internal scratch/review files.
- Moved the rate limiter to `backend/core/rate_limit.py` to eliminate the router ↔ app circular import.
- Migrated FastAPI startup logic to a lifespan handler.
- Fixed the asynchronous database health check.
- Added the missing logout endpoint and cleaned duplicate auth imports.
- Prevented Arabic source feedback from being overwritten by its English classification translation.
- Removed the duplicate `/complaints/{id}/history` route.
- Added a `FeedbackService` so core feedback use cases match the responsibilities in the final UML.
- Added `AIClassificationPipeline` as a domain-level facade around the LangGraph implementation.
- Added UML terminology aliases in `backend/domain.py` while keeping legacy API/database compatibility.
- Fixed Docker health dependencies for PostgreSQL/backend startup.
- Added architecture/UML documentation and selected UI screenshots.

## Deliberately not rewritten

The project contains a large set of working admin/course features. This pass avoids a destructive full rewrite of those routes simply to achieve cosmetic class-name parity. Compatibility with the Angular application remains a priority.
