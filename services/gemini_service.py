import httpx
from google import genai
from google.genai.errors import ClientError, ServerError

from brain.errors import (
    AIConfigurationError,
    AIConnectionError,
    AIQuotaError,
    AIServiceError,
)
from config.settings import GEMINI_API_KEY


MODEL = "gemini-2.0-flash"

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def ask_gemini(prompt):
    if not GEMINI_API_KEY:
        raise AIConfigurationError()

    try:
        response = _get_client().models.generate_content(
            model=MODEL,
            contents=prompt,
        )

        return response.text

    except ClientError as error:
        if error.code == 429:
            raise AIQuotaError() from error

        raise AIServiceError() from error

    except httpx.RequestError as error:
        raise AIConnectionError() from error

    except ServerError as error:
        raise AIServiceError() from error
