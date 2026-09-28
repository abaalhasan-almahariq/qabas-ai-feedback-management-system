# QABAS — AI-Powered Student Feedback Analysis & Management System

QABAS (**Quality Assessment for Better Academic Services**) is a graduation-project system for collecting, classifying, managing, and analyzing university student feedback.

Students can submit course-related feedback directly or through an AI-assisted chat flow. The project used GPT-4o mini with a LangGraph classification pipeline to produce structured results such as category, sentiment, urgency, keywords, and a summary, while administrators could review, assign, track, discuss, and analyze feedback.

> **Portfolio note:** QABAS was built by a **3-member graduation-project team**. My main contributions were technical documentation, system design and architecture decisions, testing, backend routing/integration fixes, and database troubleshooting. This repository is a curated post-graduation portfolio edition: selected implementation pieces were refactored to better match the final UML and those changes are documented separately from the original team submission.

## Features represented by the project

- Student registration, login, email verification, and role-based access control
- Course-scoped feedback submission
- AI classification for category, sentiment, urgency, keywords, and summaries
- Feedback lifecycle and audit-history tracking
- Student/admin discussion and real-time updates
- AI-assisted feedback chat flow
- Analytics and course-level statistics
- Arabic/English interface support
- Master / Advance / Basic administration tiers

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | Angular 17, TypeScript, RxJS, Angular Material, Chart.js, ngx-translate |
| Backend | Python, FastAPI, SQLModel, Pydantic |
| AI | OpenAI GPT-4o mini, LangChain, LangGraph |
| Data | SQLite during local development; PostgreSQL support in the team project |
| Auth / Security | JWT, bcrypt, RBAC, CSRF checks |
| Real-time | FastAPI WebSocket + RxJS |
| Testing | pytest, pytest-asyncio, httpx, Locust |
| DevOps | Docker Compose, GitHub Actions |

## Final UML as the design reference

The final project UML is treated as the source of truth for this portfolio refactor.

- [Portfolio class diagram](docs/CLASS_DIAGRAM.md)
- [UML-to-code mapping and design decisions](docs/UML_TO_CODE.md)
- [Post-graduation refactor notes](PORTFOLIO_REFACTOR.md)

One small documentation correction is made transparently: the original class diagram contains a second box labelled `ChatMessage`, but its fields and operations describe an `AdminNote`. The portfolio diagram labels it `AdminNote`.

### Architecture alignment

The portfolio edition introduces several targeted changes rather than rewriting the entire team application:

- `FeedbackService` centralizes the UML operations `submit`, `edit`, `rateSatisfaction`, and `getHistory`.
- `AIClassificationPipeline` provides a domain-level facade over the LangGraph classification implementation.
- `backend/domain.py` exposes the final UML term **Feedback** while keeping the original `Complaint` persistence/API vocabulary compatible.
- The shared rate limiter is separated from the application entry point to avoid a circular import.
- The refactor also addressed a duplicate feedback-history route, async health-check behavior, logout integration, startup lifecycle handling, and preservation of the student's original Arabic text during classification.

## Selected portfolio implementation

```text
backend/
├── core/
│   └── rate_limit.py
├── services/
│   ├── ai_pipeline.py
│   └── feedback_service.py
└── domain.py

docs/
├── CLASS_DIAGRAM.md
├── UML_TO_CODE.md
└── screenshots/
    └── feedback-dashboard.jpg

.env.example
.gitignore
PORTFOLIO_REFACTOR.md
README.md
```

This public repository focuses on the architecture, design mapping, and selected refactored implementation rather than publishing every file from the original team workspace. That keeps the portfolio focused and avoids presenting unrelated team code or local development material as my individual work.

## Interface preview

### Feedback dashboard

![Feedback dashboard](docs/screenshots/feedback-dashboard.jpg)

> The interface uses development/demo data. Screenshots demonstrate the project UI and are not presented as production usage metrics.

## Security / repository hygiene

The portfolio intentionally excludes the original `.env`, local databases, virtual environments, caches, IDE metadata, and other machine-specific files. `.env.example` contains placeholders only; real API keys and secrets should never be committed.

## My contribution

My work on the original graduation project focused heavily on:

- technical documentation and maintaining a coherent design specification;
- system architecture and design decisions;
- software testing and validation;
- backend routing and integration troubleshooting;
- database troubleshooting and fixes;
- collaboration across frontend, backend, database, and AI work.

The post-graduation code cleanup in this repository is identified as a **portfolio refactor** rather than being presented as part of the original submitted implementation.
