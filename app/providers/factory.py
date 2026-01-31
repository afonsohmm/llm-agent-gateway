from .base import BaseProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider
from typing import Type

def get_provider(provider_name: str) -> Type[BaseProvider]:
    """
    Factory function to get a provider class based on its name.
    """
    provider_map = {
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "ollama": OllamaProvider,
    }
    provider_class = provider_map.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Provider '{provider_name}' not supported.")
    return provider_class()
