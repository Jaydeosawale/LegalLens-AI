from langchain_groq import ChatGroq
from fastapi import HTTPException
from groq import APIStatusError, APITimeoutError

from config.settings import GROQ_API_KEY, MODEL_NAME
from api.services.system_settings_service import get_system_settings


def public_ai_error(error):
    if isinstance(error, APITimeoutError):
        return HTTPException(503, 'The AI service is taking too long. Please try again shortly.')
    if not isinstance(error, APIStatusError):
        return None
    if error.status_code == 413:
        return HTTPException(422, 'This request exceeds the AI text limit. Please ask a shorter question or select fewer documents.')
    if error.status_code == 429:
        return HTTPException(503, 'The AI service has reached its free usage limit. Please try again later.')
    return HTTPException(503, 'The AI service is temporarily unavailable. Please try again later.')


class LLMService:
    """
    Creates and returns the Groq LLM.
    """

    _llm = None
    _configuration = None

    @classmethod
    def get_llm(cls):
        """
        Returns a singleton ChatGroq instance.
        """

        settings = get_system_settings()
        configuration = (settings['model_name'], settings['temperature'])
        if cls._llm is None or cls._configuration != configuration:

            cls._llm = ChatGroq(
                groq_api_key=GROQ_API_KEY,
                model=settings['model_name'],
                temperature=settings['temperature'],
                max_tokens=1024,
                timeout=45,
                max_retries=1,
                streaming=True
            )
            cls._configuration = configuration

        return cls._llm
