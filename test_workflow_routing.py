"""Tests for deterministic workflow intent routing."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from brain.brain import Brain
from brain.context import ACTIVE_PDF, SEARCH_DIRECTORY
from brain.errors import InvalidRequestError
from brain.workflow import Workflow
from brain.workflow_router import (
    FILE_SEARCH_TO_PDF_WORKFLOW_NAME,
    WorkflowRouter,
    build_file_search_to_pdf_workflow,
    has_required_context,
)


# ==================================================
# Workflow recognition -- PDF -> Notes
# ==================================================

def test_recognize_summarize_pdf_and_save_note():
    router = WorkflowRouter()
    wf = router.route("summarize the PDF and save a note")
    assert wf is not None
    assert wf.name == "pdf-to-note"
    print("Recognize summarize-pdf-and-save-note passed.")


def test_recognize_save_note_from_pdf():
    router = WorkflowRouter()
    wf = router.route("save a note from the PDF")
    assert wf is not None
    assert wf.name == "pdf-to-note"
    print("Recognize save-note-from-pdf passed.")


def test_recognize_turn_pdf_into_note():
    router = WorkflowRouter()
    wf = router.route("turn the PDF into a note")
    assert wf is not None
    assert wf.name == "pdf-to-note"
    print("Recognize turn-pdf-into-note passed.")


# ==================================================
# Workflow recognition -- File Search -> PDF
# ==================================================

def test_recognize_search_and_summarize_pdf():
    router = WorkflowRouter()
    wf = router.route("search for budget and summarize the PDF")
    assert wf is not None
    assert wf.name == FILE_SEARCH_TO_PDF_WORKFLOW_NAME
    print("Recognize search-and-summarize-pdf passed.")


def test_recognize_find_pdf_containing_and_process():
    router = WorkflowRouter()
    wf = router.route("find PDF containing invoice and process it")
    assert wf is not None
    assert wf.name == FILE_SEARCH_TO_PDF_WORKFLOW_NAME
    print("Recognize find-pdf-containing-and-process passed.")


def test_file_search_query_extracted():
    router = WorkflowRouter()
    wf = router.route("search for quarterly report and then summarize the PDF")
    assert wf is not None
    assert wf.steps[0].intent == "file_search"
    assert "quarterly report" in wf.steps[0].request
    print("File search query extraction passed.")


# ==================================================
# Ambiguous / non-workflow requests
# ==================================================

def test_simple_summarize_pdf_not_routed():
    """A plain 'summarize the PDF' should NOT route to a workflow."""
    router = WorkflowRouter()
    wf = router.route("summarize the PDF")
    assert wf is None
    print("Simple summarize-pdf not routed passed.")


def test_simple_save_note_not_routed():
    router = WorkflowRouter()
    wf = router.route("create note: hello")
    assert wf is None
    print("Simple save-note not routed passed.")


def test_simple_file_search_not_routed():
    router = WorkflowRouter()
    wf = router.route("search for hello")
    assert wf is None
    print("Simple file-search not routed passed.")


def test_empty_message_returns_none():
    router = WorkflowRouter()
    assert router.route("") is None
    assert router.route("   ") is None
    print("Empty message returns None passed.")


# ==================================================
# Required context guard
# ==================================================

def test_pdf_to_note_requires_active_pdf():
    wf = build_file_search_to_pdf_workflow.__wrapped__ if hasattr(build_file_search_to_pdf_workflow, '__wrapped__') else None
    from brain.workflow import build_pdf_to_note_workflow
    wf = build_pdf_to_note_workflow()
    assert has_required_context(wf, {}) is False
    assert has_required_context(wf, {ACTIVE_PDF: "/tmp/x.pdf"}) is True
    print("PDF-to-note requires active_pdf passed.")


def test_file_search_to_pdf_requires_search_directory():
    wf = build_file_search_to_pdf_workflow("query")
    assert has_required_context(wf, {}) is False
    assert has_required_context(wf, {SEARCH_DIRECTORY: "/tmp"}) is True
    print("File-search-to-pdf requires search_directory passed.")


# ==================================================
# Brain.process integration -- missing context
# ==================================================

def test_brain_workflow_missing_context_falls_through():
    """When a workflow is recognized but context is missing,
    Brain.process falls back to single-capability handling rather
    than running a workflow that would fail.
    """
    brain = Brain()
    # "summarize the PDF and save a note" matches the PDF-to-note
    # workflow, but without active_pdf it should fall through.
    with patch("capabilities.chat.ask_gemini", return_value="chat response"):
        result = brain.process("summarize the PDF and save a note")
    # Should fall through to chat (the default intent), not crash.
    assert isinstance(result, str)
    print("Brain workflow missing-context fallthrough passed.")


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
    print("Brain workflow with context runs workflow passed.")


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
    print("Brain workflow failure returned safely passed.")


# ==================================================
# Regression -- single-capability commands unchanged
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
    """A simple 'summarize the PDF' (no note clause) should route to
    the single pdf capability, not a workflow.
    """
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


def main():
    test_recognize_summarize_pdf_and_save_note()
    test_recognize_save_note_from_pdf()
    test_recognize_turn_pdf_into_note()
    test_recognize_search_and_summarize_pdf()
    test_recognize_find_pdf_containing_and_process()
    test_file_search_query_extracted()
    test_simple_summarize_pdf_not_routed()
    test_simple_save_note_not_routed()
    test_simple_file_search_not_routed()
    test_empty_message_returns_none()
    test_pdf_to_note_requires_active_pdf()
    test_file_search_to_pdf_requires_search_directory()
    test_brain_workflow_missing_context_falls_through()
    test_brain_workflow_with_context_runs_workflow()
    test_brain_workflow_failure_returned_safely()
    test_brain_process_chat_still_works()
    test_brain_process_notes_command_still_works()
    test_brain_process_empty_message_still_raises()
    test_brain_process_file_search_with_context_still_works()
    test_brain_process_pdf_intent_still_works()
    print("\nAll workflow routing tests passed.")


if __name__ == "__main__":
    main()
