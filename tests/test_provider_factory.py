import pytest
from app.providers.factory import get_provider
from app.providers.openai_provider import OpenAIProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.ollama_provider import OllamaProvider

def test_get_openai_provider():
    provider = get_provider("openai")
    assert isinstance(provider, OpenAIProvider)

def test_get_gemini_provider():
    provider = get_provider("gemini")
    assert isinstance(provider, GeminiProvider)

def test_get_ollama_provider():
    provider = get_provider("ollama")
    assert isinstance(provider, OllamaProvider)

def test_get_provider_case_insensitive():
    provider = get_provider("oPeNaI")
    assert isinstance(provider, OpenAIProvider)

def test_get_unknown_provider():
    with pytest.raises(ValueError):
        get_provider("unknown-provider")
