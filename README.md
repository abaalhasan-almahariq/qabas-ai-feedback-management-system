# QABAS — AI-Powered Student Feedback Analysis & Management System

QABAS (**Quality Assessment for Better Academic Services**) is a graduation-project web application for collecting, classifying, managing, and analyzing university student feedback.

Students can submit course-related feedback directly or use an AI-assisted chat flow. The backend uses GPT-4o mini through a LangGraph pipeline to produce structured classification results such as category, sentiment, urgency, keywords, and a short summary. Administrators can then review, discuss, assign, track, and analyze feedback through a role-scoped dashboard.

> **Portfolio note:** this was a **3-member graduation project**, not a solo project. This repository is a cleaned portfolio edition of the team codebase. My main contributions were technical documentation, system design/architecture decisions, testing, backend routing/integration fixes, and database troubleshooting. The portfolio edition also contains post-project refactoring to better align the code structure with the final UML design; those refactors are documented below rather than presented as part of the original submission.

## Features

- Student registration, login, email verification, and role-based access control
- Course-scoped feedback submission
- AI classification pipeline using GPT-4o mini and LangGraph
- Category, sentiment, urgency, keyword, and summary extraction
- Feedback lifecycle tracking: pending → classifying → classified → in progress → resolved / closed
- Admin assignment and audit history
- Student/admin discussion threads and WebSocket-based updates
- AI-assisted student chat flow
- Analytics dashboard and course-level statistics
- Arabic/English interface support
- Master/Advance/Basic admin permission tiers
- Docker setup for frontend, backend, and PostgreSQL

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | Angular 17, TypeScript, RxJS, Angular Material, Chart.js, ngx-translate |
| Backend | Python, FastAPI, SQLModel, Pydantic |
| AI | OpenAI GPT-4o mini, LangChain, LangGraph |
| Data | SQLite for local development; PostgreSQL supported through Docker |
| Auth / Security | JWT, bcrypt, RBAC, CSRF token checks |
| Real-time | FastAPI WebSocket + RxJS |
| Testing | pytest, pytest-asyncio, httpx, Locust |
| DevOps | Docker Compose, GitHub Actions |

## Architecture

The final design follows a **3-tier client-server architecture** with an AI classification pipeline inside the backend logic tier.

![System architecture](docs/diagrams/system-architecture.png)

The classification flow is organized as:

**Preprocess → Classify → Postprocess → Escalation Check**

![Backend pipeline](docs/diagrams/backend-pipeline.png)

## UML & Design

The final UML is the source of truth for the portfolio refactor.

- [Portfolio class diagram (Mermaid)](docs/CLASS_DIAGRAM.md)
- [UML-to-code mapping and design decisions](docs/UML_TO_CODE.md)
- [Original class diagram](docs/diagrams/class-diagram.png)
- [Activity diagram](docs/diagrams/activity-diagram.png)
- [Data-flow diagram](docs/diagrams/data-flow-diagram.png)
- [Entity-relationship diagram](docs/diagrams/erd.png)
- [Use-case diagram](docs/diagrams/use-case-diagram.png)

### Portfolio Refactor Highlights

The original implementation worked but did not always mirror the final UML structure. The portfolio edition therefore makes several targeted architectural changes while keeping the working API contract compatible:

- Introduces a `FeedbackService` for the UML operations `submit`, `edit`, `rateSatisfaction`, and `getHistory` instead of keeping that business logic inside FastAPI route functions.
- Adds an `AIClassificationPipeline` facade matching the UML pipeline entity while keeping the existing LangGraph nodes underneath.
- Adds `backend/domain.py` aliases so the final UML term **Feedback** is represented cleanly while the legacy database/API name `Complaint` remains compatible.
- Removes a duplicate feedback-history route.
- Preserves the student's original Arabic feedback during English translation for classification.
- Fixes the async database health check, authentication logout flow, application startup lifespan, and Docker database health dependency.
- Removes local secrets, virtual environments, database files, IDE metadata, caches, and internal scratch files from the portfolio tree.

See [docs/UML_TO_CODE.md](docs/UML_TO_CODE.md) for the exact mapping.

## Screenshots

### Feedback dashboard

![Feedback dashboard](docs/screenshots/feedback-dashboard.jpg)

### Analytics dashboard

![Analytics dashboard](docs/screenshots/analytics-dashboard.jpg)

### Arabic/English AI assistant

![AI chatbot](docs/screenshots/chatbot-arabic.jpg)

### Login UI

![Login screen](docs/screenshots/login-screen.jpg)

> Some screenshots contain demo/prototype data used during development and are shown to demonstrate the interface rather than production metrics.

## Project Structure

```text
QABAS/
├── backend/
│   ├── core/
│   ├── graph/
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── domain.py
│   └── main.py
├── frontend/
│   └── feedback-dashboard/
├── tests/
├── docs/
│   ├── diagrams/
│   └── screenshots/
├── .github/workflows/
├── docker-compose.yml
├── seeder.py
└── requirements.txt
```

## Running Locally

### 1. Environment

Copy the environment template:

```bash
cp .env.example .env
```

Set at minimum:

```env
OPENAI_API_KEY=your_key_here
JWT_SECRET_KEY=your_long_random_secret
ALLOWED_ORIGINS=http://localhost:4200
```

Do **not** commit `.env`.

### 2. Backend

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python seeder.py
uvicorn backend.main:app --reload --port 8001
```

API documentation:

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`
- Health: `http://localhost:8001/api/health`

### 3. Frontend

```bash
cd frontend/feedback-dashboard
npm install --legacy-peer-deps
npm start
```

Frontend: `http://localhost:4200`

## Docker

```bash
cp .env.example .env
# Fill in real secrets first
docker compose up --build
```

The Docker configuration starts PostgreSQL, the FastAPI backend, and the Angular frontend.

## Tests

```bash
pytest -v
```

The repository includes unit, RBAC, JWT, API, end-to-end, and load-testing files from the project.

## Security Notes

This portfolio edition intentionally excludes the original `.env`, local database, and development virtual environment. Replace all example credentials before any real deployment. The application was built as an academic project and should receive a full production security review before handling real institutional data.

## Team Project / My Contribution

This system was built by a three-member multidisciplinary graduation-project team. My contribution focused heavily on:

- technical documentation and keeping the design specification coherent;
- system architecture and design decisions;
- software testing and validation;
- backend routing/integration troubleshooting;
- database troubleshooting and fixes;
- cross-team work between frontend, backend, database, and AI components.

The source in this portfolio remains representative of a **team project**. The post-graduation cleanup/refactor in this repository is separate from the original team contribution and is documented as such.
