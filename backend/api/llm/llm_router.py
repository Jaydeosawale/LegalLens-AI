"""
=========================================================
LegalLens AI
LLM Router
=========================================================
"""

from api.llm.llm import LLMService


class LLMRouter:
    """
    Central LLM Router.

    Future providers:
        • Groq
        • Gemini
        • OpenAI
        • Ollama
        • Claude
    """

    @staticmethod
    def get_llm(provider="groq"):

        provider = provider.lower()

        if provider == "groq":
            return LLMService.get_llm()

        # Future providers
        # if provider == "gemini":
        #     return GeminiService.get_llm()

        # if provider == "openai":
        #     return OpenAIService.get_llm()

        # if provider == "ollama":
        #     return OllamaService.get_llm()

        raise ValueError(
            f"Unsupported provider: {provider}"
        )