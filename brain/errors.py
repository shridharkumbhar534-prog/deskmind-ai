class DeskMindError(Exception):
    """Base error with a technical message and a safe message for users."""

    def __init__(self, message: str, user_message: str):
        super().__init__(message)
        self.user_message = user_message


class InvalidRequestError(DeskMindError):
    def __init__(self):
        super().__init__(
            "A non-empty text message is required.",
            "Please enter a message before sending.",
        )


class CapabilityNotFoundError(DeskMindError):
    def __init__(self, intent: str):
        super().__init__(
            f"Capability '{intent}' is not registered.",
            "That feature is not available yet.",
        )


class AIConfigurationError(DeskMindError):
    def __init__(self):
        super().__init__(
            "Gemini API key is not configured.",
            "AI chat is not configured on this device.",
        )


class AIQuotaError(DeskMindError):
    def __init__(self):
        super().__init__(
            "Gemini request was rejected because the quota was exceeded.",
            "AI chat has reached its current usage limit. Please try again later.",
        )


class AIConnectionError(DeskMindError):
    def __init__(self):
        super().__init__(
            "Could not connect to the Gemini service.",
            "Unable to reach AI chat. Please check your internet connection and try again.",
        )


class AIServiceError(DeskMindError):
    def __init__(self):
        super().__init__(
            "Gemini service request failed.",
            "AI chat is temporarily unavailable. Please try again later.",
        )
