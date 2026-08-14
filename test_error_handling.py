from unittest.mock import patch

import httpx
from google.genai.errors import ClientError

from brain.brain import Brain
from brain.errors import (
    AIConnectionError,
    AIQuotaError,
    CapabilityNotFoundError,
    InvalidRequestError,
)
from brain.registry import CapabilityRegistry
from services.gemini_service import ask_gemini


def main():
    try:
        Brain().process("   ")
    except InvalidRequestError as error:
        assert error.user_message == "Please enter a message before sending."
    else:
        raise AssertionError("Expected InvalidRequestError for an empty request")

    try:
        CapabilityRegistry().get("notes")
    except CapabilityNotFoundError as error:
        assert error.user_message == "That feature is not available yet."
    else:
        raise AssertionError("Expected CapabilityNotFoundError for an unknown capability")

    with patch(
        "services.gemini_service.client.models.generate_content",
        side_effect=ClientError(429, {}),
    ):
        try:
            ask_gemini("Hello")
        except AIQuotaError as error:
            assert "usage limit" in error.user_message
        else:
            raise AssertionError("Expected AIQuotaError for a 429 response")

    with patch(
        "services.gemini_service.client.models.generate_content",
        side_effect=httpx.ConnectError("offline"),
    ):
        try:
            ask_gemini("Hello")
        except AIConnectionError as error:
            assert "internet connection" in error.user_message
        else:
            raise AssertionError("Expected AIConnectionError for a connection failure")

    print("Error handling checks passed.")


if __name__ == "__main__":
    main()
