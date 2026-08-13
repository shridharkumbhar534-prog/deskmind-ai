from brain.capability import Capability
from services.gemini_service import ask_gemini


class ChatCapability(Capability):

    def execute(self, request, context=None):
        return ask_gemini(request)