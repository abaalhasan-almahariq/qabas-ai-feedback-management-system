"""UML-aligned facade over the LangGraph classification pipeline."""
from __future__ import annotations

from typing import Any

from .classifier import classify_one


class AIClassificationPipeline:
    """Run the preprocess → classify → postprocess → escalation pipeline.

    The individual nodes remain in ``backend.graph.nodes``; this facade gives the
    application a single domain-level entry point matching the final class diagram.
    """

    async def run(
        self,
        text: str,
        feedback_id: int,
        categories: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return await classify_one(text, feedback_id, categories=categories)
