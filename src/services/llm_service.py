from langchain_ollama import OllamaLLM
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL

def get_llm(temperature: float = 0.3) -> OllamaLLM:
    """Return a configured Ollama LLM instance."""
    return OllamaLLM(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=temperature,
    )

