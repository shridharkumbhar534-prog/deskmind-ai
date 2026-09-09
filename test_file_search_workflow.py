"""Tests for workflow-compatible FileSearchCapability.

Covers:
- Structured results stored in context for workflow consumers
- Absolute path resolution
- PDF file discovery
- No matches
- Multiple matches (ambiguity)
- Human-readable display string preserved for UI
- Backward compatibility with Brain.process
"""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from brain.brain import Brain
from brain.context import ACTIVE_PDF, SEARCH_DIRECTORY
from brain.workflow import Workflow, WorkflowStep
from capabilities.file_search import (
    FILE_SEARCH_RESULTS,
    FileSearchCapability,
    FileSearchResult,
)
from capabilities.pdf import PDFCapability


# ==================================================
# Helpers
# ==================================================

def _make_pdf(path: Path, text: str):
    import pymupdf
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(str(path))
    doc.close()


# ==================================================
# Structured results
# ==================================================

def test_structured_result_stored_in_context():
    with TemporaryDirectory() as directory:
        test_file = Path(directory) / "notes.txt"
        test_file.write_text("findme keyword")

        ctx = {SEARCH_DIRECTORY: directory}
        display = FileSearchCapability().execute("findme", ctx)

        assert FILE_SEARCH_RESULTS in ctx
        result = ctx[FILE_SEARCH_RESULTS]
        assert isinstance(result, FileSearchResult)
        assert result.has_matches
        assert result.query == "findme"
        assert len(result.matches) == 1
    print("Structured result stored in context passed.")


def test_human_readable_display_preserved():
    with TemporaryDirectory() as directory:
        test_file = Path(directory) / "notes.txt"
        test_file.write_text("findme keyword")

        ctx = {SEARCH_DIRECTORY: directory}
        display = FileSearchCapability().execute("findme", ctx)

        assert "Files containing" in display
        assert "1 found" in display
        assert "notes.txt" in display
    print("Human-readable display preserved passed.")


# ==================================================
# Absolute path resolution
# ==================================================

def test_resolved_paths_are_absolute():
    with TemporaryDirectory() as directory:
        test_file = Path(directory) / "subdir" / "deep.txt"
        test_file.parent.mkdir()
        test_file.write_text("findme")

        ctx = {SEARCH_DIRECTORY: directory}
        FileSearchCapability().execute("findme", ctx)
        result = ctx[FILE_SEARCH_RESULTS]

        for p in result.resolved_paths():
            assert Path(p).is_absolute()
            assert Path(p).exists()
    print("Absolute path resolution passed.")


def test_first_resolved_path():
    with TemporaryDirectory() as directory:
        test_file = Path(directory) / "only.txt"
        test_file.write_text("findme")

        ctx = {SEARCH_DIRECTORY: directory}
        FileSearchCapability().execute("findme", ctx)
        result = ctx[FILE_SEARCH_RESULTS]

        assert result.first_resolved_path() is not None
        assert Path(result.first_resolved_path()).is_absolute()
        assert Path(result.first_resolved_path()).exists()
    print("First resolved path passed.")


def test_first_resolved_path_none_when_no_matches():
    with TemporaryDirectory() as directory:
        ctx = {SEARCH_DIRECTORY: directory}
        FileSearchCapability().execute("nothing", ctx)
        result = ctx[FILE_SEARCH_RESULTS]

        assert result.first_resolved_path() is None
    print("First resolved path None passed.")


# ==================================================
# PDF discovery
# ==================================================

def test_pdf_discovery():
    with TemporaryDirectory() as directory:
        pdf_file = Path(directory) / "report.pdf"
        _make_pdf(pdf_file, "unique pdf keyword")

        ctx = {SEARCH_DIRECTORY: directory}
        FileSearchCapability().execute("unique pdf keyword", ctx)
        result = ctx[FILE_SEARCH_RESULTS]

        assert result.has_matches
        assert len(result.matches) == 1
        assert result.matches[0].suffix == ".pdf"
        assert Path(result.first_resolved_path()).is_absolute()
    print("PDF discovery passed.")


def test_pdf_no_match():
    with TemporaryDirectory() as directory:
        pdf_file = Path(directory) / "report.pdf"
        _make_pdf(pdf_file, "some content")

        ctx = {SEARCH_DIRECTORY: directory}
        FileSearchCapability().execute("nonexistent keyword", ctx)
        result = ctx[FILE_SEARCH_RESULTS]

        assert not result.has_matches
    print("PDF no match passed.")


def test_pdf_consumes_single_structured_match():
    with TemporaryDirectory() as directory:
        pdf_file = Path(directory) / "report.pdf"
        _make_pdf(pdf_file, "workflow pdf keyword")
        ctx = {SEARCH_DIRECTORY: directory}
        FileSearchCapability().execute("workflow pdf keyword", ctx)

        with patch("services.gemini_service.ask_gemini", return_value="summary"):
            result = PDFCapability().execute("Summarize", ctx)

        assert result == "summary"
        assert Path(ctx[ACTIVE_PDF]) == pdf_file.resolve()
    print("PDF consumes single structured match passed.")


def test_pdf_rejects_ambiguous_structured_matches():
    with TemporaryDirectory() as directory:
        for name in ("a.pdf", "b.pdf"):
            _make_pdf(Path(directory) / name, "ambiguous keyword")

        ctx = {SEARCH_DIRECTORY: directory}
        FileSearchCapability().execute("ambiguous keyword", ctx)

        try:
            PDFCapability().execute("Summarize", ctx)
        except ValueError as error:
            assert "multiple" in str(error)
        else:
            raise AssertionError("Expected an explicit ambiguity error")
    print("PDF ambiguity handling passed.")


def test_file_search_to_pdf_workflow():
    with TemporaryDirectory() as directory:
        pdf_file = Path(directory) / "report.pdf"
        _make_pdf(pdf_file, "workflow chain keyword")
        brain = Brain()
        workflow = Workflow("search-pdf", [
            WorkflowStep("file_search", "workflow chain keyword"),
            WorkflowStep("pdf", "Summarize this PDF"),
        ])

        with patch("services.gemini_service.ask_gemini", return_value="workflow summary"):
            result = brain.run_workflow(
                workflow,
                context={SEARCH_DIRECTORY: directory},
            )

        assert result["results"] == [
            'Files containing "workflow chain keyword" (1 found):\n- report.pdf',
            "workflow summary",
        ]
    print("File Search to PDF workflow passed.")


# ==================================================
# No matches
# ==================================================

def test_no_matches_structured():
    with TemporaryDirectory() as directory:
        test_file = Path(directory) / "notes.txt"
        test_file.write_text("hello world")

        ctx = {SEARCH_DIRECTORY: directory}
        FileSearchCapability().execute("nonexistent", ctx)
        result = ctx[FILE_SEARCH_RESULTS]

        assert not result.has_matches
        assert len(result.matches) == 0
        assert result.first_resolved_path() is None
    print("No matches structured passed.")


def test_no_matches_display():
    with TemporaryDirectory() as directory:
        ctx = {SEARCH_DIRECTORY: directory}
        display = FileSearchCapability().execute("nothing", ctx)

        assert "No files found" in display
    print("No matches display passed.")


# ==================================================
# Multiple matches (ambiguity)
# ==================================================

def test_multiple_matches_is_ambiguous():
    with TemporaryDirectory() as directory:
        f1 = Path(directory) / "a.txt"
        f1.write_text("shared keyword")
        f2 = Path(directory) / "b.txt"
        f2.write_text("shared keyword")

        ctx = {SEARCH_DIRECTORY: directory}
        FileSearchCapability().execute("shared keyword", ctx)
        result = ctx[FILE_SEARCH_RESULTS]

        assert result.is_ambiguous
        assert len(result.matches) == 2
    print("Multiple matches ambiguity passed.")


def test_single_match_not_ambiguous():
    with TemporaryDirectory() as directory:
        f1 = Path(directory) / "a.txt"
        f1.write_text("unique keyword")

        ctx = {SEARCH_DIRECTORY: directory}
        FileSearchCapability().execute("unique keyword", ctx)
        result = ctx[FILE_SEARCH_RESULTS]

        assert not result.is_ambiguous
        assert len(result.matches) == 1
    print("Single match not ambiguous passed.")


def test_multiple_matches_display_shows_all():
    with TemporaryDirectory() as directory:
        f1 = Path(directory) / "a.txt"
        f1.write_text("shared keyword")
        f2 = Path(directory) / "b.txt"
        f2.write_text("shared keyword")

        ctx = {SEARCH_DIRECTORY: directory}
        display = FileSearchCapability().execute("shared keyword", ctx)

        assert "2 found" in display
        assert "a.txt" in display
        assert "b.txt" in display
    print("Multiple matches display passed.")


# ==================================================
# Deterministic ordering
# ==================================================

def test_deterministic_ordering():
    """rglob traversal order is deterministic (alphabetical within
    each directory level).  The same directory and query always
    produces the same match order.
    """
    with TemporaryDirectory() as directory:
        for name in ("c.txt", "a.txt", "b.txt"):
            Path(directory, name).write_text("keyword")

        ctx = {SEARCH_DIRECTORY: directory}
        FileSearchCapability().execute("keyword", ctx)
        result1 = ctx[FILE_SEARCH_RESULTS]

        ctx2 = {SEARCH_DIRECTORY: directory}
        FileSearchCapability().execute("keyword", ctx2)
        result2 = ctx2[FILE_SEARCH_RESULTS]

        assert result1.resolved_paths() == result2.resolved_paths()
    print("Deterministic ordering passed.")


# ==================================================
# Backward compatibility
# ==================================================

def test_brain_process_file_search_still_works():
    brain = Brain()
    with TemporaryDirectory() as directory:
        test_file = Path(directory) / "test.txt"
        test_file.write_text("hello world")

        result = brain.process("hello", {SEARCH_DIRECTORY: directory})
        assert "test.txt" in result
    print("Brain.process file search backward compatibility passed.")


def test_empty_query_returns_message():
    with TemporaryDirectory() as directory:
        ctx = {SEARCH_DIRECTORY: directory}
        display = FileSearchCapability().execute("   ", ctx)

        assert "Please enter" in display
        assert FILE_SEARCH_RESULTS not in ctx
    print("Empty query backward compatibility passed.")


def test_missing_directory_raises():
    ctx = {}
    try:
        FileSearchCapability().execute("query", ctx)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for missing search_directory")
    print("Missing directory raises passed.")


def test_pdf_in_supported_extensions():
    assert ".pdf" in FileSearchCapability.SUPPORTED_EXTENSIONS
    print("PDF in supported extensions passed.")


def main():
    test_structured_result_stored_in_context()
    test_human_readable_display_preserved()
    test_resolved_paths_are_absolute()
    test_first_resolved_path()
    test_first_resolved_path_none_when_no_matches()
    test_pdf_discovery()
    test_pdf_no_match()
    test_pdf_consumes_single_structured_match()
    test_pdf_rejects_ambiguous_structured_matches()
    test_file_search_to_pdf_workflow()
    test_no_matches_structured()
    test_no_matches_display()
    test_multiple_matches_is_ambiguous()
    test_single_match_not_ambiguous()
    test_multiple_matches_display_shows_all()
    test_deterministic_ordering()
    test_brain_process_file_search_still_works()
    test_empty_query_returns_message()
    test_missing_directory_raises()
    test_pdf_in_supported_extensions()
    print("\nAll file search workflow tests passed.")


if __name__ == "__main__":
    main()
