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


client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-3.6-flash"


def ask_gemini(prompt):
    if not GEMINI_API_KEY:
        raise AIConfigurationError()

    try:
        interaction = client.interactions.create(
            model=MODEL,
            input=prompt,
        )

        return interaction.output_text

    except ClientError as error:
        if error.code == 429:
            raise AIQuotaError() from error

        raise AIServiceError() from error

    except httpx.RequestError as error:
        raise AIConnectionError() from error

    except ServerError as error:
        raise AIServiceError() from error