"""Deterministic workflow intent routing.

A small, rule-based layer that recognizes requests for existing
DeskMind workflows and returns the matching :class:`Workflow`.
No LLM planning, no autonomy -- just deterministic pattern matching
that runs *before* single-capability intent detection so multi-step
requests are routed to the workflow engine instead of a single
capability.

Routing rules are intentionally conservative:
- A workflow is only returned when the request explicitly names the
  multi-step outcome (e.g. "search for X and summarize the PDF",
  "summarize the PDF and save a note").
- Ambiguous or partial requests return ``None`` so the caller falls
  back to single-capability intent detection.
- Required context keys are checked by the caller (Brain), not here;
  the router only decides *which* workflow matches the message.
"""

from __future__ import annotations

import re

from brain.context import ACTIVE_PDF, SEARCH_DIRECTORY
from brain.workflow import Workflow
from brain.workflow_registry import (
    FILE_SEARCH_TO_PDF_WORKFLOW_ID,
    PDF_TO_NOTE_WORKFLOW_ID,
    WorkflowRegistry,
    create_default_registry,
)


# Patterns are matched on the lowercased, stripped message.
_PDF_TO_NOTE_PATTERNS = [
    re.compile(
        r"(?:summarize|summarise)\s+(?:the\s+)?pdf\b.*\b"
        r"(?:and\s+)?(?:save|create|add|store)\b.*\bnote\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:save|create|add|store)\b.*\bnote\b.*\bfrom\b.*\bpdf\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:turn|convert)\b.*\bpdf\b.*\b(?:into|to)\b.*\bnote\b",
        re.IGNORECASE,
    ),
]

_FILE_SEARCH_TO_PDF_PATTERNS = [
    # "search for X and summarize the PDF"
    re.compile(
        r"(?:search|find|look\s+for)\s+(?:for\s+)?(?P<query>.+?)\s+"
        r"(?:and\s+)?(?:then\s+)?(?:summarize|summarise|read|open|process)\b.*\bpdf\b",
        re.IGNORECASE,
    ),
    # "find PDF containing X and summarize it"
    re.compile(
        r"(?:find|search)\b.*\bpdf\b.*\b(?:containing|with|for)\s+"
        r"(?P<query>.+?)\s+(?:and\s+)?(?:then\s+)?(?:summarize|summarise|read|process)\b",
        re.IGNORECASE,
    ),
]


class WorkflowRouter:
    """Deterministic router that maps messages to workflows.

    ``route`` returns a :class:`Workflow` when the message unambiguously
    requests a known multi-step workflow, or ``None`` when it does not.
    The caller is expected to fall back to single-capability intent
    detection when ``route`` returns ``None``.
    """

    def __init__(self, registry: WorkflowRegistry | None = None):
        self.registry = registry or create_default_registry()

    def route(self, message: str, context: dict | None = None) -> Workflow | None:
        if not message or not message.strip():
            return None

        lowered = message.strip().lower()

        # PDF -> Gemini -> Notes
        if self._matches_any(lowered, _PDF_TO_NOTE_PATTERNS):
            if not self.registry.has(PDF_TO_NOTE_WORKFLOW_ID):
                return None
            return self.registry.build(PDF_TO_NOTE_WORKFLOW_ID)

        # File Search -> PDF -> Gemini
        workflow = self._route_file_search_to_pdf(lowered)
        if workflow is not None:
            return workflow

        return None

    def _route_file_search_to_pdf(self, lowered: str) -> Workflow | None:
        if not self.registry.has(FILE_SEARCH_TO_PDF_WORKFLOW_ID):
            return None
        for pattern in _FILE_SEARCH_TO_PDF_PATTERNS:
            match = pattern.search(lowered)
            if match:
                query = match.group("query").strip()
                # Strip trailing filler words captured before the PDF clause.
                query = re.sub(
                    r"\s+(?:and|then)\s+.*$",
                    "",
                    query,
                    flags=re.IGNORECASE,
                ).strip()
                if query:
                    return self.registry.build(
                        FILE_SEARCH_TO_PDF_WORKFLOW_ID,
                        search_query=query,
                    )
        return None

    @staticmethod
    def _matches_any(text: str, patterns) -> bool:
        return any(pattern.search(text) for pattern in patterns)


def has_required_context(workflow: Workflow, context: dict | None) -> bool:
    """Check whether *context* has the keys *workflow* needs to run.

    This is a lightweight guard so Brain can return a safe message
    instead of letting the workflow fail mid-execution.
    """
    if context is None:
        context = {}

    name = workflow.name

    if name == "file-search-to-pdf":
        return SEARCH_DIRECTORY in context

    if name == "pdf-to-note":
        return ACTIVE_PDF in context

    return True
