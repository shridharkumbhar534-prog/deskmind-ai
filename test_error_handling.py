"""Error handling checks that do not require external AI credentials."""

from brain.brain import Brain
from brain.errors import CapabilityNotFoundError, InvalidRequestError
from brain.registry import CapabilityRegistry


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

    print("Non-AI error handling checks passed.")
    print("SKIPPED: remote Gemini error mappings require an external API client.")


if __name__ == "__main__":
    main()
