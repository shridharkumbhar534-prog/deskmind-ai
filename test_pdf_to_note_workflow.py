"""Tests for the explicit PDF -> Gemini -> Notes workflow."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pymupdf

from brain.dispatcher import Dispatcher
from brain.errors import WorkflowStepError
from brain.registry import CapabilityRegistry
from brain.workflow import WorkflowEngine, build_pdf_to_note_workflow
from capabilities.notes import NotesCapability
from capabilities.pdf import PDFCapability
from database.connection import Database


def make_pdf(path: Path, text: str) -> None:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    document.save(str(path))
    document.close()


def make_engine(database_path: Path):
    registry = CapabilityRegistry()
    registry.register("pdf", PDFCapability)
    registry.register(
        "notes",
        lambda: NotesCapability(Database(database_path)),
    )
    return WorkflowEngine(Dispatcher(registry))


def test_successful_pdf_to_note_creation():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        pdf_path = root / "source.pdf"
        database_path = root / "notes.db"
        make_pdf(pdf_path, "workflow source content")
        engine = make_engine(database_path)

        with patch(
            "services.gemini_service.ask_gemini",
            return_value="Generated PDF summary",
        ) as ask_gemini:
            result = engine.run(
                build_pdf_to_note_workflow(),
                {"active_pdf": str(pdf_path)},
            )

        assert ask_gemini.called
        assert result["results"][0] == "Generated PDF summary"
        assert result["results"][1].startswith("Note ")
    print("Successful PDF-to-note creation passed.")


def test_missing_active_pdf():
    with TemporaryDirectory() as directory:
        engine = make_engine(Path(directory) / "notes.db")

        try:
            engine.run(build_pdf_to_note_workflow())
        except WorkflowStepError as error:
            assert error.step_index == 0
            assert "No PDF file was selected" in error.cause
        else:
            raise AssertionError("Expected WorkflowStepError")
    print("Missing active PDF passed.")


def test_invalid_pdf():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        invalid_path = root / "not-a-pdf.pdf"
        invalid_path.write_text("not a PDF")
        engine = make_engine(root / "notes.db")

        try:
            engine.run(
                build_pdf_to_note_workflow(),
                {"active_pdf": str(invalid_path)},
            )
        except WorkflowStepError as error:
            assert error.step_index == 0
            assert "Unable to read this PDF" in error.cause or "Unable to read" in error.cause
        else:
            raise AssertionError("Expected WorkflowStepError")
    print("Invalid PDF passed.")


def test_gemini_failure_stops_before_note_creation():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        pdf_path = root / "source.pdf"
        database_path = root / "notes.db"
        make_pdf(pdf_path, "workflow source content")
        engine = make_engine(database_path)

        with patch(
            "services.gemini_service.ask_gemini",
            side_effect=RuntimeError("Gemini unavailable"),
        ):
            try:
                engine.run(
                    build_pdf_to_note_workflow(),
                    {"active_pdf": str(pdf_path)},
                )
            except WorkflowStepError as error:
                assert error.step_index == 0
                assert "Gemini unavailable" in error.cause
            else:
                raise AssertionError("Expected WorkflowStepError")

        notes = Database(database_path)
        notes.initialize()
        with notes.session() as connection:
            assert connection.execute("SELECT COUNT(*) FROM notes").fetchone()[0] == 0
    print("Gemini failure handling passed.")


def test_note_persistence_contains_generated_content():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        pdf_path = root / "source.pdf"
        database_path = root / "notes.db"
        make_pdf(pdf_path, "workflow source content")
        engine = make_engine(database_path)

        with patch(
            "services.gemini_service.ask_gemini",
            return_value="Persisted generated summary",
        ):
            engine.run(
                build_pdf_to_note_workflow(),
                {"active_pdf": str(pdf_path)},
            )

        database = Database(database_path)
        database.initialize()
        with database.session() as connection:
            row = connection.execute(
                "SELECT content FROM notes ORDER BY id DESC LIMIT 1"
            ).fetchone()

        assert row is not None
        assert row["content"] == "Persisted generated summary"
    print("Note persistence passed.")


def main():
    test_successful_pdf_to_note_creation()
    test_missing_active_pdf()
    test_invalid_pdf()
    test_gemini_failure_stops_before_note_creation()
    test_note_persistence_contains_generated_content()
    print("\nAll PDF-to-note workflow tests passed.")


if __name__ == "__main__":
    main()
