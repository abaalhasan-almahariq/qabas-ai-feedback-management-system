"""Domain vocabulary used by the final UML.

The persistence layer keeps the legacy ``Complaint`` table/class name so existing
migrations, API clients, and the Angular application remain compatible.  These
aliases expose the terminology used in the final design documentation without
creating a second set of database tables.
"""
from .models.db_models import (
    AdminTier,
    Category,
    Complaint as Feedback,
    ComplaintHistory as FeedbackHistory,
    ComplaintStatus as FeedbackStatus,
    Course,
    CourseStatus,
    Notification,
    UrgencyLevel,
    User,
    UserRole,
)
from .models.chat_models import ChatMessage, ChatSession, ChatSender, ChatStatus
from .models.metadata_models import Keyword

__all__ = [
    "AdminTier",
    "Category",
    "ChatMessage",
    "ChatSender",
    "ChatSession",
    "ChatStatus",
    "Course",
    "CourseStatus",
    "Feedback",
    "FeedbackHistory",
    "FeedbackStatus",
    "Keyword",
    "Notification",
    "UrgencyLevel",
    "User",
    "UserRole",
]
