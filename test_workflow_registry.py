"""Tests for the centralized WorkflowRegistry."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from brain.brain import Brain
from brain.context import ACTIVE_PDF, SEARCH_DIRECTORY
from brain.errors import InvalidRequestError
from brain.workflow import Workflow
from brain.workflow_registry import (
    FILE_SEARCH_TO_PDF_WORKFLOW_ID,
    PDF_TO_NOTE_WORKFLOW_ID,
    WorkflowDefinition,
    WorkflowRegistry,
    create_default_registry,
)
from brain.workflow_router import WorkflowRouter, has_required_context


# ==================================================
# Registration
# ==================================================

def test_register_workflow():
    registry = WorkflowRegistry()

    def build_demo():
        from brain.workflow import WorkflowStep
        return Workflow("demo", [WorkflowStep("chat", "hi")])

    definition = registry.register(
        "demo",
        "demo",
        "A demo workflow.",
        build_demo,
        required_context_keys=("active_pdf",),
    )

    assert isinstance(definition, WorkflowDefinition)
    assert definition.id == "demo"
    assert definition.name == "demo"
    assert definition.description == "A demo workflow."
    assert definition.required_context_keys == ("active_pdf",)
    print("Workflow registration passed.")


def test_duplicate_registration_raises():
    registry = WorkflowRegistry()

    def build_demo():
        from brain.workflow import WorkflowStep
        return Workflow("demo", [WorkflowStep("chat", "hi")])

    registry.register("demo", "demo", "First", build_demo)

    try:
        registry.register("demo", "demo", "Second", build_demo)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for duplicate registration")
    print("Duplicate registration raises passed.")


def test_empty_id_raises():
    registry = WorkflowRegistry()
    try:
        registry.register("", "name", "desc", lambda: None)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for empty ID")
    print("Empty ID raises passed.")


def test_empty_name_raises():
    registry = WorkflowRegistry()
    try:
        registry.register("id", "", "desc", lambda: None)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for empty name")
    print("Empty name raises passed.")


# ==================================================
# Lookup
# ==================================================

def test_lookup_known_workflow():
    registry = create_default_registry()
    definition = registry.get(PDF_TO_NOTE_WORKFLOW_ID)
    assert definition.id == PDF_TO_NOTE_WORKFLOW_ID
    assert definition.name == "pdf-to-note"
    assert "PDF" in definition.description
    print("Lookup known workflow passed.")


def test_lookup_unknown_workflow():
    registry = create_default_registry()
    try:
        registry.get("nonexistent")
    except KeyError:
        pass
    else:
        raise AssertionError("Expected KeyError for unknown workflow")
    print("Unknown workflow lookup passed.")


def test_has_workflow():
    registry = create_default_registry()
    assert registry.has(PDF_TO_NOTE_WORKFLOW_ID) is True
    assert registry.has(FILE_SEARCH_TO_PDF_WORKFLOW_ID) is True
    assert registry.has("nonexistent") is False
    print("Has workflow passed.")


def test_list_workflows():
    registry = create_default_registry()
    workflows = registry.list_workflows()
    assert len(workflows) == 2
    ids = {wf.id for wf in workflows}
    assert ids == {PDF_TO_NOTE_WORKFLOW_ID, FILE_SEARCH_TO_PDF_WORKFLOW_ID}
    print("List workflows passed.")


# ==================================================
# Building workflows through the registry
# ==================================================

def test_build_pdf_to_note():
    registry = create_default_registry()
    wf = registry.build(PDF_TO_NOTE_WORKFLOW_ID)
    assert isinstance(wf, Workflow)
    assert wf.name == "pdf-to-note"
    assert len(wf.steps) == 2
    assert wf.steps[0].intent == "pdf"
    assert wf.steps[1].intent == "notes"
    print("Build PDF-to-note passed.")


def test_build_file_search_to_pdf():
    registry = create_default_registry()
    wf = registry.build(
        FILE_SEARCH_TO_PDF_WORKFLOW_ID,
        search_query="budget",
    )
    assert isinstance(wf, Workflow)
    assert wf.name == "file-search-to-pdf"
    assert wf.steps[0].intent == "file_search"
    assert wf.steps[0].request == "budget"
    print("Build file-search-to-pdf passed.")


def test_build_unknown_raises():
    registry = create_default_registry()
    try:
        registry.build("nonexistent")
    except KeyError:
        pass
    else:
        raise AssertionError("Expected KeyError for unknown workflow build")
    print("Build unknown raises passed.")


# ==================================================
# Router resolves through registry
# ==================================================

def test_router_uses_registry():
    registry = create_default_registry()
    router = WorkflowRouter(registry)

    wf = router.route("summarize the PDF and save a note")
    assert wf is not None
    assert wf.name == "pdf-to-note"
    print("Router uses registry for PDF-to-note passed.")


def test_router_uses_registry_file_search():
    registry = create_default_registry()
    router = WorkflowRouter(registry)

    wf = router.route("search for budget and summarize the PDF")
    assert wf is not None
    assert wf.name == "file-search-to-pdf"
    assert wf.steps[0].request == "budget"
    print("Router uses registry for file-search-to-pdf passed.")


def test_router_empty_registry_returns_none():
    registry = WorkflowRegistry()
    router = WorkflowRouter(registry)

    wf = router.route("summarize the PDF and save a note")
    assert wf is None
    print("Router with empty registry returns None passed.")

# ==================================================
# Brain regression -- process, run_workflow, context
# ==================================================

def test_brain_process_chat_still_works():
    brain = Brain()
    with patch("capabilities.chat.ask_gemini", return_value="hello back"):
        result = brain.process("hello there")
    assert result == "hello back"
    print("Brain.process chat regression passed.")


def test_brain_process_notes_command_still_works():
    brain = Brain()
    result = brain.process("create note: regression test")
    assert "saved" in result.lower()
    print("Brain.process notes regression passed.")


def test_brain_process_empty_message_still_raises():
    brain = Brain()
    try:
        brain.process("   ")
    except InvalidRequestError:
        pass
    else:
        raise AssertionError("Expected InvalidRequestError")
    print("Brain.process empty-message regression passed.")


def test_brain_process_file_search_with_context_still_works():
    brain = Brain()
    with TemporaryDirectory() as directory:
        test_file = Path(directory) / "test.txt"
        test_file.write_text("findme keyword")

        result = brain.process("findme", {SEARCH_DIRECTORY: directory})
        assert "test.txt" in result
    print("Brain.process file-search regression passed.")


def test_brain_process_pdf_intent_still_works():
    brain = Brain()
    with TemporaryDirectory() as directory:
        pdf_path = Path(directory) / "doc.pdf"
        import pymupdf
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((72, 72), "single capability pdf content")
        doc.save(str(pdf_path))
        doc.close()

        with patch(
            "services.gemini_service.ask_gemini",
            return_value="pdf summary",
        ):
            result = brain.process(
                "summarize the PDF",
                {ACTIVE_PDF: str(pdf_path)},
            )

        assert result == "pdf summary"
    print("Brain.process pdf single-capability regression passed.")


def test_brain_workflow_missing_context_returns_safe_message():
    brain = Brain()
    result = brain.process("summarize the PDF and save a note")
    assert isinstance(result, str)
    assert "PDF" in result or "select" in result.lower()
    print("Brain workflow missing-context regression passed.")


def test_brain_workflow_with_context_runs_workflow():
    brain = Brain()
    with TemporaryDirectory() as directory:
        pdf_path = Path(directory) / "doc.pdf"
        import pymupdf
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((72, 72), "workflow routing content")
        doc.save(str(pdf_path))
        doc.close()

        with patch(
            "services.gemini_service.ask_gemini",
            return_value="generated summary",
        ):
            result = brain.process(
                "summarize the PDF and save a note",
                {ACTIVE_PDF: str(pdf_path)},
            )

        assert "saved" in result.lower()
    print("Brain workflow with-context regression passed.")


def test_brain_workflow_failure_returned_safely():
    brain = Brain()
    with TemporaryDirectory() as directory:
        pdf_path = Path(directory) / "doc.pdf"
        pdf_path.write_text("not a real PDF")

        with patch(
            "services.gemini_service.ask_gemini",
            return_value="ok",
        ):
            result = brain.process(
                "summarize the PDF and save a note",
                {ACTIVE_PDF: str(pdf_path)},
            )

        assert isinstance(result, str)
        assert "could not be completed" in result or "not" in result.lower()
    print("Brain workflow failure regression passed.")


def test_brain_run_workflow_still_works():
    from brain.workflow import WorkflowStep, Workflow
    brain = Brain()
    wf = Workflow("manual", [WorkflowStep("notes", "create note: from run_workflow")])
    result = brain.run_workflow(wf)
    assert result["workflow"] == "manual"
    assert "saved" in result["results"][0].lower()
    print("Brain.run_workflow regression passed.")


def test_brain_save_active_pdf_as_note_still_works():
    brain = Brain()
    with TemporaryDirectory() as directory:
        pdf_path = Path(directory) / "doc.pdf"
        import pymupdf
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((72, 72), "save as note content")
        doc.save(str(pdf_path))
        doc.close()

        with patch(
            "services.gemini_service.ask_gemini",
            return_value="saved summary",
        ):
            result = brain.save_active_pdf_as_note({ACTIVE_PDF: str(pdf_path)})

        assert result["workflow"] == "pdf-to-note"
        assert "saved" in result["results"][1].lower()
    print("Brain.save_active_pdf_as_note regression passed.")


def main():
    test_register_workflow()
    test_duplicate_registration_raises()
    test_empty_id_raises()
    test_empty_name_raises()
    test_lookup_known_workflow()
    test_lookup_unknown_workflow()
    test_has_workflow()
    test_list_workflows()
    test_build_pdf_to_note()
    test_build_file_search_to_pdf()
    test_build_unknown_raises()
    test_router_uses_registry()
    test_router_uses_registry_file_search()
    test_router_empty_registry_returns_none()
    test_brain_process_chat_still_works()
    test_brain_process_notes_command_still_works()
    test_brain_process_empty_message_still_raises()
    test_brain_process_file_search_with_context_still_works()
    test_brain_process_pdf_intent_still_works()
    test_brain_workflow_missing_context_returns_safe_message()
    test_brain_workflow_with_context_runs_workflow()
    test_brain_workflow_failure_returned_safely()
    test_brain_run_workflow_still_works()
    test_brain_save_active_pdf_as_note_still_works()
    print("\nAll workflow registry tests passed.")


if __name__ == "__main__":
    main()
