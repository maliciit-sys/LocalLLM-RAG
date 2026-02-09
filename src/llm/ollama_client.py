"""
Ollama API client for interacting with the local LLM.
"""

import requests
import json
from src.utils.config import config


class OllamaClient:
    """Client for the Ollama API."""

    def __init__(self):
        self.base_url = config.ollama.host
        self.model = config.ollama.model

    def is_available(self) -> bool:
        """Check if Ollama is running and the model is loaded."""
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            models = [m["name"] for m in r.json().get("models", [])]
            return self.model in models
        except Exception:
            return False

    def get_models(self) -> list[str]:
        """List available models."""
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return [m["name"] for m in r.json().get("models", [])]
        except Exception:
            return []

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        """Generate a response (non-streaming)."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": 4096,
                "top_p": 0.9,
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120,
            )
            return response.json().get("response", "")
        except requests.exceptions.ConnectionError:
            return "❌ Error: Cannot connect to Ollama. Run: ollama serve"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def generate_stream(self, prompt: str, temperature: float = 0.3):
        """Generate a response with streaming (yields tokens)."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_ctx": 4096,
                "top_p": 0.9,
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=120,
            )
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    token = data.get("response", "")
                    if token:
                        yield token
                    if data.get("done", False):
                        break
        except requests.exceptions.ConnectionError:
            yield "❌ Error: Cannot connect to Ollama. Run: ollama serve"
        except Exception as e:
            yield f"❌ Error: {str(e)}"


# Singleton instance
_client = None


def get_ollama_client() -> OllamaClient:
    """Get or create the singleton OllamaClient."""
    global _client
    if _client is None:
        _client = OllamaClient()
    return _client
