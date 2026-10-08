from langchain_groq import ChatGroq

from config.settings import GROQ_API_KEY, MODEL_NAME
from api.services.system_settings_service import get_system_settings


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
                streaming=True
            )
            cls._configuration = configuration

        return cls._llm
