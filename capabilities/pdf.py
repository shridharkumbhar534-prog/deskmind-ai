from pathlib import Path

import pymupdf
from brain.capability import Capability
from brain.context import ACTIVE_PDF
from capabilities.file_search import FILE_SEARCH_RESULTS, FileSearchResult


PDF_RESULT = "pdf_result"


class PDFResult:
    """Structured Gemini output produced from an active PDF."""

    def __init__(self, source_path: Path, request: str, content: str):
        self.source_path = source_path.resolve()
        self.request = request
        self.content = content

    def __repr__(self):
        return f"PDFResult(source_path={str(self.source_path)!r})"


class PDFCapability(Capability):
    """Extract and process text from a locally selected PDF."""

    MAX_FILE_SIZE = 25 * 1024 * 1024
    MAX_PAGES = 100

    def execute(self, request, context=None):
        if not context:
            raise ValueError("No PDF file was selected.")

        pdf_path = self._resolve_pdf_path(context)

        self._validate_pdf(pdf_path)

        text = self._extract_text(pdf_path)

        if not text.strip():
            content = "The selected PDF does not contain readable text."
            context[PDF_RESULT] = PDFResult(pdf_path, request, content)
            return content

        prompt = f"""
The user has selected a PDF document.

User request:
{request}

PDF content:
{text}

Answer the user's request using the PDF content.
If the answer cannot be found in the document, say so clearly.
"""

        from services.gemini_service import ask_gemini

        content = ask_gemini(prompt)
        context[PDF_RESULT] = PDFResult(pdf_path, request, content)
        return content

    def _resolve_pdf_path(self, context) -> Path:
        if ACTIVE_PDF in context:
            return Path(context[ACTIVE_PDF]).resolve()

        search_result = context.get(FILE_SEARCH_RESULTS)
        if not isinstance(search_result, FileSearchResult):
            raise ValueError("No PDF file was selected.")

        if not search_result.matches:
            raise ValueError("File search found no PDF files.")

        if search_result.is_ambiguous:
            raise ValueError("File search found multiple matching files.")

        resolved_path = search_result.first_resolved_path()
        if resolved_path is None:
            raise ValueError("File search found no PDF files.")

        context[ACTIVE_PDF] = resolved_path
        return Path(resolved_path)

    def _validate_pdf(self, pdf_path: Path):

        if not pdf_path.exists():
            raise ValueError("The selected PDF does not exist.")

        if not pdf_path.is_file():
            raise ValueError("The selected PDF is not a valid file.")

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError("The selected file is not a PDF.")

        if pdf_path.stat().st_size > self.MAX_FILE_SIZE:
            raise ValueError("The PDF is too large to process.")

    def _extract_text(self, pdf_path: Path):

        try:
            document = pymupdf.open(pdf_path)

            if len(document) > self.MAX_PAGES:
                document.close()
                raise ValueError(
                    f"The PDF contains more than {self.MAX_PAGES} pages."
                )

            text = "\n".join(
                page.get_text()
                for page in document
            )

            document.close()

            return text

        except ValueError:
            raise

        except Exception as exc:
            raise ValueError(
                f"Unable to read the PDF: {exc}"
            ) from exc