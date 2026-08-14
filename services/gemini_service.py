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

def ask_gemini(prompt):
    if not GEMINI_API_KEY:
        raise AIConfigurationError()

    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt,
        )
    except ClientError as error:
        if error.code == 429:
            raise AIQuotaError() from error
        raise AIServiceError() from error
    except httpx.RequestError as error:
        raise AIConnectionError() from error
    except ServerError as error:
        raise AIServiceError() from error

    return response.text
