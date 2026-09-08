from pathlib import Path
from unittest.mock import patch

from brain.context import ACTIVE_PDF
from capabilities.pdf import PDFCapability


pdf_path = Path(__file__).parent / "capabilities" / "DeskMind_AI_Project_Status_and_Semester_Roadmap.pdf"

with patch("services.gemini_service.ask_gemini", return_value="mocked PDF answer") as ask_gemini:
    result = PDFCapability().execute(
        "Summarize this PDF",
        {ACTIVE_PDF: str(pdf_path)},
    )

assert result == "mocked PDF answer"
assert ask_gemini.called
print("PDF capability checks passed without external AI credentials.")
