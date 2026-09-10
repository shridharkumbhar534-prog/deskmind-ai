"""Centralized workflow registry for DeskMind AI.

Each workflow is registered with a stable ID, human-readable name,
description, and a builder callable that produces a
:class:`~brain.workflow.Workflow` instance.  The deterministic
:class:`~brain.workflow_router.WorkflowRouter` resolves workflows
through this registry instead of constructing them inline.

This module is intentionally free of LLM planning and autonomous
execution -- workflows are explicit, hand-defined sequences.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from brain.workflow import (
    Workflow,
    WorkflowStep,
    build_pdf_to_note_workflow,
)


# Stable workflow IDs (used for lookup and routing).
PDF_TO_NOTE_WORKFLOW_ID = "pdf_to_note"
FILE_SEARCH_TO_PDF_WORKFLOW_ID = "file_search_to_pdf"


@dataclass(frozen=True)
class WorkflowDefinition:
    """A registered workflow definition."""

    id: str
    name: str
    description: str
    build: Callable[..., Workflow]
    required_context_keys: tuple[str, ...]


class WorkflowRegistry:
    """Registry of known workflow definitions.

    Workflows are registered once and looked up by stable ID.  The
    router uses this registry to resolve recognized requests into
    concrete :class:`Workflow` instances.
    """

    def __init__(self):
        self._definitions: dict[str, WorkflowDefinition] = {}

    def register(
        self,
        workflow_id: str,
        name: str,
        description: str,
        build: Callable[..., Workflow],
        required_context_keys: tuple[str, ...] = (),
    ) -> WorkflowDefinition:
        if not workflow_id or not workflow_id.strip():
            raise ValueError("Workflow ID must not be empty.")
        if not name or not name.strip():
            raise ValueError("Workflow name must not be empty.")
        if workflow_id in self._definitions:
            raise ValueError(
                f"Workflow '{workflow_id}' is already registered."
            )
        definition = WorkflowDefinition(
            id=workflow_id,
            name=name,
            description=description,
            build=build,
            required_context_keys=tuple(required_context_keys),
        )
        self._definitions[workflow_id] = definition
        return definition

    def get(self, workflow_id: str) -> WorkflowDefinition:
        if workflow_id not in self._definitions:
            raise KeyError(f"Unknown workflow: '{workflow_id}'.")
        return self._definitions[workflow_id]

    def has(self, workflow_id: str) -> bool:
        return workflow_id in self._definitions

    def list_workflows(self) -> list[WorkflowDefinition]:
        return list(self._definitions.values())

    def build(self, workflow_id: str, **kwargs) -> Workflow:
        return self.get(workflow_id).build(**kwargs)


# ---------------------------------------------------------------------------
# Default registry with the existing DeskMind workflows
# ---------------------------------------------------------------------------

def _build_file_search_to_pdf_workflow(
    search_query: str,
    pdf_request: str = "Summarize this PDF",
) -> Workflow:
    """Build the File Search -> PDF workflow for a given query."""
    return Workflow(
        "file-search-to-pdf",
        [
            WorkflowStep("file_search", search_query),
            WorkflowStep("pdf", pdf_request),
        ],
    )


def create_default_registry() -> WorkflowRegistry:
    """Return a registry pre-populated with the existing workflows."""
    registry = WorkflowRegistry()

    registry.register(
        workflow_id=PDF_TO_NOTE_WORKFLOW_ID,
        name="pdf-to-note",
        description="Summarize the active PDF with Gemini and save the result as a note.",
        build=build_pdf_to_note_workflow,
        required_context_keys=("active_pdf",),
    )

    registry.register(
        workflow_id=FILE_SEARCH_TO_PDF_WORKFLOW_ID,
        name="file-search-to-pdf",
        description="Search for files containing a query, then summarize the found PDF.",
        build=_build_file_search_to_pdf_workflow,
        required_context_keys=("search_directory",),
    )

    return registry
