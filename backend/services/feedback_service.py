"""Application service for the Feedback aggregate.

The original implementation placed most feedback business logic directly in the
FastAPI router.  This service centralizes the operations shown on the final UML
(`submit`, `edit`, `rateSatisfaction`, and `getHistory`) while preserving the
existing database/API schema for backwards compatibility.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from ..models.auth_schemas import ComplaintHistoryPublic
from ..models.db_models import (
    AdminTier,
    Complaint,
    ComplaintHistory,
    ComplaintStatus,
    Course,
    CourseAdmin,
    CourseStatus,
    CourseStudent,
    Notification,
    User,
    UserRole,
)


def detect_language(text: str) -> str:
    """Small deterministic Arabic/English detector used before AI processing."""
    stripped = text.strip()
    if not stripped:
        return "en"
    arabic_chars = sum(1 for char in stripped if "\u0600" <= char <= "\u06ff")
    return "ar" if arabic_chars / len(stripped) > 0.30 else "en"


class FeedbackService:
    """Implements the core Feedback use cases from the UML design."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def submit(self, student: User, text: str, course_id: int) -> Complaint:
        course = await self.session.get(Course, course_id)
        if not course or course.deleted_at is not None or course.status != CourseStatus.active:
            raise HTTPException(status_code=404, detail="Course not found or inactive")

        enrollment_result = await self.session.exec(
            select(CourseStudent)
            .where(CourseStudent.course_id == course_id)
            .where(CourseStudent.student_id == student.id)
        )
        if not enrollment_result.first():
            raise HTTPException(status_code=403, detail="You are not enrolled in this course")

        language = detect_language(text)
        feedback = Complaint(
            text=text,
            user_id=student.id,
            course_id=course_id,
            detected_language=language,
            # The student's text remains the canonical text.  original_text is
            # retained for compatibility with the multilingual feature.
            original_text=text if language == "ar" else None,
        )
        self.session.add(feedback)
        await self.session.flush()

        preview = text[:100] + ("..." if len(text) > 100 else "")
        self.session.add(
            ComplaintHistory(
                complaint_id=feedback.id,
                user_id=student.id,
                action_type="created",
                old_value=None,
                new_value=preview,
            )
        )

        await self._notify_course_admins(
            course=course,
            student=student,
            feedback_id=feedback.id,
        )
        await self.session.commit()

        # Email delivery is intentionally best-effort: a mail outage must not
        # roll back a valid feedback submission.
        try:
            from .email_service import send_complaint_submitted

            send_complaint_submitted(student.email, feedback.id)
        except Exception:
            pass

        return await self._load(feedback.id)

    async def edit(self, student: User, feedback_id: int, text: str) -> Complaint:
        feedback = await self._load(feedback_id)
        self._require_owner(feedback, student)
        if feedback.status != ComplaintStatus.pending:
            raise HTTPException(status_code=400, detail="Only pending feedback can be edited")

        old_text = feedback.text
        feedback.text = text
        feedback.detected_language = detect_language(text)
        feedback.original_text = text if feedback.detected_language == "ar" else None
        self.session.add(feedback)
        self.session.add(
            ComplaintHistory(
                complaint_id=feedback.id,
                user_id=student.id,
                action_type="text_edited",
                old_value=old_text[:100],
                new_value=text[:100],
            )
        )
        await self.session.commit()
        return await self._load(feedback.id)

    async def soft_delete(self, student: User, feedback_id: int) -> None:
        feedback = await self._load(feedback_id)
        self._require_owner(feedback, student)
        if feedback.status != ComplaintStatus.pending:
            raise HTTPException(status_code=400, detail="Only pending feedback can be deleted")

        feedback.deleted_at = datetime.now(timezone.utc)
        self.session.add(feedback)
        self.session.add(
            ComplaintHistory(
                complaint_id=feedback.id,
                user_id=student.id,
                action_type="deleted",
                old_value=None,
                new_value="Feedback soft-deleted by user",
            )
        )
        await self.session.commit()

    async def rate_satisfaction(
        self,
        user: User,
        feedback_id: int,
        score: int,
        comment: str | None,
    ) -> Complaint:
        feedback = await self._load(feedback_id)
        self._require_owner(feedback, user)
        if feedback.status not in (ComplaintStatus.resolved, ComplaintStatus.closed):
            raise HTTPException(
                status_code=400,
                detail="Only resolved or closed feedback can be rated",
            )

        feedback.satisfaction_score = score
        feedback.satisfaction_comment = comment
        self.session.add(feedback)
        self.session.add(
            ComplaintHistory(
                complaint_id=feedback.id,
                user_id=user.id,
                action_type="rated",
                old_value=None,
                new_value=str(score),
            )
        )
        await self.session.commit()
        return await self._load(feedback.id)

    async def get_history(self, user: User, feedback_id: int) -> list[ComplaintHistoryPublic]:
        feedback = await self._load(feedback_id)
        if user.role == UserRole.student and feedback.user_id != user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Non-master admins are scoped to courses assigned to them.
        if user.role == UserRole.admin and user.admin_tier != AdminTier.master:
            if feedback.course_id is None:
                raise HTTPException(status_code=403, detail="Access denied")
            access_result = await self.session.exec(
                select(CourseAdmin)
                .where(CourseAdmin.course_id == feedback.course_id)
                .where(CourseAdmin.admin_id == user.id)
            )
            if not access_result.first():
                raise HTTPException(status_code=403, detail="Access denied")

        history_result = await self.session.exec(
            select(ComplaintHistory)
            .where(ComplaintHistory.complaint_id == feedback_id)
            .order_by(ComplaintHistory.timestamp.desc())
        )
        rows = list(history_result.all())
        actor_ids = {row.user_id for row in rows}
        actor_map: dict[int, str] = {}
        if actor_ids:
            users_result = await self.session.exec(select(User).where(User.id.in_(actor_ids)))
            actor_map = {actor.id: actor.username for actor in users_result.all()}

        return [
            ComplaintHistoryPublic(
                id=row.id,
                complaint_id=row.complaint_id,
                user_id=row.user_id,
                actor_username=actor_map.get(row.user_id, "system"),
                action_type=row.action_type,
                old_value=row.old_value,
                new_value=row.new_value,
                timestamp=row.timestamp,
            )
            for row in rows
        ]

    async def _load(self, feedback_id: int) -> Complaint:
        result = await self.session.exec(
            select(Complaint)
            .options(selectinload(Complaint.categories))
            .where(Complaint.id == feedback_id)
        )
        feedback = result.first()
        if not feedback or feedback.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Feedback not found")
        return feedback

    @staticmethod
    def _require_owner(feedback: Complaint, user: User) -> None:
        if feedback.user_id != user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    async def _notify_course_admins(self, course: Course, student: User, feedback_id: int) -> None:
        assigned_result = await self.session.exec(
            select(CourseAdmin).where(CourseAdmin.course_id == course.id)
        )
        admin_ids = {assignment.admin_id for assignment in assigned_result.all()}

        master_result = await self.session.exec(
            select(User).where(
                User.role == UserRole.admin,
                User.admin_tier == AdminTier.master,
                User.deleted_at.is_(None),
            )
        )
        admin_ids.update(admin.id for admin in master_result.all())

        for admin_id in admin_ids:
            self.session.add(
                Notification(
                    user_id=admin_id,
                    title="New feedback submitted",
                    message=(
                        f"Feedback #{feedback_id} in course {course.code} "
                        f"by {student.username}"
                    ),
                    complaint_id=feedback_id,
                )
            )
