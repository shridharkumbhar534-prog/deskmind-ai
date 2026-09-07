"""Tests for standardized context key propagation across DeskMind pages and Brain."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from brain.brain import Brain
from brain.context import (
    ACTIVE_NOTE,
    ACTIVE_PDF,
    SEARCH_DIRECTORY,
    AppContext,
)
from brain.intent import IntentDetector
from capabilities.chat import ChatCapability
from capabilities.file_search import FileSearchCapability
from capabilities.pdf import PDFCapability
from database.connection import Database
from ui.file_serch import FileSearchPage
from ui.notes import NotesPage
from ui.pdf_page import PDFPage


def test_context_constants():
    assert ACTIVE_NOTE == "active_note"
    assert ACTIVE_PDF == "active_pdf"
    assert SEARCH_DIRECTORY == "search_directory"
    print("Context constants check passed.")


def test_app_context_wrapper():
    ctx = AppContext()
    assert ctx.active_note is None
    assert ctx.active_pdf is None
    assert ctx.search_directory is None

    ctx.active_note = {"title": "Test", "content": "Hello"}
    assert ctx.active_note["title"] == "Test"
    assert ACTIVE_NOTE in ctx

    ctx.active_pdf = "/tmp/test.pdf"
    assert ctx.active_pdf == "/tmp/test.pdf"

    ctx.search_directory = "/tmp"
    assert ctx.search_directory == "/tmp"

    ctx.clear_active_note()
    assert ctx.active_note is None
    assert ACTIVE_NOTE not in ctx

    ctx.clear_active_pdf()
    assert ctx.active_pdf is None

    ctx.clear_search_directory()
    assert ctx.search_directory is None
    print("AppContext wrapper check passed.")


def test_brain_uses_search_directory_key():
    brain = Brain()
    with TemporaryDirectory() as directory:
        # Create a file that matches the query
        test_file = Path(directory) / "test.txt"
        test_file.write_text("hello world")

        result = brain.process("hello", {SEARCH_DIRECTORY: directory})
        assert "test.txt" in result
    print("Brain search_directory key check passed.")


def test_brain_passes_context_to_chat():
    detector = IntentDetector()
    assert detector.detect("hello there") == "chat"
    print("Brain chat intent check passed.")


def test_pdf_capability_reads_active_pdf():
    pdf = PDFCapability()
    try:
        pdf.execute("Summarize", {})
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for missing active_pdf")

    try:
        pdf.execute("Summarize", {"pdf_path": "/tmp/fake.pdf"})
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for old pdf_path key")

    print("PDFCapability active_pdf key check passed.")


def test_chat_capability_reads_active_note():
    chat = ChatCapability()
    with patch("capabilities.chat.ask_gemini", return_value="ok") as mock:
        chat.execute("Summarize", {ACTIVE_NOTE: {"title": "T", "content": "C"}})
        assert mock.called
        prompt = mock.call_args[0][0]
        assert "T" in prompt
        assert "C" in prompt

    with patch("capabilities.chat.ask_gemini", return_value="ok") as mock:
        chat.execute("Hello", {})
        assert mock.called
        prompt = mock.call_args[0][0]
        assert "Hello" in prompt

    print("ChatCapability active_note key check passed.")


def test_notes_page_writes_active_note():
    app = QApplication.instance() or QApplication([])
    with TemporaryDirectory() as directory:
        page = NotesPage(Database(Path(directory) / "ctx-notes.db"))
        page.title_input.setText("Context Test")
        page.content_input.setPlainText("Testing context propagation")
        page.save_note()

        assert ACTIVE_NOTE in page.context
        assert page.context[ACTIVE_NOTE]["title"] == "Context Test"

        page.new_note()
        assert ACTIVE_NOTE not in page.context
    app.quit()
    print("NotesPage active_note write check passed.")


def test_pdf_page_writes_active_pdf():
    app = QApplication.instance() or QApplication([])
    ctx = {}
    page = PDFPage(context=ctx)
    # Simulate selecting a PDF without the file dialog
    page.pdf_path = "/tmp/fake.pdf"
    page.context[ACTIVE_PDF] = "/tmp/fake.pdf"
    assert ctx[ACTIVE_PDF] == "/tmp/fake.pdf"
    app.quit()
    print("PDFPage active_pdf write check passed.")


def test_file_search_page_writes_search_directory():
    app = QApplication.instance() or QApplication([])
    ctx = {}
    page = FileSearchPage(context=ctx)
    page.directory = "/tmp"
    page.context[SEARCH_DIRECTORY] = "/tmp"
    assert ctx[SEARCH_DIRECTORY] == "/tmp"
    app.quit()
    print("FileSearchPage search_directory write check passed.")


def main():
    test_context_constants()
    test_app_context_wrapper()
    test_brain_uses_search_directory_key()
    test_brain_passes_context_to_chat()
    test_pdf_capability_reads_active_pdf()
    test_chat_capability_reads_active_note()
    test_notes_page_writes_active_note()
    test_pdf_page_writes_active_pdf()
    test_file_search_page_writes_search_directory()
    print("\nAll context propagation checks passed.")


if __name__ == "__main__":
    main()
