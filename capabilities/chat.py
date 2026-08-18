from brain.capability import Capability
from services.gemini_service import ask_gemini


class ChatCapability(Capability):

    def execute(self, request, context=None):

        if context and context.get("active_note"):
            note = context["active_note"]

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

        return ask_gemini(request)