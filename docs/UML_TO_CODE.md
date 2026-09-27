# UML-to-Code Mapping

The final project documentation uses a conceptual UML model. The original implementation evolved quickly during development, so some names and responsibilities drifted away from the diagram. This portfolio refactor treats the final UML as the design reference while preserving compatibility with the working application.

## Main Mapping

| Final UML concept | Portfolio implementation | Notes |
| --- | --- | --- |
| `User` | `backend.models.db_models.User` | Stored as one relational table. Role/tier determine runtime capabilities. |
| `Student` | `User(role=student)` + `require_student` | Conceptual subclass represented through RBAC rather than a second database table. |
| `User_Admin` | `User(role=admin)` | Shared admin behavior is enforced through auth dependencies. |
| `Advance Admin` | `User(admin_tier=advance)` | Course-scoped management permissions. |
| `Master Admin` | `User(admin_tier=master)` | Global administration permissions. |
| `Lecturer` | Conceptual role in UML | The final application primarily operationalized student/admin roles; lecturer-specific attendance/homework behavior was not part of the core deployed feedback workflow. |
| `Feedback` | `Complaint` persistence model + `FeedbackService` | The table/API retained the legacy word `complaint`; `backend/domain.py` exposes the final design term `Feedback`. |
| `FeedbackHistory` | `ComplaintHistory` | Same compatibility decision as `Feedback`. |
| `Category` | `Category` | Direct mapping. |
| `Keyword` | `Keyword` / `ComplaintKeyword` | Normalized keyword support. |
| `UrgencyLevel` | `UrgencyLevel` | Direct mapping. |
| `Course` | `Course` + course router/service behavior | Direct persistence mapping. |
| `Notification` | `Notification` | Direct mapping. |
| `ChatSession` | `ChatSession` | Direct mapping. |
| `ChatMessage` | `ChatMessage` | Student-AI assistant messages. |
| `AdminNote` | `AdminNote` | The original diagram image accidentally labels this box `ChatMessage`; its fields/methods clearly describe `AdminNote`. The portfolio diagram corrects that label. |
| `AIClassificationPipeline` | `backend.services.ai_pipeline.AIClassificationPipeline` | Facade over the existing LangGraph implementation. |

## Why `User` subclasses are not separate SQL tables

The class diagram uses inheritance to communicate roles and responsibilities. A literal table-per-subclass implementation would add unnecessary relational complexity for this project because the subclasses share almost all persisted fields.

The code therefore uses **single-table role representation**:

- `User.role` distinguishes student vs admin.
- `User.admin_tier` distinguishes Master / Advance / Basic admin capability.
- FastAPI authorization dependencies enforce the behavioral boundaries expressed by UML inheritance.

This keeps the conceptual model while using a simpler database design.

## Why the database still says `Complaint`

The project began with the word `Complaint` throughout the API and database. The final documentation broadened the concept to **student feedback**. Renaming the physical table, every endpoint, every frontend service, and every migration solely for terminology would introduce avoidable breakage.

The portfolio edition therefore uses an adapter-style approach:

- Database/API compatibility: `Complaint`, `/api/complaints/...`
- Domain/design terminology: `Feedback`, `FeedbackService`
- Alias layer: `backend/domain.py`

This makes the final UML visible in the code without pretending the legacy contract never existed.

## UML methods and responsibility placement

The UML places operations such as `submit`, `edit`, `rateSatisfaction`, and `getHistory` on the `Feedback` entity. In the portfolio code they are implemented in `FeedbackService` rather than directly on the SQLModel ORM class. That is intentional: persistence models remain data-focused while application services coordinate database queries, authorization, notifications, and audit logging.

The same principle applies to the AI pipeline: LangGraph nodes stay small and testable, while `AIClassificationPipeline.run()` is the single domain-level entry point described in the UML.

## UI Interfaces

The UML contains `LoginUI`, `DashboardUI`, `FeedbackUI`, `CourseUI`, `EditCourseUI`, `ChatbotUI`, and `PermissionMatrixUI`. In the implementation these responsibilities are realized by Angular components, routes, guards, and services rather than Python interface classes.

Examples:

- `LoginUI` → `features/login` + `AuthService`
- `DashboardUI` → `features/admin-dashboard` / `features/analytics-dashboard`
- `FeedbackUI` → `features/complaint-workspace`
- `CourseUI` / `EditCourseUI` → `features/course-management` / `course-detail`
- `ChatbotUI` → `features/chat`
- `PermissionMatrixUI` → `features/permission-matrix`

## Refactor Boundary

The goal of this portfolio pass is architecture alignment and safe cleanup, not rewriting every working feature. Existing route contracts are intentionally preserved so the Angular frontend and tests do not need a destructive migration.
