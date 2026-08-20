from pathlib import Path

import pymupdf
from brain.capability import Capability


class PDFCapability(Capability):
    """Extract and process text from a locally selected PDF."""

    MAX_FILE_SIZE = 25 * 1024 * 1024
    MAX_PAGES = 100

    def execute(self, request, context=None):
        if not context or "pdf_path" not in context:
            raise ValueError("No PDF file was selected.")

        pdf_path = Path(context["pdf_path"])

        self._validate_pdf(pdf_path)

        text = self._extract_text(pdf_path)

        if not text.strip():
            return "The selected PDF does not contain readable text."

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

        return ask_gemini(prompt)

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