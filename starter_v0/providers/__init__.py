from providers.groq_provider import GroqProvider
from providers.openai_provider import OpenAIProvider
from providers.openrouter_provider import OpenRouterProvider
from providers.anthropic_provider import AnthropicProvider
from providers.gemini_provider import GeminiProvider
from providers.ollama_provider import OllamaProvider


PROVIDER_CHOICES = ["groq", "openrouter", "openai", "anthropic", "gemini", "ollama"]
DEFAULT_PROVIDER = "groq"


def make_provider(name: str):
    if name == "groq":
        return GroqProvider()
    if name == "openai":
        return OpenAIProvider()
    if name == "openrouter":
        return OpenRouterProvider()
    if name == "anthropic":
        return AnthropicProvider()
    if name == "gemini":
        return GeminiProvider()
    if name == "ollama":
        return OllamaProvider()
    raise ValueError(f"Unknown provider: {name}")
