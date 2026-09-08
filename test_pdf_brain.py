"""AI-dependent PDF-to-Brain integration check.

Run this test only when a Gemini API key is configured.
"""

from pathlib import Path

from brain.context import ACTIVE_PDF
from brain.brain import Brain
from config.settings import GEMINI_API_KEY


if not GEMINI_API_KEY:
    print("SKIPPED: test_pdf_brain.py requires a configured Gemini API key.")
else:
    pdf_path = Path(__file__).parent / "capabilities" / "DeskMind_AI_Project_Status_and_Semester_Roadmap.pdf"
    result = Brain().process(
        "Summarize this PDF",
        {ACTIVE_PDF: str(pdf_path)},
    )
    print(result)
