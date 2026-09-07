from brain.capability import Capability
from brain.context import ACTIVE_NOTE, ACTIVE_PDF
from services.gemini_service import ask_gemini


class ChatCapability(Capability):

    def execute(self, request, context=None):
        if context and context.get(ACTIVE_NOTE):
            note = context[ACTIVE_NOTE]

            prompt = f"""
The user is asking about the note currently open in DeskMind AI.

Note title:
{note.get("title", "")}

Note content:
{note.get("content", "")}

User request:
{request}

Answer the user's request using the note content when relevant.
If the request is not about the note, answer normally.
"""
            return ask_gemini(prompt)

        if context and context.get(ACTIVE_PDF):
            pdf_path = context[ACTIVE_PDF]
            prompt = f"""
The user has a PDF document open at: {pdf_path}

User request:
{request}

If the user is asking about the PDF, let them know they can use the
PDF Assistant page for detailed questions about the document.
Otherwise, answer normally.
"""
            return ask_gemini(prompt)

        return ask_gemini(request)